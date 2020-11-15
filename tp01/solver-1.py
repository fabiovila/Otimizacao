
# Comentários gerais:
# Foi escolhido numpy para ganhar velocidade, porém a melhor opção mesmo seria C++
# O algoritmo de solução usa de muita aleatoriedade em busca da solução do problema
# o que fará com que cada execução tenha resultado diferente


from collections import namedtuple
import numpy as np
import os
import random
import psutil
import gc


Item = namedtuple("Item", ['index', 'value', 'weight'])

DEBUG = 1

INDEX = 0
VALUE = 1
WEIGHT = 2
SOLUTION = 3
MAX_AGENDA = 1000

RAM = 0.15

pid = os.getpid()
py = psutil.Process(pid)
memoryUse = py.memory_info()  
if DEBUG >= 1:
    print('memory use:', memoryUse)
    print('memory use:', psutil.virtual_memory())


def solve_it(input_data):
    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])
    conflict_count = int(firstLine[2])

    items = np.zeros((item_count,3), dtype="i")
    conflicts = []
    conflicts_list = np.zeros((conflict_count,item_count), dtype="i")

    maior_peso = 0
    menor_peso = 99999999999

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items[i-1] = np.array([i-1,int(parts[0]), int(parts[1])])

        if int(parts[1]) > maior_peso:
            maior_peso = int(parts[1])
        if int(parts[1]) < menor_peso:
            menor_peso = int(parts[1])
    if DEBUG >= 1:
        print ("Maior: ", maior_peso)
        print ("Menor: ", menor_peso)      
    for i in range(1, conflict_count+1):
        line = lines[item_count + i]
        parts = line.split()
        conflicts.append((int(parts[0]), int(parts[1])))

    return RandomSearch(item_count, items, capacity, conflict_count, conflicts)

# Faz nova mascara não aleatória
def NewMask (size, shape):
    ones = np.ones(size, dtype="i")
    zeros = np.zeros(shape - size, dtype="i")    
    return np.hstack((ones,zeros))

# faz diversas mascaras sortidas
def NewList(flag, items, size, shape, items_weight, items_value):

    if flag == 0:  # Retorna lista organizada por valor / peso
        d = (items_value / items_weight).argsort()  
        a = np.copy(items_weight)
        a[d[:(d.size - size)]] = 0
        return  a
    if flag == 1:  # Retorna lista organizada por peso / valor
        d = (items_weight / items_value).argsort()  
        a = np.copy(items_weight)
        a[d[:(d.size - size)]] = 0
        return  a
    if flag == 2:  # Retorna lista organizada valor
        d = (items_value).argsort()  
        a = np.copy(items_weight)
        a[d[:(d.size - size)]] = 0
        return  a
    if flag == 3:  # Retorna lista organizada por peso
        d = (items_weight).argsort()
        a = np.copy(items_weight)
        a[d[:(d.size - size)]] = 0
        return  a
    if flag == 4: # os ultimos na ordem entrada
        a = np.copy(items_weight)
        a[:(a.size - size)] = 0
        return  a
    if flag == 5: # os primeiros na ordem entrada
        a = np.copy(items_weight)
        a[size:] = 0
        return  a

    return np.copy(items_weight)

# Faz mudanças aleatórias na máscara ativando ou desativando um item
def ChangeMask (mask, size,items_weight):
    index = np.random.randint(low = 0, high = mask.size, size = int(size) )
    mask[index] = mask[index] ^ items_weight[index]
    return mask

# faz um rol na mascara. Se mostrou pouco efetivo.
def Rol(mask, items_weight):
    nz = np.nonzero(mask)[0]
    nz = nz + 1
    nz[ nz >= mask.size ]  = 0    
    mask = np.zeros_like(mask, dtype="i")
    mask[nz] = items_weight[nz]
    return mask

# faz um caminho browniano na máscara (ou seja mais aleatoriedade)
def Neighboor(mask, items_weight):
    nz = np.nonzero(mask)[0]
    index = np.random.randint(low = -1, high = 2, size = nz.size)
    nz += index    
    nz[ nz >= mask.size ]  = 0
    nz[ nz < 0 ]  = mask.size - 1
    nz = np.unique(nz)
    mask = np.zeros_like(mask, dtype="i")
    mask[nz] = items_weight[nz]
    return mask

# remove o maior peso da máscara. Não usado mais pois remove é mais efetivo
def RemoveMaxWeight(mask):
    d = mask.argsort()
    if np.count_nonzero(mask) > 1:
        mask[d[-1]] = 0
    return mask

# remove o menor valor da máscara. Não usado pois remove é mais efetivo
def RemoveMinValue(mask, items_value):
    z = np.nonzero(mask)[0]
    values = items_value[z]
    v = values.argsort()
    if np.count_nonzero(mask) > 1:
        mask[z[v[0]]] = 0
    return mask

# adiciona items a máscara até o limite da memória
# e de fato tem funcionado. Quando uma melhor máscara é achada com capacidade ociosa o preenchimento é logo feito
def Add(mask, items_weight, capacity, num = 0):
    c = np.where( items_weight <= capacity )[0]
    m = np.nonzero(mask)[0]
    z = np.setdiff1d(c, m)
    l = []
    e = np.copy(mask)
    if num == 0:
        num = z.size
    if (z.size > 0):
        # a aleatoriedade se faz presente em diversos momentos
        np.random.shuffle(z)
        for zz in z:
            m = np.copy(mask)
            m [zz] = items_weight[zz]
            e [zz] = items_weight[zz]
            l.append(m)
            l.append(np.copy(e))
            #memory = psutil.virtual_memory()
            #if memory.available / memory.total <= RAM:
            #    break
    return l

# remove items da máscara até o limite da memória
def Remove(mask, num = 0):
    m = np.nonzero(mask)[0]
    l = []
    if num == 0:
        num = m.size
    if (m.size > 1):
        temp = np.copy(mask)
        np.random.shuffle(m)
        for mm in m:
            temp[mm] = 0
            if np.count_nonzero(temp) > 0:
                l.append(np.copy(temp))
            #memory = psutil.virtual_memory()
            #if memory.available / memory.total <= RAM:
            #    break
    return l

# rotina principal em busca da solução do problema. Se chama RandomSearch porque apesar de ter 
# diversas heuristicas iniciais a aleatoriedade é que realmente soluciona o problema
# A rotina ataca em duas frente:
#  usa o agendamento de sugestões de máscaras através da lista mask_agenda
#  usa rotinas de alterações aleatórias e determinadas na máscara atual
def RandomSearch(num_items, items, capacity, num_conflicts, conflicts):

    if DEBUG >= 1:
        print(f"numero de itens = {num_items}")
        print(f"capacidade da mochila = {capacity}")
        print(f"numero de conflitos = {num_conflicts}")

    if DEBUG >= 2:
        print("Itens na ordem em que foram lidos")
        for item in items:
            print(item)
        print()

    if DEBUG >= 2:
        print("Conflitos na ordem em que foram lidos")
        for conflict in conflicts:
            if DEBUG >= 3:
                print (conflict, np.where(conflicts_index[conflict[0]] == True,1,0),np.where(conflicts_index[conflict[1]] == True,1,0))
            else:
                print (conflict)
        print()    


    best_solution = np.zeros(num_items, dtype="i")
    best_solution_value = 1
    best_solution_weight = 0
    best_mask = np.zeros(num_items, dtype="i")

    items_weight = np.copy(items[:,WEIGHT])
    items_value  = np.copy(items[:,VALUE])

    # a rotina usa um sistema de agenda. 
    mask_agenda = []
    best_agenda = []
    conflict_true = False
    mask = np.ones(num_items, dtype="i")

    capacity_calc = -1
    num = num_items
    media_num = num_items
    zero = np.zeros(num_items)  

    # faz uma análise inicial de quantos items em média é necessário para 
    # que se atinja a capacidade da mochila. Isso ajuda a não se perder em construir máscaras
    # excessivas ou insuficientes. Esse algoritmo é não-deterministico, ou seja, os valores mudam a cada execu

    for i in range(1000):
        while capacity_calc < 0 and num > 0:
            r = np.random.randint(low = 0, high = num_items, size = int(num))
            z = np.zeros_like(items_weight, dtype="i")
            z[r] += items_weight[r] 
            mask = z
            masksum = mask.sum()
            value = items_value[np.nonzero(mask)].sum() 
            capacity_calc = capacity - masksum
            num -= 1

    if media_num < 5 or 2 * media_num >= num_items:
        media_num  = num_items / 8

        
    # constroi inicialmente mascaras com heuristicas propostas pelo Prof.
    # como os algoritmos gulosos de preenchimento
    # as máscaras começam com 1 item até o dobro da média de items achados anteriormente que atingem a capacidade da mochila
    for i in range(1, int(media_num + media_num)):
        mask_agenda.append(NewList(0,items,i,num_items,items_weight,items_value))
        mask_agenda.append(NewList(1,items,i,num_items,items_weight,items_value))
        mask_agenda.append(NewList(2,items,i,num_items,items_weight,items_value))
        mask_agenda.append(NewList(3,items,i,num_items,items_weight,items_value))
        mask_agenda.append(NewList(4,items,i,num_items,items_weight,items_value)) 
        mask_agenda.append(NewList(5,items,i,num_items,items_weight,items_value)) 
        mask = np.zeros(num_items, dtype="i")
        index = np.random.randint(low = 0, high = num_items, size = i )
        mask[index] = mask[index] + items_weight[index]
        mask_agenda.append(mask)


    # agenda máscaras com um item apenas para inicio
    for i in range(0,num_items):
        mask = np.zeros(num_items, dtype="i")
        mask[i] = items_weight[i]
        mask_agenda.append(mask) 
        

    best_mask = NewList(0,items,int(media_num),num_items,items_weight,items_value)
    best_solution_value = items_value[np.nonzero(mask)].sum() 
    best_solution_weight = best_mask.sum()
    best_solution = np.zeros_like(mask, dtype="i")
    best_solution[np.nonzero(mask)] = 1
    mask_agenda.append(mask)
    
    flag = 0
    
    # loop principal de solução
    # 
    for deep in range(200000):    
        
        # faz o desagendamento das mascaras para análise
        # porém faz um rodízio de alterações e geração de máscaras aleatórias
        flag += 1       
        if len(mask_agenda) > 0:
            if flag  == 0:
                mask = mask_agenda.pop()  # desagenda as últimas máscaras              
            if flag  == 1:
                mask = mask_agenda.pop(0) # desagenda as primeiras máscaras
            if flag  == 2:
                mask = random.choice(mask_agenda) # desagenda uma máscara aleatória
        else:
            # faz alterações aleatórias na melhor máscara que achamos
            mask = ChangeMask(np.copy(best_mask),deep % (media_num + media_num),items_weight)
            flag = 3
        if flag == 3:
            # faz alterações aleatórias na máscara atual
            mask = ChangeMask(np.copy(mask),deep % (media_num + media_num),items_weight)
        if flag == 4:
            # faz um rol da máscara atual
            mask = Rol(mask,items_weight)
        if flag == 5:
            # faz alterações na máscara atual
            mask = Neighboor(mask,items_weight)
        if flag == 6:
            # faz alterações aleatórias na melhor máscara
            mask = Neighboor(np.copy(best_mask),items_weight)
            flag = 0

        masksum = mask.sum()
        capacity_calc = capacity - masksum

        if masksum == 0:
            continue

        # então ... em uma instância gcloud com 650Mb ou no meu notebook com 8G 
        # rodar a versão 10000 leve e solta acaba com a memória
        memory = psutil.virtual_memory().available / psutil.virtual_memory().total

        # se a capacidade da máscara excede a mochila agendamos retiradas para análise
        if capacity_calc < 0:
            if memory > RAM:
                mask_agenda += Remove(mask)   
            continue
                      
            
        value = items_value[np.nonzero(mask)].sum() 

        # detecta conflitos e faz agendamentos das trocas dos items em conflitos
        # tem sido importante para melhorar a melhor máscara, porém explode a memória
        conflict_true = False
        for conflict in conflicts:            
            if mask[conflict[0]] != 0  and mask[conflict[1]] != 0: # faz duas agendas com um item ou outro ( ou seja uma troca dos itens em conflitos )
                if memory > RAM:              
                    c_first = np.copy(mask)
                    c_last = np.copy(mask)
                    c_first[conflict[0]] = 0   
                    c_last[conflict[1]] = 0          
                    mask_agenda.append(c_first) 
                    mask_agenda.append(c_last)
                conflict_true = True

        # Agenda inserções 
        if memory > RAM: 
            mask_agenda += Add(mask,items_weight,capacity_calc)

        # e finalmente o algoritimo testa se é a melhor solução no momento
        if conflict_true == False: 
            if value > best_solution_value and capacity_calc >= 0:
                gc.collect(generation=2)
                best_solution_value = value 
                best_solution_weight = mask.sum() 
                best_solution = np.zeros_like(mask)
                best_solution[np.nonzero(mask)] = 1  
                best_mask = np.copy(mask)
                # Melhor solução até agora? Agendamos alguma exploração sobre essa solução
                #mask_agenda.clear()
                mask_agenda += Add(mask,items_weight,capacity_calc)
                mask_agenda += Remove(mask)
                if DEBUG >= 1:
                    print ("Best {} Free {} Agenda size {} RAM {}".format(best_solution_value, capacity_calc, len(mask_agenda), memory ))

    
    
    ### Sanity check
    print (best_solution_value, best_solution_weight)
    value = 0
    weight = 0
    for i in items[best_solution > 0]:
        value += i[VALUE]
        weight += i[WEIGHT]
        print (i[VALUE], i[WEIGHT])
    for conflict in conflicts:
        if best_solution[conflict[0]] != 0  and best_solution[conflict[1]] != 0:
            raise Exception ("Sanity check error! Conflict detected!")
    if best_solution_weight != weight or best_solution_value != value or weight > capacity:
        raise Exception ("Sanity check error! Values don't match!")



    # prepare the solution in the specified output format
    output_data = str(best_solution_value) + '\n'
    output_data += ' '.join(map(str, best_solution))

    return output_data


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
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

