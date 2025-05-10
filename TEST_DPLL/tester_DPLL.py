import os
import time
import csv
from dpll_method import dpll
from statistics import mean, median, stdev
from datetime import datetime
import tracemalloc

class CNFTester:
    """
    A class to test the DPLL (Davis-Putnam-Logemann-Loveland) algorithm on CNF files
    using various heuristics and record performance metrics.

    Attributes:
        results (list): A list to store the results of each test.
        timeout (int): The maximum time allowed for each test in seconds.
        heuristics (list): A list of heuristics available for testing.
    """
    def __init__(self):
        self.results = []
        self.timeout = 30  # seconds
        self.heuristics = ["moms", "vsids", "jw"]

    def parse_cnf_file(self, file_path):
        """Parse a CNF file and return the clauses and number of variables."""
        clauses = []
        num_vars = 0
        print(f"Parsing file: {file_path}")
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('p cnf'):
                    # Parse problem line to get number of variables
                    parts = line.split()
                    if len(parts) >= 4:
                        num_vars = int(parts[2])
                elif not line.startswith(('c', 'p', '%')):
                    literals = [int(x) for x in line.split() if x != '0']
                    if literals:
                        clauses.append(literals)
        return clauses, num_vars

    def run_test(self, file_path, heuristic, results_queue):  # results_queue parameter can be removed
        """Run a single test on a CNF file with specified heuristic."""
        try:
            # Parse the CNF file
            clauses, num_vars = self.parse_cnf_file(file_path)
            print(f"Problem has {num_vars} variables and {len(clauses)} clauses")

            # Start memory tracking
            tracemalloc.start()

            # Run the solver
            start_time = time.time()
            result, assignments = dpll(clauses, heuristic=heuristic)
            end_time = time.time()
            execution_time = end_time - start_time

            # Get current and peak memory usage
            current, peak = tracemalloc.get_traced_memory()
            memory_used = peak / (1024 * 1024)  # Convert to MB

            # Stop memory tracking
            tracemalloc.stop()

            # Store results directly in self.results
            result_data = {
                'file': os.path.basename(file_path),
                'heuristic': heuristic,
                'variables': num_vars,
                'clauses': len(clauses),
                'satisfiable': result,
                'time': execution_time,
                'memory_used_mb': memory_used,
                'assignments': assignments
            }
            self.results.append(result_data)

            # Print results
            print(f"Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}")
            print(f"Time taken: {execution_time:.4f} seconds")
            print(f"Memory used: {memory_used:.4f} MB")
            if result:
                print("Assignments:", assignments)
            print("-" * 50)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            self.results.append({
                'file': os.path.basename(file_path),
                'heuristic': heuristic,
                'error': str(e)
            })

    def run_benchmarks(self, test_cases_dir):

        """Run benchmarks on all CNF files in the directory."""
        # Print absolute path for debugging
        abs_path = os.path.abspath(test_cases_dir)
        print(f"Looking for test files in: {abs_path}")
        print(f"Current working directory: {os.getcwd()}")

        if not os.path.exists(test_cases_dir):
            print(f"Error: Directory '{test_cases_dir}' does not exist.")
            return
        # Get all CNF files
        cnf_files = [f for f in os.listdir(test_cases_dir) if f.endswith('.cnf')]
        cnf_files.sort()  # Sort for consistent order

        print(f"\nFound {len(cnf_files)} CNF files to test")
        print("=" * 50)

        # Ask user which heuristic to use
        print("\nAvailable heuristics:")
        for i, h in enumerate(self.heuristics, 1):
            print(f"{i}. {h.upper()}")
        print("4. All heuristics")

        choice = input("\nChoose a heuristic (1-4): ")
        try:
            choice = int(choice)
            if choice == 4:
                heuristics_to_use = self.heuristics
            elif 1 <= choice <= 3:
                heuristics_to_use = [self.heuristics[choice - 1]]
            else:
                print("Invalid choice. Using MOMS heuristic.")
                heuristics_to_use = ["moms"]
        except ValueError:
            print("Invalid input. Using MOMS heuristic.")
            heuristics_to_use = ["moms"]

        # Run tests sequentially
        for cnf_file in cnf_files:
            file_path = os.path.join(test_cases_dir, cnf_file)
            for heuristic in heuristics_to_use:
                print(f"\nTesting with {heuristic.upper()} heuristic:")
                self.run_test(file_path, heuristic, None)

        # Print summary
        self.print_summary()

        # Export to CSV
        self.export_to_csv()

    def export_to_csv(self):
        """Export results to CSV file with statistics."""
        # Create results directory if it doesn't exist
        results_dir = os.path.join('TEST_DPLL', 'results')
        os.makedirs(results_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = os.path.join(results_dir, f'dpll_results_{timestamp}.csv')

        # Write to CSV
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['filename', 'num_clauses', 'result', 'time_seconds', 'memory_used_mb', 'heuristic'])

            for result in self.results:
                if result['satisfiable'] is None:
                    # Handle unsatisfiable cases
                    writer.writerow([
                        result['file'], result['variables'], 'ERROR', 'ERROR', 'ERROR', result['heuristic']
                    ])
                else:
                    # Write result row
                    writer.writerow([
                        result['file'],
                        result['variables'],
                        'SAT' if result['satisfiable'] else 'UNSAT',
                        f"{result['time']:.6f}",  # Use 6 decimal places for seconds
                        f"{result['memory_used_mb']:.6f}",  # Use 6 decimal places for memory
                        result['heuristic']
                    ])

        # Calculate statistics for each heuristic
        heuristic_stats = {}
        for result in self.results:
            heuristic = result['heuristic']
            time_taken = result['time']
            memory_used = result['memory_used_mb']
            if heuristic not in heuristic_stats:
                heuristic_stats[heuristic] = {'times': [], 'memory': []}
            heuristic_stats[heuristic]['times'].append(time_taken)
            heuristic_stats[heuristic]['memory'].append(memory_used)

        # Write statistics for each heuristic at the end of the CSV
        with open(csv_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for heuristic, stats in heuristic_stats.items():
                times = stats['times']
                memory = stats['memory']
                if times:
                    avg_time = mean(times)
                    min_time = min(times)
                    max_time = max(times)
                    avg_memory = mean(memory) if memory else 0
                    writer.writerow(['', '', 'Average Time', f"{avg_time:.6f}", f"{avg_memory:.6f}", heuristic])
                    writer.writerow(['', '', 'Min Time', f"{min_time:.6f}", '', heuristic])
                    writer.writerow(['', '', 'Max Time', f"{max_time:.6f}", '', heuristic])

    
    def print_summary(self):
        """Print a summary of all test results."""
        print("\n=== Test Summary ===")
        
        # Group results by heuristic
        heuristic_results = {h: [] for h in self.heuristics}
        for result in self.results:
            if 'heuristic' in result:
                heuristic_results[result['heuristic']].append(result)

        # Print statistics for each heuristic
        for heuristic in self.heuristics:
            results = heuristic_results[heuristic]
            if not results:
                continue

            print(f"\n{heuristic.upper()} Heuristic:")
            print("-" * 50)
            
            # Calculate statistics
            sat_count = sum(1 for r in results if r.get('satisfiable', False))
            unsat_count = sum(1 for r in results if not r.get('satisfiable', True))
            error_count = sum(1 for r in results if 'error' in r)
            
            # Calculate timing statistics
            valid_times = [r['time'] for r in results if 'time' in r]
            if valid_times:
                avg_time = mean(valid_times)
                median_time = median(valid_times)
                std_time = stdev(valid_times) if len(valid_times) > 1 else 0
                max_time = max(valid_times)
                min_time = min(valid_times)
            else:
                avg_time = median_time = std_time = max_time = min_time = 0

            print(f"Total tests: {len(results)}")
            print(f"Satisfiable: {sat_count}")
            print(f"Unsatisfiable: {unsat_count}")
            print(f"Errors: {error_count}")
            print(f"\nTiming Statistics:")
            print(f"Average time: {avg_time:.4f} seconds")
            print(f"Median time: {median_time:.4f} seconds")
            print(f"Standard deviation: {std_time:.4f} seconds")
            print(f"Maximum time: {max_time:.4f} seconds")
            print(f"Minimum time: {min_time:.4f} seconds")

            # Print detailed results
            print("\nDetailed Results:")
            print("-" * 80)
            print(f"{'File':<30} {'Variables':<10} {'Clauses':<10} {'Result':<12} {'Time (s)':<10} {'Memory (MB)':<10}")
            print("-" * 80)
            for result in results:
                if 'error' in result:
                    print(f"{result['file']:<30} {'ERROR':<10} {'ERROR':<10} {'ERROR':<12} {'ERROR':<10} {'ERROR':<10}")
                else:
                    print(f"{result['file']:<30} {result['variables']:<10} {result['clauses']:<10} "
                          f"{'SAT' if result['satisfiable'] else 'UNSAT':<12} {result['time']:.4f} {result['memory_used_mb']:.4f}")


def main():
    # Initialize tester
    tester = CNFTester()

    # Get the absolute path to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the test files path
    test_cases_dir = os.path.join(script_dir, 'test_files')
    # Run benchmarks
    tester.run_benchmarks(test_cases_dir)

if __name__ == "__main__":
    main()
