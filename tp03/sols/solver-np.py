 
import numpy as np
import os
import time
import queue
import threading

DEBUG = 3 

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

    Arestas = np.zeros((n,n),dtype=TYPE)

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
        
        edges.append((a,b))
        Arestas[a,b] = 1
        Arestas[b,a] = 1
        
    solved = 0
    if solved_data != None:
        lines = solved_data.split('\n')
        solved = lines[1].split()
        

    if DEBUG >= 1:
        print("Numero de vertices = {node_count}")
        print("Numero de arestas = {edge_count}")

    if DEBUG >= 2:
        print("Arestas:")
        for edge in edges:
            print(edge)
        print()

    return ColoringNaive(e,n,Arestas,solved)

def write (m):
    solution = [0] * m.shape[0]
    for i in range(m.shape[0]):
        solution[i] = int(np.max(m.T[i])) - 2
    output_data = str(int(np.max(m) - 1)) + '\n'
    output_data += ' '.join(map(str, solution))
    solution_file = open(file_location + ".sol", "w")
    solution_file.write(output_data)
    solution_file.close()
    return output_data

def Permuta(index, n):
    x = np.random.randint(0,high = n) 
    
    y = x + np.random.choice([-1,+1])
    
    if x == 0:
        y = 1
    if x == (n - 1):
        y = x -1
    
    b = index[x]
    index[x] = index[y]
    index[y] = b
    
    return index

def ColoringNaive(e,n,Arestas, solved):
    
    np.random.seed(int(time.time()))

    best_solution = 0
    best_min      = n 
    worsth = np.arange(2, int(n / 2) + 2)
    Arestas = Arestas + np.identity(n,dtype=TYPE)
    Range = np.arange(n)
    Maiores = np.argsort(np.sum(Arestas, axis = 1))[::-1]
    
    A = np.copy(Arestas)

    Colisoes = np.zeros(n, dtype=np.int32)
    
    Index = np.zeros(n)
    its = 1
    
    if solved != 0:
        # Recupera solução anterior  
        for ii in range(n):
            A[:,ii] = A[:,ii] * (int(solved[ii]) + 2)

    else:
        # Se não inicia com um algoritimo Guloso como ponto de partida    
        for ii in Maiores:
            it = np.min(np.setdiff1d(worsth,A[ii]))
            A[:,ii] = A[:,ii] * it
    
    U = np.max(A)
    best_solution   = np.copy(A)
    best_min        = int(U)
    Best_Index      = np.copy(Maiores[::-1])
    print ("Start Solution: ", best_min - 1)


    # Index é a lista que ordena quem recebe as cores
    Index = Maiores
    timestep = time.time() + 5
    its = 1

    for i in range(1000000):            

        if  U < best_min:
            
            # Sanity check. Nunca ocorreu.
            if U != len(np.unique(A)):
                print ("Algo deu errado no cálculo das cores", U,len(np.unique(A)))
                exit()
                
            Best_Index = Index
            best_solution   = np.copy(A)
            best_min        = int(U)
            B = np.copy(A)
            if DEBUG >= 1:
                print ("Best Solution: ", best_min - 1)
            write(best_solution)

        A = np.copy(Arestas) 
        #A[A > 0] = 1 # Copiar é levemente mais rápido. E faz todo sentido

        
        # Da aquela sacudida no local atual
        if i % 101 == 0:     
            # Copia a melhor solução atual para trabalharmos nela 
            
            Index = Permuta(np.copy(Best_Index),n)

            
        if i % 307 == 0:
            # Os vertices com mais arestas montam primeiro. 
            Index = np.argsort(np.sum(Arestas, axis = 1))[::-1]
        if i % (n * 2) == 0:
            # Gera uma solução randonica
            Index = np.random.permutation(np.arange(n)) 
        
        
        U = 0
        
        # Basicamente a exploração das soluções ocorre aqui
        # Monta a solução e se for detectado pior caso faz alterações para a próxima rodada
        for xx,ii in enumerate(Index):
            # Procura a menor cor que os vizinhos desse vértice não tem
            it = np.min(np.setdiff1d(worsth,A[ii]))
            if it >= best_min:                       # Interrompe a montagem dessa solução se pior ou igual que o melhor caso     
                Colisoes[ii] += 1                    # Faz uma simples contagem de quais vértices estão mais problemáticos
                                                     # A permutação abaixo fez com que a distribuição da contagem dos vértices problemáticos fique quase uniforme
                x = np.random.randint(0,high = xx)   # Troca o vértice que foi o pior caso com algum aleatório antes dele. Se mostrou muito efetivo
                b = Index[x]
                Index[x] = Index[xx]
                Index[xx] = b
                U = n
                break

            if it > U:
                U = it
            # Atribui a cor it ao vértice ii da lista Index
            A[:,ii] = A[:,ii] * it
 

        if timestep < time.time():       
            
            timestep = time.time() + 5
            if DEBUG >= 2:
                #print (Colisoes)
                print (np.diagonal(A))
                #print (np.histogram(Colisoes, bins = np.max(Colisoes)))
            Colisoes *= 0
            if DEBUG >= 1:
                print ("Vertices: {}, Iteração: {}, Iterações por tempo: {}, Best_Solution: {}".format(n, i, i-its,best_min - 1))
            its = i
            time.sleep(0.5) # Permite não matar meu servidor GCLOUD! Se deixar rolar livre leve e solto nem login é possível fazer. Até o Apache fica irresponsivo.

    return write(best_solution)


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
