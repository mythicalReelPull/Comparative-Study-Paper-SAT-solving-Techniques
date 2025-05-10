import os
import time
import csv
import datetime
from dp_method import DavisPutnam  # Ensure this import matches your file structure
import re
from statistics import mean
from datetime import datetime
import tracemalloc  # Import tracemalloc for memory usage tracking

INT_RE = re.compile(r'[-+]?\d+')

def read_dimacs_file(path):
        """
    Parses a DIMACS CNF file into a list of clauses.

    Args:
        path (str): The path to the DIMACS CNF file.

    Returns:
        list: A list of clauses, where each clause is a list of integers.
    """
    clauses = []
    with open(path, 'r', encoding='ascii', errors='ignore') as f:
        for idx, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith(('c', 'p')):
                continue

            # Strip inline comments
            for delim in ('%', ';', '*'):
                if delim in line:
                    line = line.split(delim, 1)[0].strip()

            # Extract integers
            nums = list(map(int, INT_RE.findall(line)))
            if not nums:
                continue

            # Check for clause terminator
            if nums[-1] != 0:
                print(f"[Line {idx}] warning: clause doesn't end in 0: {nums}")
                continue

            clause = nums[:-1]
            clauses.append(clause)  # Add clause (empty or non-empty)

    print(f"Parsed {len(clauses)} clauses")
    return clauses


def test_davis_putnam_on_folder(folder_path, csv_path, heuristics):
    """
    Tests the Davis-Putnam algorithm on all DIMACS CNF files in a folder and writes results to a CSV file.

    Args:
        folder_path (str): The path to the folder containing DIMACS CNF files.
        csv_path (str): The path to the output CSV file.
        heuristics (list): A list of heuristics to use for testing.
    """
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Header row
        writer.writerow(['filename', 'num_clauses', 'result', 'time_seconds', 'memory_used_mb', 'heuristic'])

        # Store times and memory for each heuristic
        heuristic_times = {h: [] for h in heuristics}
        heuristic_memory = {h: [] for h in heuristics}  # New dictionary for memory usage

        # Test each file
        for filename in sorted(os.listdir(folder_path)):
            if not filename.endswith('.cnf'):
                continue
            file_path = os.path.join(folder_path, filename)
            print(f"Testing {filename}…")

            clauses = read_dimacs_file(file_path)

            for heuristic in heuristics:
                print(f"  Using heuristic: {heuristic}")
                dp_solver = DavisPutnam(clauses, heuristic=heuristic)

                # Start memory tracking
                tracemalloc.start()

                start = time.perf_counter()
                result = dp_solver.solve()
                elapsed = time.perf_counter() - start

                # Get current and peak memory usage
                current, peak = tracemalloc.get_traced_memory()
                memory_used = peak / (1024 * 1024)  # Convert to MB

                # Stop memory tracking
                tracemalloc.stop()

                # Write a row: file, clause count, result, time, memory, heuristic
                writer.writerow([filename, len(clauses), result, f"{elapsed:.6f}", f"{memory_used:.6f}", heuristic])
                print(f"  → {result} in {elapsed:.6f}s ({len(clauses)} clauses, heuristic={heuristic}, memory={memory_used:.2f} MB)")

                # Store the elapsed time and memory for the chosen heuristic
                heuristic_times[heuristic].append(elapsed)
                heuristic_memory[heuristic].append(memory_used)

        # Write statistics for each heuristic
        for heuristic in heuristics:
            if heuristic_times[heuristic]:
                avg_time = mean(heuristic_times[heuristic])
                min_time = min(heuristic_times[heuristic])
                max_time = max(heuristic_times[heuristic])
                avg_memory = mean(heuristic_memory[heuristic]) if heuristic_memory[heuristic] else 0
                writer.writerow(['', '', 'Average Time', f"{avg_time:.6f}", f"{avg_memory:.6f}", heuristic])
                writer.writerow(['', '', 'Min Time', f"{min_time:.6f}", '', heuristic])
                writer.writerow(['', '', 'Max Time', f"{max_time:.6f}", '', heuristic])


if __name__ == "__main__":
    """
    Main entry point for the script. Prompts the user to select a heuristic, tests the Davis-Putnam algorithm
    on all DIMACS CNF files in a specified folder, and saves the results to a CSV file.
    """
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = r"C:\Users\MrWoo\OneDrive\Faculty\SAT_SOLVING\TEST_DP\test_files"
    output_csv = os.path.join(r"C:\Users\MrWoo\OneDrive\Faculty\SAT_SOLVING\TEST_DP\results",
                              f"performance_{current_time}.csv")

    # Prompt user for heuristic choice
    print("Available heuristics:")
    print("1. Jeroslow-Wang (jw)")
    print("2. MOM's (moms)")
    print("3. VSIDS (vsids)")
    print("4. All heuristics (all)")

    choice = input("Select a heuristic (1-4): ").strip().lower()

    if choice == '1':
        heuristics = ["jeroslow_wang"]
    elif choice == '2':
        heuristics = ["moms"]
    elif choice == '3':
        heuristics = ["vsids"]
    elif choice == '4':
        heuristics = ["jeroslow_wang", "moms", "vsids"]
    else:
        print("Invalid choice. Defaulting to Most Occurrences.")
        heuristics = ["moms"]

    test_davis_putnam_on_folder(folder_path, output_csv, heuristics)
    print(f"\nAll done! Results saved to {output_csv}")