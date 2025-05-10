import sys
import os
import tracemalloc  # Import tracemalloc for memory usage tracking
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cdcl.algorithm_backbone import *
import time, csv, os, re
from statistics import mean


# Global start time for total execution time tracking
SCRIPT_START_TIME = time.perf_counter()

class SATSolver:
    """
    A class for solving SAT problems using the CDCL (Conflict-Driven Clause Learning) algorithm.

    Attributes:
        cdcl_solver (CDCLSolver): An instance of the CDCLSolver class used for solving SAT problems.
    """
    def parse_cnf_file(self, filename):
        clauses = []
        num_vars = 0
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('p cnf'):
                        # Parse problem line to get number of variables and clauses
                        parts = line.split()
                        if len(parts) >= 4:
                            n_vars = parts[2]
                            num_vars = int(n_vars)
                    elif not line.startswith('c') and line:
                        try:
                            # Parse clause (safely)
                            parts = line.split()
                            # Remove trailing 0 if present
                            if parts and parts[-1] == '0':
                                parts = parts[:-1]

                            # Convert to integers
                            clause = [int(x) for x in parts]
                            if clause:  # Only add non-empty clauses
                                clauses.append(clause)
                        except ValueError:
                            # Skip lines that can't be parsed as integers
                            continue
            return clauses, num_vars
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            raise
    def __init__(self):
        """
               Initializes the SATSolver with a CDCLSolver instance.
               """
        self.cdcl_solver = CDCLSolver()

    def parse_cnf_file(self, filename):
        """
        Parses a CNF file and extracts the clauses and number of variables.

        Args:
            filename (str): The path to the CNF file.

        Returns:
            tuple: A tuple containing a list of clauses (list of lists of integers) and the number of variables (int).

        Raises:
            Exception: If there is an error while parsing the file.
        """
        clauses = []
        num_vars = 0
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('p cnf'):
                        # Parse problem line to get number of variables and clauses
                        parts = line.split()
                        if len(parts) >= 4:
                            n_vars = parts[2]
                            num_vars = int(n_vars)
                    elif not line.startswith('c') and line:
                        try:
                            # Parse clause (safely)
                            parts = line.split()
                            # Remove trailing 0 if present
                            if parts and parts[-1] == '0':
                                parts = parts[:-1]

                            # Convert to integers
                            clause = [int(x) for x in parts]
                            if clause:  # Only add non-empty clauses
                                clauses.append(clause)
                        except ValueError:
                            # Skip lines that can't be parsed as integers
                            continue
            return clauses, num_vars
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            raise

    def solve(self, clauses, time_limit=30):
                """
        Solves a SAT problem using the CDCL algorithm with a time limit.

        Args:
            clauses (list): A list of clauses representing the SAT problem.
            time_limit (int): The maximum time allowed for solving (in seconds).

        Returns:
            bool: True if the problem is satisfiable (SAT), False if unsatisfiable (UNSAT).
        """
        # Set up variable tracking - find all variables in the problem
        all_vars = set()
        for clause in clauses:
            for lit in clause:
                all_vars.add(abs(lit))

        # Track the maximum variable for proper termination check
        max_var = max(all_vars) if all_vars else 0
        self.cdcl_solver.max_var = max_var
        
        # Initialize VSIDS activity scores
        self.cdcl_solver.initialize_activity()

        # Check for empty clause in the input - immediate UNSAT
        if any(len(clause) == 0 for clause in clauses):
            return False
            
        # Set up timers and progress counters
        start_time = time.perf_counter()
        progress_interval = 5  # Report progress every 5 seconds
        last_progress_time = start_time
        num_conflicts = 0
        num_decisions = 0
        num_restarts = 0
        num_clauses_learned = 0
        
        # Main CDCL loop with time limit for unsatisfiable problems
        while time.perf_counter() - start_time < time_limit:
            # Check if we should restart
            if self.cdcl_solver.should_restart():
                self.cdcl_solver.perform_restart()
                num_restarts += 1
            
            # Unit propagation with all clauses (original + learned)
            all_clauses = clauses + self.cdcl_solver.learned_clauses
            conflict = self.cdcl_solver.unit_propagate(all_clauses)

            # Progress reporting
            current_time = time.perf_counter()
            if current_time - last_progress_time > progress_interval:
                elapsed = current_time - start_time
                total_elapsed = current_time - SCRIPT_START_TIME
                print(f"\rSolving: {elapsed:.1f}s (total: {total_elapsed:.1f}s), {num_conflicts} conflicts, {num_decisions} decisions, " + 
                      f"{num_restarts} restarts, {len(self.cdcl_solver.learned_clauses)} learned clauses", end="")
                last_progress_time = current_time

            if conflict:
                num_conflicts += 1
                
                # Conflict at decision level 0 means UNSAT
                if self.cdcl_solver.decision_level == 0:
                    print("\nUNSAT proven by conflict at decision level 0")
                    return False

                # Analyze conflict and learn a new clause
                level, learned_clause = self.cdcl_solver.analyze_conflict(conflict, debug=False)

                # Backtrack and add the learned clause
                self.cdcl_solver.backtrack(level)
                self.cdcl_solver.learned_clauses.append(learned_clause)
                num_clauses_learned += 1
                
                # Add clause activity for the new learned clause
                self.cdcl_solver.clause_activity[len(self.cdcl_solver.learned_clauses) - 1] = 1.0

            else:
                # Check termination - ensure all clauses are satisfied
                if all(
                    any(
                        (lit > 0 and self.cdcl_solver.assignment.get(abs(lit), False)) or
                        (lit < 0 and not self.cdcl_solver.assignment.get(abs(lit), True))
                        for lit in clause
                    )
                    for clause in clauses
                ):
                    print("\nSAT: All clauses satisfied")
                    return True  # SAT - all clauses are satisfied

                # Make a new decision using VSIDS
                if not self.cdcl_solver.make_decision():
                    print("\nUNSAT: No valid decisions left")
                    return False  # UNSAT - no valid decisions left
                
                num_decisions += 1
        
        # If we reach the time limit, report timeout
        print("\nTimeout reached 30s per file")
        return False  # Assume UNSAT if timeout reached

    def solve_with_timing(self, clauses, repeat=10):
        """More accurate timing for very fast operations"""
        # For very fast operations, repeat multiple times for accuracy
        total_time = 0
        iterations = repeat
        
        for _ in range(iterations):
            # Reset solver state for each iteration
            self.cdcl_solver = CDCLSolver()

            # Measure with high precision
            start_time = time.perf_counter()
            result = self.solve(clauses)
            total_time += time.perf_counter() - start_time

        # Average time per solve
        avg_time = total_time / iterations
        return result, avg_time

    def solve_with_debug(self, clauses):
        """Solve with detailed debugging output for each step"""
        # Set up variable tracking - find all variables in the problem
        all_vars = set()
        for clause in clauses:
            for lit in clause:
                all_vars.add(abs(lit))

        # Track the maximum variable for proper termination check
        max_var = max(all_vars) if all_vars else 0
        self.cdcl_solver.max_var = max_var
        
        print(f"Problem has {len(clauses)} clauses and {max_var} variables")
        print("Initial clauses:")
        for i, clause in enumerate(clauses):
            print(f"  C{i}: {clause}")
        
        # Initialize VSIDS activity scores
        self.cdcl_solver.initialize_activity()
        print("Activity scores initialized")

        # Check for empty clause in the input - immediate UNSAT
        if any(len(clause) == 0 for clause in clauses):
            print("Empty clause found in input - UNSAT")
            return False

        step = 0
        # Main CDCL loop
        while True:
            step += 1
            print(f"\n===== STEP {step} =====")
            print(f"Current decision level: {self.cdcl_solver.decision_level}")
            print(f"Current assignment: {self.cdcl_solver.assignment}")
            print(f"Trail: {self.cdcl_solver.trail}")
            
            # Check if we should restart
            if self.cdcl_solver.should_restart():
                print(f"RESTARTING after {self.cdcl_solver.conflicts} conflicts")
                self.cdcl_solver.perform_restart()
                print(f"New restart threshold: {self.cdcl_solver.restart_threshold}")
            
            # Unit propagation with all clauses (original + learned)
            all_clauses = clauses + self.cdcl_solver.learned_clauses
            print(f"Performing unit propagation with {len(all_clauses)} clauses")
            
            trail_before = len(self.cdcl_solver.trail)
            conflict = self.cdcl_solver.unit_propagate(all_clauses)
            trail_after = len(self.cdcl_solver.trail)
            
            if trail_after > trail_before:
                print(f"Unit propagation assigned {trail_after - trail_before} new variables:")
                for i in range(trail_before, trail_after):
                    var = self.cdcl_solver.trail[i]
                    val = self.cdcl_solver.assignment[var]
                    reason = self.cdcl_solver.antecedent.get(var, "decision")
                    print(f"  {var} = {val} (reason: {reason})")

            if conflict:
                print(f"CONFLICT detected: {conflict}")
                # Conflict at decision level 0 means UNSAT
                if self.cdcl_solver.decision_level == 0:
                    print("Conflict at decision level 0 - UNSAT")
                    return False

                # Analyze conflict and learn a new clause
                print("Analyzing conflict...")
                level, learned_clause = self.cdcl_solver.analyze_conflict(conflict)
                print(f"Learned clause: {learned_clause}")
                print(f"Backtracking to level {level}")

                # Backtrack and add the learned clause
                self.cdcl_solver.backtrack(level)
                self.cdcl_solver.learned_clauses.append(learned_clause)
                
                # Add clause activity for the new learned clause
                self.cdcl_solver.clause_activity[len(self.cdcl_solver.learned_clauses) - 1] = 1.0
                print(f"Learned clauses count: {len(self.cdcl_solver.learned_clauses)}")

            else:
                # Check termination - ensure all clauses are satisfied
                all_satisfied = True
                for i, clause in enumerate(clauses):
                    is_sat = any(
                        (lit > 0 and self.cdcl_solver.assignment.get(abs(lit), False)) or
                        (lit < 0 and not self.cdcl_solver.assignment.get(abs(lit), True))
                        for lit in clause
                    )
                    if not is_sat:
                        print(f"Clause {i} not satisfied: {clause}")
                        all_satisfied = False
                        break
                
                if all_satisfied:
                    print("All clauses satisfied - SAT")
                    return True  # SAT - all clauses are satisfied

                # Make a new decision using VSIDS
                print("Making new decision using VSIDS")
                # Get variables with highest activity
                unassigned_vars = [v for v in range(1, max_var+1) if v not in self.cdcl_solver.assignment]
                if unassigned_vars:
                    activities = [(v, self.cdcl_solver.activity.get(v, 0.0)) for v in unassigned_vars]
                    activities.sort(key=lambda x: x[1], reverse=True)
                    print(f"Top variable activities: {activities[:3] if len(activities) >= 3 else activities}")
                
                if not self.cdcl_solver.make_decision():
                    print("No more decisions possible - UNSAT")
                    return False  # UNSAT - no valid decisions left
                
                print(f"Decided: {self.cdcl_solver.trail[-1]} = {self.cdcl_solver.assignment[self.cdcl_solver.trail[-1]]}")

    def solve_from_folder_(self, folder_path, output_csv="solving_results.csv"):
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(results_dir, exist_ok=True)  # Create the directory if it doesn't exist
        output_csv = os.path.join(results_dir, "solving_results.csv")  # Update the path for the CSV
        results = {}
        timing_data = {}
        clause_counts = {}  # Track clause counts for sorting

        print(f"Processing files from: {folder_path}")
        print("-" * 50)

        file_count = len([f for f in os.listdir(folder_path) if f.endswith('.cnf')])
        processed = 0
        skipped = 0

        for filename in os.listdir(folder_path):
            if filename.endswith('.cnf'):
                file_path = os.path.join(folder_path, filename)
                processed += 1
                
                # Show total elapsed time
                total_elapsed = time.perf_counter() - SCRIPT_START_TIME
                print(f"Processing [{processed}/{file_count}] (Total time: {total_elapsed:.1f}s): {filename}", end=" ")

                try:
                    self.cdcl_solver = CDCLSolver()
                    clauses, num_vars = self.parse_cnf_file(file_path)
                    print(f"({len(clauses)} clauses, {num_vars} vars)", end=" ")

                    # Start memory tracking
                    tracemalloc.start()

                    # Start timing the solving process
                    start_time = time.perf_counter()
                    is_sat, solve_time = self.solve_with_timing(clauses, repeat=1)  # Use repeat=1 for faster debugging
                    end_time = time.perf_counter()
                    solve_time = end_time - start_time  # Calculate the solving time

                    # Get current and peak memory usage
                    current, peak = tracemalloc.get_traced_memory()
                    memory_used = peak / (1024 * 1024)  # Convert to MB

                    # Stop memory tracking
                    tracemalloc.stop()

                    # Check if solving time exceeds 30 seconds
                    if solve_time > 30:
                        skipped += 1
                        print(f"Result: Skipped (exceeded 30s) in {solve_time:.4f}s, Memory used: {memory_used:.2f} MB")
                        continue  # Skip to the next file

                    # Get clause count from the filename (more reliable than just len(clauses))
                    match = re.search(r'uf(\d+)-\d+\.cnf', filename)  # Adjust regex as needed
                    clause_count = int(match.group(1)) if match else len(clauses)
                    clause_counts[filename] = clause_count

                    results[filename] = "SAT" if is_sat else "UNSAT"
                    timing_data[filename] = solve_time
                    print(f"Result: {results[filename]} in {solve_time:.4f}s, Memory used: {memory_used:.2f} MB")
                except Exception as e:
                    print(f"\nError processing {filename}: {str(e)}")  # Enhanced error message
                    results[filename] = f"Error: {str(e)}"
                    timing_data[filename] = 0
                    clause_counts[filename] = 0

        total_time = time.perf_counter() - SCRIPT_START_TIME
        print(f"\nCompleted processing in {total_time:.2f} seconds")
        print(f"Processed: {processed - skipped} files, Skipped: {skipped} files")
        print("-" * 50)

        if not results:
            print("No results to write to CSV")
            return {}, {}, {}

        # Sort filenames by clause count
        sorted_filenames = sorted(results.keys(), key=lambda f: clause_counts.get(f, 0))

        # Group by clause count
        grouped_results = {}
        for filename in sorted_filenames:
            count = clause_counts.get(filename, 0)
            if count not in grouped_results:
                grouped_results[count] = []
            grouped_results[count].append(filename)

        # Calculate overall statistics
        valid_times = [t for t in timing_data.values() if t > 0]
        stats = {
            'mean_time': mean(valid_times) if valid_times else 0,
            'max_time': max(valid_times) if valid_times else 0,
            'min_time': min(valid_times) if valid_times else 0,
            'total_time': total_time
        }

        print(f"Writing results to {output_csv}")
        # Export to CSV with results grouped by clause count
        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Filename', 'Clauses', 'Result', 'Solving Time (s)', 'Memory Used (MB)'])

            # Write results grouped by clause count
            for count in sorted(grouped_results.keys()):
                # Add group header
                writer.writerow([f"--- {count} Clauses ---", "", "", "", ""])

                # Add group results
                filenames = grouped_results[count]
                group_times = [timing_data[f] for f in filenames if timing_data[f] > 0]

                for filename in filenames:
                    writer.writerow([
                        filename,
                        count,
                        results[filename],
                        f"{timing_data[filename]:.6f}",
                        f"{memory_used:.2f}"  # Include memory used in the CSV
                    ])

                # Add group statistics if we have valid times
                if group_times:
                    writer.writerow(["", "", "", ""])
                    writer.writerow([f"Group Mean", count, f"{mean(group_times):.6f}"])
                    writer.writerow([f"Group Max", count, f"{max(group_times):.6f}"])
                    writer.writerow([f"Group Min", count, f"{min(group_times):.6f}"])

        return results, timing_data, stats

def main():
    script_start = time.perf_counter()
    
    solver = SATSolver()

    # Solve files from folder
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
    folder_path = os.path.join(script_dir, "test_cases")

    # Process all CNF files in the test_cases folder
    print("\nProcessing CNF files from folder:")
    print(f"Folder: {folder_path}")
    print("-" * 50)

    results, timing_data, stats = solver.solve_from_folder_(folder_path)

    print("\nSolving Results:")
    print("-" * 50)
    for filename, result in results.items():
        print(f"{filename}: {result}")

    total_time = time.perf_counter() - script_start
    print(f"\nTotal script execution time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
