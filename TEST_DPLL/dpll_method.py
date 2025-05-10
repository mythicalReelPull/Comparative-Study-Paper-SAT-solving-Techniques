from collections import Counter, defaultdict
import time
from multiprocessing import Process, Queue

class DPLLSolver:
    def __init__(self, heuristic="moms"):
        self.assignments = {}
        self.decisions = 0
        self.propagations = 0
        self.pure_eliminations = 0
        self.heuristic = heuristic
        self.vsids_scores = defaultdict(float)
        self.vsids_decay = 0.95

    def unit_propagation(self, clauses):
        """
        Rule I: Unit Propagation
        If {L} ∈ K' then:
        - Delete all clauses containing L
        - Delete L^c from remaining clauses
        """
        while True:
            # Find unit clauses
            unit_clauses = [c for c in clauses if len(c) == 1]
            if not unit_clauses:
                break

            # Process each unit clause
            for unit in unit_clauses:
                literal = unit[0]
                self.propagations += 1
                
                # Update assignments
                variable = abs(literal)
                value = literal > 0
                self.assignments[variable] = value
                
                # Update VSIDS scores if using VSIDS heuristic
                if self.heuristic == "vsids":
                    self.vsids_scores[variable] += 1
                
                # Remove satisfied clauses and update remaining clauses
                new_clauses = []
                for clause in clauses:
                    if literal in clause:
                        continue  # Clause is satisfied
                    new_clause = [l for l in clause if l != -literal]
                    if not new_clause:  # Empty clause means unsatisfiable
                        return None
                    new_clauses.append(new_clause)
                clauses = new_clauses

        return clauses

    def pure_literal_elimination(self, clauses):
        """
        Rule II: Pure Literal Elimination
        If K' contains a pure literal (appears only positively or only negatively),
        then delete all clauses containing the pure literal.
        Repeat until no more pure literals can be found.
        """
        while True:
            # Count literal occurrences
            literal_counts = Counter()
            for clause in clauses:
                for literal in clause:
                    literal_counts[literal] += 1

            # Find pure literals
            pure_literals = set()
            for literal, count in literal_counts.items():
                if -literal not in literal_counts:
                    pure_literals.add(literal)

            # If no pure literals found, we're done
            if not pure_literals:
                break

            # Remove clauses containing pure literals
            new_clauses = []
            for clause in clauses:
                if not any(lit in pure_literals for lit in clause):
                    new_clauses.append(clause)
                else:
                    # Update assignments for pure literals
                    for lit in clause:
                        if lit in pure_literals:
                            variable = abs(lit)
                            value = lit > 0
                            self.assignments[variable] = value
                            self.pure_eliminations += 1

            # If no clauses were removed, we're done
            if len(new_clauses) == len(clauses):
                break

            clauses = new_clauses

        return clauses

    def remove_redundant_clauses(self, clauses):
        """Remove tautological and redundant clauses."""
        new_clauses = []
        seen_clauses = set()

        for clause in clauses:
            # Check for tautology
            if any(-lit in clause for lit in clause):
                continue  # Skip tautological clause
            
            # Convert clause to a frozenset for easy comparison
            clause_set = frozenset(clause)
            if clause_set not in seen_clauses:
                seen_clauses.add(clause_set)
                new_clauses.append(clause)

        return new_clauses

    def choose_literal(self, clauses):
        """
        Choose a literal for splitting (Rule III)
        Using the selected heuristic
        """
        if self.heuristic == "moms":
            return self._choose_literal_moms(clauses)
        elif self.heuristic == "vsids":
            return self._choose_literal_vsids(clauses)
        elif self.heuristic == "jw":
            return self._choose_literal_jw(clauses)
        else:
            return self._choose_literal_moms(clauses)  # Default to MOMS

    def _choose_literal_moms(self, clauses):
        """
        MOMS heuristic: Choose variable that appears most often in smallest clauses
        """
        if not clauses:
            return None

        # Find minimum clause size
        min_size = min(len(c) for c in clauses)
        smallest_clauses = [c for c in clauses if len(c) == min_size]

        # Count occurrences in smallest clauses
        literal_counts = Counter()
        for clause in smallest_clauses:
            for literal in clause:
                literal_counts[abs(literal)] += 1

        return max(literal_counts.items(), key=lambda x: x[1])[0]

    def _choose_literal_vsids(self, clauses):
        """
        VSIDS heuristic: Choose variable with highest activity score
        """
        # Decay all scores
        for var in self.vsids_scores:
            self.vsids_scores[var] *= self.vsids_decay

        # Get all variables in current clauses
        variables = {abs(lit) for clause in clauses for lit in clause}
        
        # Return variable with highest score
        return max(variables, key=lambda v: self.vsids_scores[v])

    def _choose_literal_jw(self, clauses):
        """
        Jeroslow-Wang heuristic: Choose variable with highest weight
        """
        literal_weights = Counter()
        for clause in clauses:
            weight = 2 ** -len(clause)  # Weight is 2^(-|clause|)
            for literal in clause:
                literal_weights[abs(literal)] += weight
        return max(literal_weights.items(), key=lambda x: x[1])[0]

    def update_vsids_scores(self, conflict_vars):
        """Increase scores for variables involved in a conflict."""
        for var in conflict_vars:
            self.vsids_scores[abs(var)] += 5  # Increase score significantly

    def reset_vsids_scores(self):
        """Reset VSIDS scores periodically."""
        if self.decisions % 1000 == 0:  # Reset every 1000 decisions
            self.vsids_scores.clear()  # Clear scores

    def solve(self, clauses):
        """
        Main DPLL algorithm
        Returns (satisfiable, assignments)
        """
        # Rule I: Unit Propagation
        clauses = self.unit_propagation(clauses)
        if clauses is None:
            return False, {}

        # Rule II: Pure Literal Elimination
        clauses = self.pure_literal_elimination(clauses)
        if not clauses:
            return True, self.assignments

        # Rule III: Remove Redundant Clauses
        clauses = self.remove_redundant_clauses(clauses)

        # Rule IV: Split
        if clauses:
            self.decisions += 1
            literal = self.choose_literal(clauses)
            
            # Try assigning True
            new_clauses = clauses + [[literal]]
            result, new_assignments = self.solve(new_clauses)
            if result:
                self.assignments.update(new_assignments)
                return True, self.assignments

            # Try assigning False
            new_clauses = clauses + [[-literal]]
            result, new_assignments = self.solve(new_clauses)
            if result:
                self.assignments.update(new_assignments)
                return True, self.assignments

            return False, {}

        return True, self.assignments

def dpll(clauses, assignments=None, heuristic="moms"):
    """
    Wrapper function to maintain compatibility with existing code
    """
    solver = DPLLSolver(heuristic=heuristic)
    if assignments:
        solver.assignments = assignments.copy()
    return solver.solve(clauses)

def solve_subproblem(clauses, results_queue):
    # Create a DPLLSolver instance and solve the subproblem
    solver = DPLLSolver()
    result = solver.solve(clauses)
    results_queue.put(result)

# In your main solving function
if __name__ == "__main__":
    results_queue = Queue()
    processes = []

    for decision in decisions:
        p = Process(target=solve_subproblem, args=(new_clauses, results_queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Collect results
    while not results_queue.empty():
        result = results_queue.get()
        # Process the result
