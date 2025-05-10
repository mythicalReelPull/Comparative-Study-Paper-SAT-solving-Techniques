import time

def resolution_solver(clauses):
    """
    A simple resolution-based SAT solver with step-by-step output and 5-second timeout.
    :param clauses: A list of clauses (each clause is a list of literals).
    :return: "UNSATISFIABLE" if unsatisfiable, "SATISFIABLE" if satisfiable, 
            "TIMEOUT" if computation exceeds 5 seconds.
    """
    start_time = time.time()
    # Convert each clause (list) into a frozenset for hashing
    new_clauses = set(frozenset(clause) for clause in clauses)
    print("\nInitial clauses:", [list(c) for c in new_clauses])
    
    iteration = 1
    while True:
        # Check if 5 seconds have passed
        if time.time() - start_time > 5:
            print("\nTime limit has exceeded 5 seconds")
            return "TIMEOUT"

        print(f"\nIteration {iteration}:")
        # Generate all pairs of clauses
        pairs = [(ci, cj) for ci in new_clauses for cj in new_clauses if ci != cj]
        resolvents = set()

        for (ci, cj) in pairs:
            # Check timeout within the inner loop as well
            if time.time() - start_time > 5:
                print("\nTime limit has exceeded 5 seconds")
                return "TIMEOUT"

            # Find resolvents for the pair
            for literal in ci:
                if -literal in cj:
                    resolvent = (ci - {literal}) | (cj - {-literal})
                    if not resolvent:  # Empty clause found
                        print(f"Empty clause derived from resolving {list(ci)} and {list(cj)}")
                        return "UNSATISFIABLE"
                    print(f"Resolving {list(ci)} and {list(cj)} on literal {literal}")
                    print(f"New resolvent: {list(resolvent)}")
                    resolvents.add(frozenset(resolvent))

        # If no new resolvents, stop
        if resolvents.issubset(new_clauses):
            print("\nNo new resolvents can be generated.")
            return "SATISFIABLE"

        print(f"New resolvents in iteration {iteration}:", [list(r) for r in resolvents])
        new_clauses.update(resolvents)
        iteration += 1