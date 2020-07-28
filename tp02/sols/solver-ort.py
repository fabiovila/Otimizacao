#!/usr/bin/python
# -*- coding: utf-8 -*-


from collections import namedtuple
import math
import numpy as np
import time
from ortools.linear_solver import pywraplp


DEBUG = 0

def solve_it(input_data):
    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    i = int(parts[0])       # Instalações
    j = int(parts[1])       # Clientes
    
    Fi = np.zeros(i)        # Custo de Abertura da instalação i
    Ci = np.zeros(i)        # Capacidade da instalação i 
    Ixy = np.zeros((i,2))   # Localização x,y da instalação i    
    
    Dj = np.zeros(j)        # Demanda do Cliente j
    Cxy = np.zeros((j,2))   # Localização x,y do cliente j
    
    Distancias = np.zeros((i,j)) # Distância da instalação i ao cliente j

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

    Distancias = np.zeros((j,i))

    for ii in range(i):
      for jj in range(j):
        Distancias[jj][ii] = np.sqrt(np.power(Ixy[ii][0] - Cxy[jj][0],2) + np.power(Ixy[ii][1] - Cxy[jj][1],2) )
    return facilityNaive(i,j,Fi,Ci,Dj,Distancias)


def facilityNaive(i,j,Fi,Ci,Dj,Distancias):
    
    solution = [0] * j

    solver = pywraplp.Solver('simple_mip_program',
                         pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    infinity = solver.infinity()
    
    # Variáveis de decisão 
    
    # Cliente j na instalação i
    Xji = {}
    for jj in range(j):
        for ii in range(i):
            Xji[(jj,ii)] = solver.IntVar(0.0,1.0,'Xji[%d,%d]' % (jj,ii))
            
    # Instalação i aberta
    Yi = {}
    for ii in range(i):
        Yi[ii] = solver.IntVar(0.0,1.0,'Yi[%d]' % (ii))
    
    
    
    # Constraint    
    # Cada Cliente só pode estar em uma instalação    
    for jj in range(j):
        solver.Add(sum(Xji[(jj,ii)] for ii in range(i)) == 1)
        # Dica do Carlos: Escala um cliente somente em instalações próximas. É tão óbvio ... puxa vida.
        # Porém dependendo do dataset pode ser uma armadilha ...
        solver.Add(sum(Xji[(jj,ii)] for ii in range(i)) <= np.sort(Distancias[jj])[int(i/4)])
        #print (np.min(Distancias[jj]), np.sort(Distancias[jj])[int(i/8)], np.max(Distancias[jj]))
        
    for ii in range(i):
        # Cada instalação só pode comportar Ci capacidade  
        solver.Add(sum(Xji[(jj,ii)] * Dj[jj] for jj in range(j)) <= (Ci[ii] * Yi[ii]))
        # Ao menos uma instalação tem que ser aberta
        solver.Add(sum(Yi[ii] for ii in range(i)) >= 1)

    
    # Objetivos
    objective = solver.Objective()
    for ii in range(i):
        # O Custo de abrir uma instalação
        objective.SetCoefficient(Yi[ii], Fi[ii])
        for jj in range(j): 
            # O Custo total de todos os clientes irem as suas intalações (distância euclidiana)
            objective.SetCoefficient(Xji[(jj,ii)], Distancias[jj][ii])
            
    objective.SetMinimization()
    
    
    tempo_minutos = 6*60
    
    solver.SetTimeLimit(tempo_minutos * 60 * 1000)
    #solver.EnableOutput()

    status = solver.Solve()
    
    output_data = ''
    #if status == pywraplp.Solver.OPTIMAL:
    if True:
        print('Objective value =', solver.Objective().Value())
        output_data = '%.2f' % solver.Objective().Value() + '\n'
        #for ii in range(i):
        #    if ( Yi[ii].solution_value() == 1):
        #        print (Yi[ii].name(), ' = ', Yi[ii].solution_value())
        for jj in range(j):
            for ii in range(i):
                if Xji[(jj,ii)].solution_value() >= 1:
                    #print (Xji[(jj,ii)].name(), ' = ' , Xji[(jj,ii)].solution_value())
                    output_data += str(int(ii)) + ' '
               
        print()
        print('Problem solved in %f milliseconds' % solver.wall_time())
        print('Problem solved in %d iterations' % solver.iterations())
        print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
    else:
        print('The problem does not have an optimal solution.')

    return output_data

#    instance_list = ['fl_25_2', 'fl_50_6', 'fl_100_7', 'fl_100_1', 'fl_200_7', 'fl_500_7','fl_1000_2', 'fl_2000_2']
#    good_values =   [4000000,   4500000,    2050,       26000000,    5000000,   30000000,  10000000,    10000000]
#    great_values =  [3269822,   3732794,    1966,       22724066,    4711295,   27006099,  8879294,     7453531]

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        output_data = solve_it(input_data)
        #print(output_data)
        print(file_location)
        solution_file = open(file_location + ".sol", "w")
        solution_file.write(output_data)
        solution_file.close()
        
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')
