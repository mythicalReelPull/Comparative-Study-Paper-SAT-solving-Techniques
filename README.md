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
- `main.py` – Entry point for custom testing or debugging.

## 📦 Requirements

```bash
pip install matplotlib pandas
```

## 🧪 Running Experiments

1. **Resolution Experiments (e.g., Pigeonhole PHP(n,n-1))**

```bash
python main.py pigeonhole_3_4.cnf
```

This uses `resolution_algorithm.py` and runs a test on small instances (e.g., `PHP(3,4)`). Larger instances like `PHP(7,8)` are infeasible due to exponential growth.

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
python main.py --cdcl --path test_files/uf50
```

Includes VSIDS heuristic, clause learning, and Luby restarts. Performance graphs plotted using `chart_maker_cdcl.py`.

## 📊 Visualizing Results

Run appropriate chart scripts:

```bash
python chart_maker_dpll.py
python chart_maker_cdcl.py
```

Outputs: runtime comparisons, memory plots, heuristic analysis.

## 📄 Paper and Appendix

The LaTeX paper summarizing the work is included in `Sat Solver Study`. Refer to Appendix A for GitHub link and citations.
