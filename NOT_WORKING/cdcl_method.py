# cdcl_method.py
import random

class VSIDS_CDCL:
    """
        A class implementing the Conflict-Driven Clause Learning (CDCL) algorithm with
        Variable State Independent Decaying Sum (VSIDS) heuristic for SAT solving.

        Attributes:
            clauses (list): The list of clauses representing the CNF formula.
            assignment (set): The current set of assigned literals.
            levels (dict): A mapping of literals to their decision levels.
            current_level (int): The current decision level.
            decision_stack (list): A stack of decision literals.
            scores (dict): The VSIDS scores for each variable.
            decay_factor (float): The factor by which VSIDS scores decay.
            decay_interval (int): The number of conflicts after which scores decay.
            conflict_count (int): The number of conflicts encountered.
        Methods:
            unit_propagate(): Performs unit propagation on the clauses.
            analyze_conflict(): Analyzes a conflict and learns a new clause.
            decay_scores(): Decays the VSIDS scores periodically.
            backjump_to(level): Backjumps to a specific decision level.
            choose_literal(): Chooses the next literal to assign based on VSIDS scores.
            solve(): Main solving loop for the CDCL algorithm.
    """
    def __init__(self, clauses, decay_factor=0.95, decay_interval=100):
        # Deep copy clauses
        self.clauses = [list(c) for c in clauses]
        # Assignment and decision levels
        self.assignment = set()
        self.levels = {}  # literal -> decision level
        self.current_level = 0
        # Decision stack of decision literals
        self.decision_stack = []
        # VSIDS scores
        self.scores = {}
        self.decay_factor = decay_factor
        self.decay_interval = decay_interval
        self.conflict_count = 0
        # Initialize scores
        self._init_scores()

    def _init_scores(self):
        """
        Initializes the VSIDS_CDCL solver.

        Args:
            clauses (list): The list of clauses in CNF format.
            decay_factor (float): The decay factor for VSIDS scores.
            decay_interval (int): The interval for decaying VSIDS scores.
        """
        for clause in self.clauses:
            for lit in clause:
                var = abs(lit)
                self.scores.setdefault(var, 0.0)

    def unit_propagate(self):
        """
              Performs unit propagation to assign literals that must be true
              to satisfy the formula. Continues until no more unit clauses exist.
        """
        while True:
            unit = None
            for clause in self.clauses:
                # skip satisfied clauses
                if any(l in self.assignment for l in clause):
                    continue
                # collect unassigned literals
                unassigned = [l for l in clause if -l not in self.assignment and l not in self.assignment]
                if len(unassigned) == 1:
                    unit = unassigned[0]
                    break
            if unit is None:
                break
            # assign unit at current level
            self.assignment.add(unit)
            self.levels[unit] = self.current_level
        return

    def analyze_conflict(self):
        """
        Analyzes a conflict and generates a learned clause.

        Returns:
            list: The learned clause to be added to the formula.
        """
        # pick any falsified clause and bump scores
        for clause in self.clauses:
            if all(-l in self.assignment for l in clause):
                for lit in clause:
                    self.scores[abs(lit)] += 1.0
                # learn negation of the first literal
                learned = [-clause[0]]
                return learned
        return []

    def decay_scores(self):
        """
        Decays the VSIDS scores for all variables by the decay factor.
        """
        for var in self.scores:
            self.scores[var] *= self.decay_factor

    def backjump_to(self, level):
        """
        Backjumps to a specified decision level, removing assignments
        and decisions made at higher levels.

        Args:
            level (int): The decision level to backjump to.
        """
        # Remove assignments above target level
        to_remove = [lit for lit, lvl in self.levels.items() if lvl > level]
        for lit in to_remove:
            self.assignment.remove(lit)
            del self.levels[lit]
        # Prune decision stack
        while self.decision_stack and self.levels.get(self.decision_stack[-1], 0) > level:
            self.decision_stack.pop()
        self.current_level = level

    def choose_literal(self):
        """
        Chooses the next literal to assign based on VSIDS scores.

        Returns:
            int: The chosen literal, or None if no unassigned variables remain.
        """
        # unassigned variables
        unassigned = [v for v in self.scores if v not in self.assignment and -v not in self.assignment]
        if not unassigned:
            return None
        max_score = max(self.scores[v] for v in unassigned)
        best = [v for v in unassigned if self.scores[v] == max_score]
        return random.choice(best)

    def solve(self):
        """
        Solves the SAT problem using the CDCL algorithm.

        Returns:
            str: "sat" if the formula is satisfiable, "unsat" otherwise.
        """
        num_vars = max(self.scores) if self.scores else 0
        while True:
            # 1) Unit propagation
            self.unit_propagate()

            # 2) Conflict check
            conflict = any(all(-l in self.assignment for l in clause) for clause in self.clauses)
            if conflict:
                self.conflict_count += 1
                # conflict at root level -> UNSAT
                if not self.decision_stack:
                    return "unsat"
                # analyze and learn clause
                learned = self.analyze_conflict()
                if learned:
                    self.clauses.append(learned)
                # decay scores periodically
                if self.conflict_count % self.decay_interval == 0:
                    self.decay_scores()
                # backjump to root (for single-literal learnt clause)
                self.backjump_to(0)
                # assert learned unit at level 0
                continue

            # 3) Check if complete
            if all((v in self.assignment) or (-v in self.assignment) for v in range(1, num_vars+1)):
                return "sat"

            # 4) Decision
            var = self.choose_literal()
            if var is None:
                return "unsat"
            self.current_level += 1
            self.decision_stack.append(var)
            self.assignment.add(var)
            self.levels[var] = self.current_level
