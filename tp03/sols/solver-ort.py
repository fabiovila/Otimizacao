 
import numpy as np
import os
import time
from ortools.linear_solver import pywraplp

DEBUG = 0

Exit = False



def solve_it(input_data, solved_data):
    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])
    

    n = node_count
    e = edge_count
    
    nodes = np.zeros(n)

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        a = int(parts[0])
        b = int(parts[1])

        if b < a:
            c = b
            b = a
            a = c
            
        nodes[a] += 1
        nodes[b] += 1
        
        edges.append((a,b))
        
    solved = 0
    if solved_data != None:
        lines = solved_data.split('\n')
        solved = lines[1].split()
    
    if np.any(nodes == 0):
        print ("Existem Vértices sem Arestas")
        exit()
    
        
    if DEBUG >= 1:
        print("Numero de vertices = {node_count}")
        print("Numero de arestas = {edge_count}")

    if DEBUG >= 2:
        print("Arestas:")
        for edge in edges:
            print(edge)
        print()

    return ColoringNaive(e,n,edges,solved)


def ColoringNaive(e,n,edges,solved):
    
    i = n
    if n > 10:
        j = int(n / 2)
    else:
        j = n
        
    solver = pywraplp.Solver('simple_mip_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)      

    # Variáveis de decisão     
    # Vértice i na cor j
    Xij = {}
    for ii in range(n):
        for jj in range(j):
            Xij[(ii,jj)] = solver.IntVar(0,1,'Xij[%d,%d]' % (ii,jj))


    # Cor j é verdadeira se contém ao menos um Vértice
    Cj = {}
    for jj in range(j):        
        Cj[(jj)] = solver.IntVar(0,1,'Cj[%d]' % (jj))
    
    # Constraint    
    # Cada Vértice i só pode estar em uma cor j
    for ii in range(i):
        solver.Add(sum(Xij[(ii,jj)] for jj in range(j)) == 1)
    
    # Para cada Arestas
    for ee in edges:
        i0 = ee[0]
        i1 = ee[1]
        # Adiciona uma constraint de somente uma cor por Vértice
        for jj in range(j):
            # Cada vértice em cada cor juntos só podem ter valor 1 somados.
            #solver.Add( Xij[(i0,jj)] + Xij[(i1,jj)]  <= 1)
            # Como Cj só pode ser 1 ou 0 substitui o 1 acima por Cj[jj]
            solver.Add( Xij[(i0,jj)] + Xij[(i1,jj)]  <= Cj[(jj)])
    
    #instance_list = ['gc_50_3', 'gc_70_7', 'gc_100_5','gc_250_9', 'gc_500_1', 'gc_1000_5']
    #good_values =   [8,          20,        21,        95,         18,         124       ]
    #great_values =  [6,          17,        16,        78,         15,         100       ]
    
    solver.Minimize( sum(Cj[(jj)] for jj in range(j)) )
    
    tempo_minutos = 1 * 60
    
    solver.SetTimeLimit(tempo_minutos * 60 * 1000)
    solver.EnableOutput()

    status = solver.Solve()
    
    output_data = ''
    #if status == pywraplp.Solver.OPTIMAL:
    if True:
        print('Objective value =', solver.Objective().Value())
        output_data = '%d' % int(solver.Objective().Value()) + '\n'
        solution = []
        
          
        for ii in range(i):
            for jj in range(j):
                if Xij[(ii,jj)].solution_value() == 1:
                    solution.append(jj)
                    

        
        unicos = np.unique(solution)
        cores = list(range(len(unicos)))
        
        for c in unicos:
            for ii in range(i):
                if solution[ii] == c:
                    solution[ii] = cores[0]
            del cores[0]
        
        print (solution)
        
            
        output_data += " ".join(map(str, solution))
        
        print (i,j)     
        print()
        print('Problem solved in %f milliseconds' % solver.wall_time())
        print('Problem solved in %d iterations' % solver.iterations())
        print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
    else:
        print('The problem does not have an optimal solution.') 
        
        
        

    return output_data


if __name__ == '__main__':
    import sys
    
    
    
    
    if len(sys.argv) > 1:

        from sys import platform
        if platform == "linux" or platform == "linux2":
            import subprocess
            result = subprocess.check_output("tput cols", shell=True)
            print (result)
            np.set_printoptions(linewidth=int(result))
            
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        solved_data = None
        if os.path.isfile(file_location + ".sol"):
            with open(file_location + ".sol", 'r') as solved_data_file:
                solved_data = solved_data_file.read()
                
        output_data = solve_it(input_data, solved_data)
        print ("\n")
        print(output_data)
        solution_file = open(file_location + ".sol", "w")
        solution_file.write(output_data)
        solution_file.close()
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

