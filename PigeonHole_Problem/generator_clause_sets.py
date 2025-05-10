def generate_pigeonhole_clauses(pigeons, holes):
    """
    Generate clauses for the pigeonhole principle in Conjunctive Normal Form (CNF).
    The pigeonhole principle states that if there are more pigeons than holes and 
    each pigeon must be placed in a hole, then at least one hole must contain more 
    than one pigeon. This function generates the CNF clauses to represent this 
    principle.
    Parameters:
        pigeons (int): The number of pigeons.
        holes (int): The number of holes.
    Returns:
        List[Set[int]]: A list of clauses, where each clause is represented as a 
        set of integers. Positive integers represent variables, and negative 
        integers represent their negations.
    Clauses:
        1. Each pigeon must be assigned to at least one hole.
        2. No two pigeons can occupy the same hole simultaneously.
    """
    clauses = []

    # Each pigeon must go into at least one hole
    for i in range(1, pigeons + 1):
        clauses.append({i * 10 + j for j in range(1, holes + 1)})

    # No two pigeons can go into the same hole
    for i in range(1, pigeons + 1):
        for j in range(i + 1, pigeons + 1):
            for k in range(1, holes + 1):
                clauses.append({-(i * 10 + k), -(j * 10 + k)})

    return clauses


def write_cnf_to_dimacs(clauses, filename):
    """
    Write the given CNF clauses to a file in DIMACS format.
    Parameters:
        clauses (List[Set[int]]): The CNF clauses to write.
        filename (str): The name of the file to write to.
    """
    # Flatten the set of clauses into a list of lists
    dimacs_clauses = [list(clause) for clause in clauses]

    # Determine the number of variables and clauses
    num_clauses = len(dimacs_clauses)
    num_variables = max(abs(literal) for clause in dimacs_clauses for literal in clause)

    with open(filename, 'w') as f:
        # Write the header line
        f.write(f"p cnf {num_variables} {num_clauses}\n")

        # Write each clause
        for clause in dimacs_clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")


# Example usage
if __name__ == "__main__":
    pigeons = int(input("Enter the number of pigeons: "))
    holes = int(input("Enter the number of holes: "))

    # Generate clauses
    clauses = generate_pigeonhole_clauses(pigeons, holes)

    # Write to DIMACS file
    write_cnf_to_dimacs(clauses, f"pigeonhole_{pigeons}_{holes}.cnf")