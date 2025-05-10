from collections import defaultdict, Counter
import math

class DavisPutnam:
    """
    A class implementing the Davis-Putnam algorithm for solving SAT problems.
    Includes support for various heuristics such as Jeroslow-Wang, MOMs, and VSIDS.

    Attributes:
        K (list): The list of clauses representing the CNF formula.
        heuristic (str): The heuristic to use for literal selection.
        literal_scores (defaultdict): A dictionary to store VSIDS scores for literals.
    """
    def jeroslow_wang(self, clauses):
        """
                Implements the Jeroslow-Wang heuristic for literal selection.

                Args:
                    clauses (list): The list of clauses in the CNF formula.

                Returns:
                    int: The literal with the highest Jeroslow-Wang score, or None if no literals are found.
                """
        scores = defaultdict(float)
        for clause in clauses:
            w = 2 ** -len(clause)
            for lit in clause:
                scores[lit] += w
        return max(scores, key=scores.get, default=None)

    def moms_heuristic(self, clauses, m=1):
        """
              Implements the MOMs (Maximum Occurrences in clauses of Minimum Size) heuristic.

              Args:
                  clauses (list): The list of clauses in the CNF formula.
                  m (int): A parameter to adjust the scoring function.

              Returns:
                  int: The literal with the highest MOMs score, or None if no literals are found.
              """
        # find size of smallest non-empty clause
        min_len = min((len(c) for c in clauses if c), default=0)
        # count occurrences in those min-length clauses
        counts = Counter(lit for c in clauses if len(c)==min_len for lit in c)
        best = None
        best_score = -1
        for lit, cnt in counts.items():
            # MOM score = (cnt_pos+cnt_neg)*2^m + cnt_pos*cnt_neg
            var = abs(lit)
            cnt_pos = counts.get(var, 0)
            cnt_neg = counts.get(-var, 0)
            score = (cnt_pos + cnt_neg)*(2**m) + cnt_pos*cnt_neg
            if score > best_score:
                best_score, best = score, lit
        return best

    def vsids_heuristic(self, literal_scores):
        """
             Implements the VSIDS (Variable State Independent Decaying Sum) heuristic.

             Args:
                 literal_scores (defaultdict): A dictionary of VSIDS scores for literals.

             Returns:
                 int: The literal with the highest VSIDS score, or None if no literals are found.
             """
        return max(literal_scores, key=literal_scores.get, default=None)

    def __init__(self, clauses, heuristic="jeroslow_wang"):
        """
        Initializes the Davis-Putnam solver.

        Args:
            clauses (list): The list of clauses in the CNF formula.
            heuristic (str): The heuristic to use for literal selection. Defaults to "jeroslow_wang".
        """
        # clauses as lists of ints
        self.K = [list(c) for c in clauses]
        self.heuristic = heuristic
        self.literal_scores = defaultdict(int)

    def choose_literal(self):
        """
        Chooses a literal for branching based on the selected heuristic.

        Returns:
            int: The chosen literal, or raises a ValueError if the heuristic is unknown.
        """
        if self.heuristic == "jeroslow_wang":
            return self.jeroslow_wang(self.K)
        if self.heuristic == "moms":
            return self.moms_heuristic(self.K)
        if self.heuristic == "vsids":
            return self.vsids_heuristic(self.literal_scores)
        raise ValueError(f"Unknown heuristic {self.heuristic}")

    def simplify(self, clauses, lit):
                """
        Simplifies the formula by removing clauses containing the given literal
        and removing the negation of the literal from other clauses.

        Args:
            clauses (list): The list of clauses in the CNF formula.
            lit (int): The literal to simplify with.

        Returns:
            list: The simplified list of clauses.
        """
        new = []
        for c in clauses:
            if lit in c:
                continue
            filtered = [x for x in c if x != -lit]
            new.append(filtered)
        return new

    def unit_propagate(self, clauses):
                """
        Performs unit propagation to simplify the formula and assign literals.

        Args:
            clauses (list): The list of clauses in the CNF formula.

        Returns:
            tuple: A tuple containing the simplified clauses and the set of assigned literals.
        """
        assignment = set()
        while True:
            # find any unit clause
            units = [c[0] for c in clauses if len(c)==1]
            if not units:
                break
            for lit in units:
                assignment.add(lit)
                # VSIDS bump
                self.literal_scores[lit] += 1
                clauses = self.simplify(clauses, lit)
        return clauses, assignment

    def pure_literal_elim(self, clauses):
                """
        Eliminates pure literals from the formula.

        Args:
            clauses (list): The list of clauses in the CNF formula.

        Returns:
            tuple: A tuple containing the simplified clauses and the set of assigned literals.
        """
        counts = Counter(l for c in clauses for l in c)
        assignment = set()
        for lit, cnt in counts.items():
            if cnt>0 and counts.get(-lit,0)==0:
                assignment.add(lit)
                clauses = self.simplify(clauses, lit)
        return clauses, assignment

    def solve_recursive(self, clauses, assignment):
        """
        Recursively solves the SAT problem using the Davis-Putnam algorithm.

        Args:
            clauses (list): The list of clauses in the CNF formula.
            assignment (set): The current set of assigned literals.

        Returns:
            bool: True if the formula is satisfiable, False otherwise.
        """
        # 1) Unit propagation
        clauses, up_assn = self.unit_propagate(clauses)
        assignment |= up_assn

        # 2) Check for empty clause ⇒ UNSAT
        if any(len(c)==0 for c in clauses):
            return False

        # 3) Pure-literal elimination
        clauses, pl_assn = self.pure_literal_elim(clauses)
        assignment |= pl_assn

        # 4) If no clauses left ⇒ SAT
        if not clauses:
            return True

        # 5) Choose a branching literal
        lit = self.choose_literal()
        if lit is None:
            # no literal chosen but clauses remain: unsatisfiable
            return False

        # 6) Branch on lit = True, then lit = False
        for trial in (lit, -lit):
            new_clauses = self.simplify(clauses, trial)
            if self.solve_recursive(new_clauses, assignment | {trial}):
                return True

        return False

    def solve(self):
        """
        Solves the SAT problem using the Davis-Putnam algorithm.

        Returns:
            str: "satisfiable" if the formula is satisfiable, "unsatisfiable" otherwise.
        """
        sat = self.solve_recursive(self.K, set())
        return "satisfiable" if sat else "unsatisfiable"


# Example:
if __name__ == "__main__":
    K = [[1, -2], [-1, 2], [2, 3], [-3]]
    for h in ("jeroslow_wang","moms","vsids"):
        dp = DavisPutnam(K, heuristic=h)
        print(h, dp.solve())
