 
import numpy as np
import os
import time
import cvxpy as cp

DEBUG = 0

Exit = False
TYPE = np.uint8


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
  
    # Recupera solução anterior  
    XijStart = np.zeros((i,j),dtype=TYPE)
    CjStart = np.zeros((j),dtype=TYPE)
    if solved != 0:
        for ii in range(n):
            XijStart[ii,int(solved[ii])] = 1
            CjStart[int(solved[ii])] = 1
    
    
    Xij = cp.Variable ((i,j), boolean=True, value=XijStart)
    Cj = cp.Variable ((j), boolean=True, value=CjStart)
    
    constraints = []
    
    
    
    # Constraint    
    # Cada Vértice i só pode estar em uma cor j
    for ii in range(i):
        if DEBUG >= 2: 
            # Saida em TEX. Só copiar e colar no Gummi e visualizar as equações
            print ("$\sum\limits_{j=0}^{"+str(j)+"} X_{"+str(ii)+",j} == 1$\\\\")
        constraints.append( cp.sum(Xij, axis = 1) == 1 )
    
    # Para cada Arestas
    for ee in edges:
        i0 = ee[0]
        i1 = ee[1]
        # Adiciona uma constraint de somente uma cor por Vértice
        for jj in range(j):
            if DEBUG >= 2:
                print ("$X_{"+str(i0)+","+str(jj)+"}+X_{"+str(i1)+","+str(jj)+"}<=Cj_{"+str(jj)+"}$\\\\")
            constraints.append( Xij[i0,jj] + Xij[i1,jj]  <= Cj[jj])
    
    #instance_list = ['gc_50_3', 'gc_70_7', 'gc_100_5','gc_250_9', 'gc_500_1', 'gc_1000_5']
    #good_values =   [8,          20,        21,        95,         18,         124       ]
    #great_values =  [6,          17,        16,        78,         15,         100       ]
    
    print ("Constraints num: " , len(constraints))
    print ("Max color usage: ", j)
    
    objective     = cp.Minimize( cp.sum(Cj) )  
    prob = cp.Problem(objective, constraints)
    
    prob.solve(solver=cp.CBC,verbose=True, maximumSeconds = 5 * 60 * 60) 
    
    output_data = ''

    if True:
        print("Status ", prob.status)
        print("Valor Otimo ", prob.value)
        
        output_data = '%d' % int( prob.value ) + '\n'
        solution = []
        
          
        for ii in range(i):
            for jj in range(j):
                if Xij[ii,jj].value == 1:
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

