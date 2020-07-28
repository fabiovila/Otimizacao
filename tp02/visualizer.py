#!/usr/bin/python
# -*- coding: utf-8 -*-


from collections import namedtuple
import matplotlib.pyplot as plt
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
        plt.scatter(Cxy[jj - i - 1][0], Cxy[jj - i - 1][1], marker='^', color=(0,0,1.0,0.5))

    Distancias = np.zeros((i,j))

    for ii in range(i):
      cor = tuple([float(Fi[ii-1])/np.max(Fi), float(Ci[ii-1])/np.max(Ci),0,0.5])
      plt.scatter(Ixy[ii-1][0], Ixy[ii-1][1], s= (Ci[ii-1]/np.max(Ci)) * 500 , marker='o', color = cor)
    plt.show()
    return ''


if __name__ == '__main__':
    sys.setrecursionlimit(10000)
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        output_data = solve_it(input_data)
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')
