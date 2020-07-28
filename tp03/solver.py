
import numpy as np

DEBUG = 0

def solve_it(input_data):
    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    n = node_count
    e = edge_count

    Arestas = np.array((n,n))

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
        Arestas[(int(parts[0]), int(parts[1]))] = 1

    if DEBUG >= 1:
        print(f"Numero de vertices = {node_count}")
        print(f"Numero de arestas = {edge_count}")

    if DEBUG >= 2:
        print("Arestas:")
        for edge in edges:
            print(edge)
            print (Arestas)
        print()

    return ColoringNaive(e,n,Arestas)

def write (e, solution):
    # prepare the solution in the specified output format
    output_data = str(e) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


def ColoringNaive(e,n,Arestas):

    print (Arestas)

    

    return write(e, solution)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        output_data = solve_it(input_data)
        print(output_data)
        solution_file = open(file_location + ".sol", "w")
        solution_file.write(output_data)
        solution_file.close()
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')
