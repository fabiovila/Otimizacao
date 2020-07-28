#!/usr/bin/python
# -*- coding: utf-8 -*-


from collections import namedtuple
import math
import numpy as np
import time
import random
import sys



DEBUG = 0

def solve_it(input_data):
    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    i = int(parts[0])
    j = int(parts[1])
    
    Fi = np.zeros(i)        # Custo de Abertura da instalação i
    Ci = np.zeros(i)        # Capacidade da instalação i 
    Ixy = np.zeros((i,2))   # Localização x,y da instalação i    
    
    Dj = np.zeros(j)        # Demanda do Cliente j
    Cxy = np.zeros((j,2))   # Localização x,y do cliente j
    
    Distancias = np.zeros((i,j))

    for ii in range(1, i+1):
        parts = lines[ii].split()
        Fi[ii-1] = float(parts[0])
        Ci[ii-1] = int(parts[1])
        Ixy[ii-1][0] = float(parts[2])
        Ixy[ii-1][1] = float(parts[3])

    for jj in range(i+1, i+1+j):
        parts = lines[jj].split()
        Dj[jj - i - 1] = int(parts[0])
        Cxy[jj - i - 1][0] = float(parts[1])
        Cxy[jj - i - 1][1] = float(parts[2])

    Distancias = np.zeros((i,j))

    for jj in range(j):
      for ii in range(i):
        Distancias[ii][jj] = np.sqrt(np.power(Ixy[ii][0] - Cxy[jj][0],2) + np.power(Ixy[ii][1] - Cxy[jj][1],2) )
    #Dj = Dj.T

    #print (Distancias)


    return facilityNaive(i,j,Fi,Ci,Dj,Distancias)

def DistribuiGuloso (Xij,j,Ci,Dj,Distancias,DelI):
    #print (Xij.T, j)
        
    if len(j) > 0:
        x = np.argsort(Distancias[ :,j[0]]) # Indice das distâncias mais curtas ao cliente j
        #print (j, Distancias[ :,j[0]])

        demanda = ((Dj @ (Xij.T)) - (Ci * (np.sum(Xij, axis=1)))) + Dj[j[0]]  # Retorna o saldo das intalações com a adição desse cliente. Se positivo ou zero ok.
        demanda[DelI] = -1
        candidatos = x[(demanda[x] >= 0).nonzero()]   # Retorna lista das intalações com capacidade livre e mais perto desse cliente j
        if len(candidatos) > 0:
            Xij[candidatos[0]][j[0]] = 1     # e finalmente coloca-se o cliente nessa instalação

        del j[0]
        #print (Dj @ (Xij.T) , candidatos)
        return DistribuiGuloso (Xij,j,Ci,Dj,Distancias, DelI)
    else:
        return Xij
    


def facilityNaive(i,j,Fi,Ci,Dj,Distancias):
    
    np.random.seed(int(time.time()))
    Cij =   np.ones((i,j))
    solution = [0] * j
    
    # Variáveis de decisão
    Xij = np.zeros((i,j))         #np.random.randint(0,high=2,size=(i,j))      #np.zeros ((i,j))  
    #Xij[0] = np.ones(j)
        
    Yi = np.random.randint(0,high=2,size=i)           #np.zeros (i)    
    Cli = np.zeros(j*i)
    Cli[0:j] = np.ones(j)
    at = Cli.reshape(i,j).T
    Ones = np.ones(j)
    RollVector = np.array([-1-2,1,2])
    #print (at)
           
    for jj in range(j):
        np.random.shuffle(at[jj])
    #print (at.T)
    best_solution = [Xij, np.iinfo(np.uint64).max]
    
    print ("...")
    
    Xij = DistribuiGuloso(Xij,list(range(j)),Ci,Dj,Distancias, np.random.randint(0,high=i) )
    at = Xij.T
    
    for ii in range(1000000):
        
        Xij = at.T 
        custo_distanc = np.sum(np.multiply(Xij,Distancias))     # Distância total da solução
        instalacoes_usadas = (np.sum(Xij, axis=1) > 0)
        custo_fixo    = np.sum(Fi * instalacoes_usadas)         # Soma dos custo de abertura de cada instalação
        custo_total   = custo_fixo + custo_distanc              # Custo Total
        estouro = (Dj @ Xij.T) <= (Ci * instalacoes_usadas) 
        
        if custo_total < best_solution[1]:
            if np.all( estouro ): 
                best_solution[0] = np.copy(Xij)
                best_solution[1] = custo_total
                print (" Best_solution custo: {} Iterações: {}".format(custo_total,ii))
                fileout(Xij, custo_total)
                
        # Destaca as intalações com demanda estourada     
        w = np.where(estouro == False)[0]   
        #print (w)
        if len(w) > 0: # seleciona aleatóriamente uma instalação estourada e um cliente nessa instalação
            index = np.random.choice(w)
            index = np.random.choice(np.where(Xij[index] == 1)[0])            
        else:
            n = list(range(j))
            random.shuffle(n)
            Xij *= 0
            at = DistribuiGuloso(Xij,n,Ci,Dj,Distancias, np.random.randint(0,high=i)).T                
            continue

        if ii % j*i == 0: # gera uma solução aleatória de tempos em tempos
            n = list(range(j))
            random.shuffle(n)
            Xij *= 0
            at = DistribuiGuloso(Xij,n,Ci,Dj,Distancias, np.random.randint(0,high=i) ).T
        else: # altera o cliente de instalação
            at[index] = np.roll(at[index],np.random.choice(RollVector))
            
        
        #print (at)
        #input()

    if np.sum(Xij) != j:
        exit()

    Xij = best_solution[0]
    custo_total = best_solution[1]

    print ("Custo de abertura: ", Fi * (np.sum(Xij, axis=1) > 0))
    #print("Instalações abertas", cp.multiply(Ci,Yi).value)
    print("Instalação i cliente j \n", Xij, )
    print ("Capacidade de cada instalação: \n" , Dj @ Xij.T) 

    print ("Custo Total" , custo_total) 
    print (np.nonzero(Xij))
    Consumidores = np.nonzero(Xij)[1]
    Instalacoes = np.nonzero(Xij)[0]
            
    for c,i in zip(Consumidores,Instalacoes):
        solution[c] = i
    print (solution)

    output_data = '%.2f' % custo_total + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

def fileout(Xij, custo_total):
    solution = [0] * Xij.shape[1]
    #print (np.nonzero(Xij))
    Consumidores = np.nonzero(Xij)[1]
    Instalacoes = np.nonzero(Xij)[0]
    for c,i in zip(Consumidores,Instalacoes):
        solution[c] = i
    #print (solution)

    output_data = '%.2f' % custo_total + '\n'
    output_data += ' '.join(map(str, solution))
    print("Custo Gravado: " , custo_total)
    #print(file_location)
    solution_file = open(file_location + ".sol", "w")
    solution_file.write(output_data)
    solution_file.close()


if __name__ == '__main__':
    sys.setrecursionlimit(10000)
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        output_data = solve_it(input_data)
        print(output_data)
        print(file_location)
        solution_file = open(file_location + ".sol", "w")
        solution_file.write(output_data)
        solution_file.close()
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')
