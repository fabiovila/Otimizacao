#!/usr/bin/python
# -*- coding: utf-8 -*-


from collections import namedtuple
import math
import numpy as np
import cvxpy as cp

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
    
    Distancias = np.zeros((i,j+1))

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



    return facilityNaive(i,j,Fi,Ci,Dj,Distancias)


def facilityNaive(i,j,Fi,Ci,Dj,Distancias):
  
    Cij =   np.ones((i,j))
    solution = [0] * j
    
    # Variáveis de decisão
    Xij = cp.Variable ((i,j), boolean=True, value = np.ones((i,j)))                 # Instalação i contém clientes j
    #Yi = cp.Variable (i,boolean=True)    
    
    # Objetivo
    Yi = np.max(Xij.value, axis=1) 
    custo_fixo    = Fi @ Yi                                # Soma dos custo de abertura de cada instalação
    custo_distanc = cp.sum(cp.multiply(Xij,Distancias))     # Distância total da solução
    custo_total   = custo_fixo + custo_distanc              # Custo Total
    objective     = cp.Minimize(custo_total)                # Objetivo é minimizar o custo_total
    
    # Restrições
    constraints = []
    # Respeita a capacidade máxima de cada instalação
    constraints.append( Dj @ Xij.T <= cp.multiply(Ci,Yi) )
    # Ao menos uma alocação é necessária
    constraints.append(cp.sum(Yi) >= 1)
    # Um cliente só deve ser alocado em uma instalação
    constraints.append(cp.sum(Xij, axis=0) == 1) 
    # Distância máxima
    constraints.append(custo_distanc <= 10000000) 

    # Resolve o problema
    prob = cp.Problem(objective, constraints)
    #prob.solve(solver=cp.GLPK_MI,verbose=True)             # Não descobri como instalar CBC no Google Colab então tem que usar esse que é muito lento ...
    print ("...")
    prob.solve(solver=cp.CBC,verbose=True, maximumSeconds = 1 * 60 * 60)  


    print("Status ", prob.status)
    print("Valor Otimo ", prob.value)
    print ("Custo de abertura: ", custo_fixo)
    #print("Instalações abertas", cp.multiply(Ci,Yi).value)
    #print("Instalação i cliente j \n", Xij.value, )
    #print ("Capacidade de cada instalação: \n" , (Dj @ Xij.T).value) 

    print ("Custo Total" , custo_total.value) 
    print (np.nonzero(Xij.value))
    Consumidores = np.nonzero(Xij.value)[1]
    Instalacoes = np.nonzero(Xij.value)[0]
            
    for c,i in zip(Consumidores,Instalacoes):
        solution[c] = i
    print (solution)

    output_data = '%.2f' % custo_total.value + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data



if __name__ == '__main__':
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
