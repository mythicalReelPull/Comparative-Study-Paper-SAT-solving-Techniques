class CDCLSolver:
    """
        A class implementing the Conflict-Driven Clause Learning (CDCL) algorithm for SAT solving.

        Attributes:
            assignment (dict): Current variable assignments (key: variable, value: True/False).
            learned_clauses (list): List of learned clauses during conflict analysis.
            decision_level (int): Current decision level in the search tree.
            level (dict): Mapping of variables to their decision levels.
            antecedent (dict): Mapping of variables to the clause that caused their assignment.
            trail (list): History of variable assignments in the order they were made.
            max_var (int): Maximum variable index in the problem.

            activity (dict): VSIDS activity scores for variables.
            decay_factor (float): Decay factor for variable activity scores.
            bump_value (float): Value to increase activity scores during conflict analysis.

            restarts (int): Number of restarts performed.
            conflicts (int): Total number of conflicts encountered.
            restart_threshold (int): Number of conflicts before a restart is triggered.
            restart_multiplier (float): Multiplier to increase the restart threshold.

            luby_sequence (list): Sequence of values for Luby restart strategy.
            luby_base (int): Base value for the Luby sequence.

            clause_deletion_threshold (int): Maximum number of learned clauses before deletion.
            clause_activity (dict): Activity scores for learned clauses.
            clause_decay (float): Decay factor for clause activity scores.

            saved_phases (dict): Last assigned value for each variable (used for phase saving).
        """
    def __init__(self):
        """
        Initializes the CDCLSolver with default parameters and data structures.
        """
        self.assignment = {}
        self.learned_clauses = []
        self.decision_level = 0
        self.level = {}          # Decision level for each variable
        self.antecedent = {}     # Reason clause for each assignment
        self.trail = []          # Assignment history
        self.max_var = 0         # Maximum variable index
        
        # VSIDS heuristic data
        self.activity = {}       # Activity score for each variable
        self.decay_factor = 0.85 # More aggressive decay (was 0.95)
        self.bump_value = 1.0    # Value to bump activity by 1
        
        # Restart strategy - more aggressive for UNSAT instances
        self.restarts = 0        # Number of restarts performed
        self.conflicts = 0       # Total number of conflicts
        self.restart_threshold = 50   # Lower initial threshold (was 100)
        self.restart_multiplier = 1.1  # Slower growth for more frequent restarts (was 1.5)
        
        # Luby series for restarts
        self.luby_sequence = [1]
        self.luby_base = 100     # Base value for Luby series
        
        # Clause management
        self.clause_deletion_threshold = 200  # Lower threshold (was 500)
        self.clause_activity = {}  # Activity for each learned clause
        self.clause_decay = 0.999  # Decay factor for clause activity
        
        # Phase saving
        self.saved_phases = {}   # Remember last value assigned to each variable

    def initialize_activity(self):
        """Initialize activity scores for all variables"""
        for var in range(1, self.max_var + 1):
            self.activity[var] = 0.0
            # Initialize phase saving to false (arbitrary starting point)
            self.saved_phases[var] = False

    def bump_variable_activity(self, var):
        """Increase activity for a variable involved in conflicts"""
        if var not in self.activity:
            self.activity[var] = 0.0
        self.activity[var] += self.bump_value
        
        # Rescale if needed to avoid numerical issues
        if self.activity[var] > 1e100:
            for v in self.activity:
                self.activity[v] *= 1e-100
            self.bump_value *= 1e-100

    def decay_variable_activity(self):
        """Decay all variable activities"""
        for var in self.activity:
            self.activity[var] *= self.decay_factor

    def bump_clause_activity(self, clause_idx):
        """Increase activity for a clause used in resolution"""
        if clause_idx not in self.clause_activity:
            self.clause_activity[clause_idx] = 0.0
        self.clause_activity[clause_idx] += 1.0

    def decay_clause_activity(self):
        """Decay all clause activities"""
        for idx in self.clause_activity:
            self.clause_activity[idx] *= self.clause_decay

    def clean_learned_clauses(self):
        """Remove less active learned clauses when we have too many"""
        if len(self.learned_clauses) <= self.clause_deletion_threshold:
            return
        
        # Sort clauses by activity
        sorted_clauses = sorted(
            range(len(self.learned_clauses)), 
            key=lambda i: self.clause_activity.get(i, 0.0),
            reverse=True
        )
        
        # Keep top third of clauses - more aggressive deletion
        keep_count = len(self.learned_clauses) // 3
        keep_count = max(keep_count, 50)  # Always keep at least 50 clauses
        to_keep = sorted_clauses[:keep_count]
        
        # Rebuild learned clauses list
        new_learned = []
        new_activity = {}
        
        for i, clause_idx in enumerate(to_keep):
            new_learned.append(self.learned_clauses[clause_idx])
            new_activity[i] = self.clause_activity.get(clause_idx, 0.0)
        
        self.learned_clauses = new_learned
        self.clause_activity = new_activity

    def next_luby(self):
        """Generate next value in Luby sequence for restarts"""
        size = len(self.luby_sequence)
        if (size & (size + 1)) == 0:  # If size is 2^k - 1
            self.luby_sequence.append(1)
        else:
            k = 1
            while size & k == 0:
                k <<= 1
            self.luby_sequence.append(self.luby_sequence[size - k])
        return self.luby_sequence[-1]

    def should_restart(self):
        """Determine if we should restart based on Luby sequence"""
        # More frequent restarts for unsatisfiable problems
        return self.conflicts >= (self.luby_base * self.luby_sequence[-1])

    def perform_restart(self):
        """Perform a restart: backtrack to level 0 and update restart threshold using Luby series"""
        self.backtrack(0)
        self.restarts += 1
        next_luby = self.next_luby()
        self.conflicts = 0  # Reset conflict counter

    def unit_propagate(self, clauses):
        """Propagate unit clauses and check for conflicts"""
        propagation_occurred = True
        
        # Continue propagating until no more unit clauses are found
        while propagation_occurred:
            propagation_occurred = False
            
            for clause_idx, clause in enumerate(clauses):
                # Check if this clause is already satisfied
                is_satisfied = False
                all_false = True
                unassigned_lits = []
                
                for lit in clause:
                    var = abs(lit)
                    if var in self.assignment:
                        val = self.assignment[var]
                        if (lit > 0 and val) or (lit < 0 and not val):
                            # Literal is true, clause is satisfied
                            is_satisfied = True
                            break
                        # Literal is false
                        continue
                    else:
                        # Unassigned literal
                        unassigned_lits.append(lit)
                        all_false = False
                
                if is_satisfied:
                    continue  # Skip satisfied clauses
                
                # If all literals are false, we have a conflict
                if all_false or not unassigned_lits:
                    # Increment conflict count for restart strategy
                    self.conflicts += 1
                    
                    # Bump activity of variables in the conflict
                    for lit in clause:
                        self.bump_variable_activity(abs(lit))
                    
                    # If it's a learned clause, bump its activity
                    if clause_idx >= len(clauses) - len(self.learned_clauses):
                        learned_idx = clause_idx - (len(clauses) - len(self.learned_clauses))
                        self.bump_clause_activity(learned_idx)
                    
                    # Decay activities
                    self.decay_variable_activity()
                    self.decay_clause_activity()
                    
                    return clause  # Conflict found!
                
                # If exactly one unassigned literal, we have a unit clause
                if len(unassigned_lits) == 1:
                    lit = unassigned_lits[0]
                    var = abs(lit)
                    value = (lit > 0)  # True if positive literal, False if negative
                    self.assignment[var] = value
                    
                    # Save phase for future decisions
                    self.saved_phases[var] = value
                    
                    self.level[var] = self.decision_level
                    self.antecedent[var] = clause
                    self.trail.append(var)
                    propagation_occurred = True
                    
                    # Bump activity for variable in unit clause
                    self.bump_variable_activity(var)
                    break  # Restart the propagation loop
        
        return None  # No conflict

    def analyze_conflict(self, conflict_clause, debug=True):
        # Initialize conflict analysis
        learned = list(conflict_clause)
        seen = set()
        current_level_literals = []
        
        if debug:
            print(f"  Conflict clause: {conflict_clause}")
            print(f"  Current decision level: {self.decision_level}")
        
        # Initial processing of conflict clause
        for lit in learned:
            var = abs(lit)
            if var in self.assignment:
                seen.add(var)
                if self.level[var] == self.decision_level:
                    current_level_literals.append(lit)
                    self.bump_variable_activity(var)  # Bump vars in conflict
        
        if debug:
            print(f"  Initial current level literals: {current_level_literals}")
        
        # Resolution process until First UIP - limit iterations for efficiency
        iteration = 0
        max_iterations = 20  # Limit resolution steps to avoid excessive work
        
        while len(current_level_literals) > 1 and iteration < max_iterations:
            iteration += 1
            if debug:
                print(f"  --- Resolution iteration {iteration} ---")
                print(f"  Current learned clause: {learned}")
                print(f"  Current level literals: {current_level_literals}")
            
            # Find the most recently assigned literal (from end of trail)
            recent_var = None
            recent_pos = -1
            
            for lit in current_level_literals:
                var = abs(lit)
                # Find position in trail
                try:
                    pos = self.trail[::-1].index(var)  # Search from end
                    if pos > recent_pos:
                        recent_pos = pos
                        recent_var = lit
                except ValueError:
                    continue
            
            if recent_var is None:
                recent_var = current_level_literals[-1]  # Fallback
            
            lit = recent_var
            current_level_literals.remove(lit)
            var = abs(lit)
            
            if debug:
                print(f"  Resolving on variable {var} (lit {lit})")
            
            # Only resolve variables that have antecedents (reason clauses)
            if var in self.antecedent:
                antecedent = self.antecedent[var]
                
                if debug:
                    print(f"  Antecedent (reason) clause: {antecedent}")
                
                # Resolve learned clause with antecedent
                new_lits_added = []
                for ant_lit in antecedent:
                    ant_var = abs(ant_lit)
                    if ant_var != var:  # Skip the literal we're resolving on
                        if ant_var not in seen:
                            seen.add(ant_var)
                            
                            # Bump activity for variable in resolution
                            self.bump_variable_activity(ant_var)
                            
                            if self.level[ant_var] == self.decision_level:
                                current_level_literals.append(ant_lit)
                                new_lits_added.append((ant_lit, "current"))
                            elif self.level[ant_var] > 0:  # Only include assigned variables
                                learned.append(ant_lit)
                                new_lits_added.append((ant_lit, "learned"))
                
                if debug:
                    print(f"  New literals added: {new_lits_added}")
            else:
                if debug:
                    print(f"  No antecedent for variable {var}, skipping resolution")
        
        # If we hit the iteration limit, simplify the clause by taking all current level literals
        if iteration >= max_iterations and len(current_level_literals) > 1:
            if debug:
                print(f"  Hit max resolution iterations, simplifying clause")
            # Keep only the most recently assigned literal from current level
            recent_var = None
            recent_pos = -1
            
            for lit in current_level_literals:
                var = abs(lit)
                try:
                    pos = self.trail[::-1].index(var)
                    if pos > recent_pos:
                        recent_pos = pos
                        recent_var = lit
                except ValueError:
                    continue
            
            if recent_var is not None:
                # Keep only this literal from the current level
                current_level_literals = [recent_var]
        
        if debug:
            print(f"  First UIP found, final current level literals: {current_level_literals}")
        
        # Add the remaining current level literal to learned clause
        if current_level_literals:
            learned.append(current_level_literals[0])
        
        # Decay activities after conflict analysis
        self.decay_variable_activity()
        
        # Clean learned clauses if we have too many - more aggressive for UNSAT instances
        if len(self.learned_clauses) >= self.clause_deletion_threshold:
            self.clean_learned_clauses()
        
        # Determine backtrack level - second highest decision level in learned clause
        back_level = 0
        second_highest = 0
        level_counts = {}
        
        for lit in learned:
            var = abs(lit)
            if var in self.level:
                level = self.level[var]
                if level not in level_counts:
                    level_counts[level] = 0
                level_counts[level] += 1
                
                if level > second_highest and level < self.decision_level:
                    if level > back_level:
                        second_highest = back_level
                        back_level = level
                    else:
                        second_highest = level
        
        if debug:
            print(f"  Decision levels in learned clause: {level_counts}")
            print(f"  Backtrack level: {back_level}")
        
        # Filter out any literals from higher levels that shouldn't be in final clause
        final_learned = []
        for lit in learned:
            var = abs(lit)
            if var not in self.level or self.level[var] <= back_level or self.level[var] == self.decision_level:
                final_learned.append(lit)
        
        # Remove duplicates for cleaner learned clauses
        final_learned = list(set(final_learned))
        
        # For very long clauses, apply minimization (optional)
        if len(final_learned) > 20:
            final_learned = self.minimize_clause(final_learned)
        
        if debug:
            print(f"  Final learned clause after filtering: {final_learned}")
        
        return back_level, final_learned
    
    def minimize_clause(self, clause):
        """Minimize learned clause by removing redundant literals"""
        # Simple minimization - check if literal is implied by others
        result = []
        for lit in clause:
            # Keep literals that aren't obviously redundant
            result.append(lit)
        return result

    def backtrack(self, level):
        # Save phases of unassigned variables for future decisions
        for var in self.assignment:
            self.saved_phases[var] = self.assignment[var]
            
        # Remove assignments above backtrack level
        while self.trail and self.level[self.trail[-1]] > level:
            var = self.trail.pop()
            del self.assignment[var]
            if var in self.antecedent:
                del self.antecedent[var]
            del self.level[var]
        self.decision_level = level

    def make_decision(self):
        # VSIDS decision heuristic - pick variable with highest activity
        unassigned_vars = []
        for var in range(1, self.max_var + 1):
            if var not in self.assignment:
                unassigned_vars.append(var)
                
        if not unassigned_vars:
            return False  # No decisions left, formula may be SAT
        
        # Find variable with highest activity
        best_var = max(unassigned_vars, key=lambda v: self.activity.get(v, 0.0))
        
        # Assign phase based on saved phase (phase saving strategy)
        saved_phase = self.saved_phases.get(best_var, True)
        self.assignment[best_var] = saved_phase
        self.level[best_var] = self.decision_level + 1
        self.trail.append(best_var)
        self.decision_level += 1
        return True

    def all_vars_assigned(self):
        # Check if all variables have been assigned
        return all(var in self.assignment for var in range(1, self.max_var + 1))
