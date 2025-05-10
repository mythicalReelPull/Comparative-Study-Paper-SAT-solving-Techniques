import sys
import os
import time  # Import the time module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from resolution_algorithm import resolution_solver


def solve_file(file_path):
    """
    Reads a DIMACS CNF file, parses it, and solves it using the custom solver.

    Args:
        file_path (str): Path to the DIMACS file.

    Returns:
        str: 'SATISFIABLE' if the problem is satisfiable, 'UNSATISFIABLE' otherwise.
    """
    clauses = []
    print(f"Reading file: {file_path}")
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('c') or line.startswith('%') or line.startswith('0'):
                continue  # Skip comments and end-of-file markers
            if line.startswith('p'):
                print(f"Problem line: {line.strip()}")  # Debug output for the problem line
                continue

            clause = list(map(int, line.strip().split()))
            clause.pop()  # Remove the trailing 0
            clauses.append(clause)

    print(f"Parsed clauses: {clauses}") 
    print("Starting resolution solver...")  
    try:
        start_time = time.time()  # Start timing
        result = resolution_solver(clauses)
        end_time = time.time()  # End timing
        duration = end_time - start_time  # Calculate duration
        print(f"Solver result: {result}")  
        print("Resolution solver completed successfully")  
        print(f"Time taken to solve: {duration:.2f} seconds")  # Print duration
        return 'SATISFIABLE' if result == "SATISFIABLE" else 'UNSATISFIABLE'
    except Exception as e:
        print(f"Error in resolution solver: {e}") 
        raise 


if __name__ == "__main__":
    test_folder = os.path.join("PigeonHole_Problem", "test_cases")
    if not os.path.exists(test_folder):
        print(f"Test folder '{test_folder}' does not exist.")
    else:
        print(f"Looking for .cnf files in folder: {test_folder}")
        all_results = []  
        for test_file in os.listdir(test_folder):
            if test_file.endswith(".cnf"):  
                file_path = os.path.join(test_folder, test_file)
                print(f"Found CNF file: {test_file}")
                
                start_time = time.time()  # Start timing
                result = solve_file(file_path)
                end_time = time.time()  # End timing
                
                duration = end_time - start_time  # Calculate duration
                print(f"The result for the file {test_file} is: {result}")
                print(f"Time taken to solve {test_file}: {duration:.2f} seconds")  # Print duration
                all_results.append((test_file, result))  # Store the result

        print("\nSummary of Results:")
        for test_file, result in all_results:
            print(f"{test_file}: {result}")