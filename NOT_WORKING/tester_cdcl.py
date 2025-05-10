#!/usr/bin/env python3
"""
Batch-solve all DIMACS CNF files in a fixed directory using the VSIDS-CDCL solver.
"""
import time
from pathlib import Path
from typing import List, Tuple

from cdcl_method import VSIDS_CDCL


def read_cnf_file(path: Path) -> Tuple[List[List[int]], int]:
    """
    Read a DIMACS CNF file at `path`.
    Returns:
      clauses: List of clauses (each a list of ints, no trailing 0).
      max_var: maximum variable index.
    """
    clauses: List[List[int]] = []
    max_var = 0
    buffer: List[int] = []

    with path.open() as f:
        for raw in f:
            line = raw.strip()
            # skip comments and empty lines
            if not line or line.startswith(('c', '%')):
                continue
            # skip problem line
            if line.startswith('p '):
                continue

            # parse clause literals
            tokens = line.split()
            for tok in tokens:
                lit = int(tok)
                if lit == 0:
                    if buffer:
                        clauses.append(buffer.copy())
                        max_var = max(max_var, *(abs(x) for x in buffer))
                        buffer.clear()
                else:
                    buffer.append(lit)
        # catch any unterminated clause
        if buffer:
            clauses.append(buffer.copy())
            max_var = max(max_var, *(abs(x) for x in buffer))

    return clauses, max_var


def solve_cnf_file(cnf_path: Path, decay: float, decay_interval: int):
    print(f"┌── Processing {cnf_path.name}")
    clauses, num_vars = read_cnf_file(cnf_path)
    print(f"│ Clauses: {len(clauses)}, Variables: {num_vars}")
    # Print every parsed clause
    for idx, cl in enumerate(clauses, 1):
        print(f"│ Clause {idx:3d}: {cl}")

    solver = VSIDS_CDCL(clauses, decay_factor=decay)
    solver.decay_interval = decay_interval

    t0 = time.perf_counter()
    result = solver.solve()
    t1 = time.perf_counter()

    print(f"│ Result: {result.upper()} (in {t1 - t0:.2f}s)")

    if result == "sat":
        assignment = {}
        for v in range(1, num_vars + 1):
            if v in solver.assignment:
                assignment[v] = True
            elif -v in solver.assignment:
                assignment[v] = False
            else:
                assignment[v] = None
        print("│ Assignment:")
        for v, val in assignment.items():
            print(f"│   x{v} = {val}")
    print("└" + "─" * (len(cnf_path.name) + 12))


def main():
    # Hardcoded CNF directory and VSIDS parameters
    cnf_directory = Path('TEST_CDCL/test_cases')
    decay_factor = 0.95
    decay_interval = 100

    if not cnf_directory.is_dir():
        print(f"Error: {cnf_directory} is not a directory.")
        return

    for cnf_file in sorted(cnf_directory.glob('*.cnf')):
        solve_cnf_file(cnf_file, decay_factor, decay_interval)

if __name__ == '__main__':
    main()
