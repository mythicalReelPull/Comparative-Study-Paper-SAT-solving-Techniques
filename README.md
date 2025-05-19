# Comparative-Study-Paper-SAT-solving-Techniques
Academic Article: Comparative Study of SAT Solving Techniques: Davis-Putnam, DPLL and CDCL Approaches

This repository contains the source code, datasets, and experimental pipeline for a comparative study of SAT solving techniques, including Resolution, Davis–Putnam (DP), DPLL, and CDCL.

## 📁 Structure

- `resolution_algorithm.py` – Resolution-based solver implementation.
- `dp_method.py` – Davis–Putnam algorithm implementation.
- `dpll_method.py` – DPLL solver with multiple heuristics.
- `tester.py`, `tester_DP.py`, `tester_DPLL.py` – Experimental runners for each solver.
- `chart_maker.py`, `chart_maker_cdcl.py`, `chart_maker_dpll.py` – Scripts to generate performance charts.
- `generator_clause_sets.py` – Generator for Pigeonhole Principle CNF files.
- `main.py` – TExperimental runner for PHP based on data present in `test_cases` folder.

## 📦 Requirements
All the test files were downloaded from: https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html
Files used from section "Uniform Random-3-SAT": 
uf20-91: 20 variables, 91 clauses - 1000 instances, all satisfiable
uf50-218 / uuf50-218: 50 variables, 218 clauses - 1000 instances, all sat/unsat
uf75-325 / uuf75-325: 75 variables, 325 clauses - 100 instances, all sat/unsat
uf100-430 / uuf100-430: 100 variables, 430 clauses - 1000 instances, all sat/unsat
uf125-538 / uuf125-538: 125 variables, 538 clauses - 100 instances, all sat/unsat
uf150-645 / uuf150-645: 150 variables, 645 clauses - 100 instances, all sat/unsat
uf175-753 / uuf175-753: 175 variables, 753 clauses - 100 instances, all sat/unsat
uf200-860 / uuf200-860: 200 variables, 860 clauses - 100 instances, all sat/unsat
uf225-960 / uuf225-960: 225 variables, 960 clauses - 100 instances, all sat/unsat
uf250-1065 / uuf250-1065: 250 variables, 1065 clauses - 100 instances, all sat/unsat
*uf- all satsifiable instances / *uuf- all unsatisfiable instances

Files used from section "'Flat' Graph Colouring":
flat30-60: 30 vertices, 60 edges - 100 instances, all satisfiable

One type of file (for example "uf20") need to be present(copy-pasted) in the folder "test_cases" 
of each of the methods used to solve the problem and test.

```bash
pip install matplotlib pandas
```

## 🧪 Running Experiments

1. **Resolution Experiments (e.g., Pigeonhole PHP(n,n-1))**

```bash
python main.py 
```

This uses `resolution_algorithm.py` and runs a test on small instances (e.g., `PHP(3,4)`). Larger instances like `PHP(7,8)` are infeasible due to exponential growth but it will still run it until it reaches the time limit. Make sure files exist in folder `PigeonHole_Problem/test_cases`

2. **DP Solver Experiments**

```bash
python tester_DP.py
```

Test DP solver on files from `test_files/uuf*`. All heuristics (MOM, JW, VSIDS) are applied and results saved as CSV.

3. **DPLL Experiments**

```bash
python tester_DPLL.py
```

Works on SATLIB `uf20`, `uf100`. Output includes runtime, memory, and SAT/UNSAT status.

4. **CDCL Experiments**

```bash
python tester.py
```

Includes VSIDS heuristic, clause learning, and Luby restarts. Performance graphs plotted using `chart_maker_cdcl.py` after firstly having a CSV of data in the correct format.

## 📊 Visualizing Results

Run appropriate chart scripts:

```bash
python chart_maker_dpll.py
python chart_maker_cdcl.py
python chart_maker.py \\for DP
```

Outputs: runtime comparisons, memory plots, heuristic analysis.

## 📄 Paper and Appendix

The LaTeX paper summarizing the work is included in `Comparative-Study-Paper-SAT-solving-Techniques`.
