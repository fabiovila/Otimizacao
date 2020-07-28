import cvxpy as cp
import numpy as np


# Dados de entrada do problema

QUANTIDADE = 10000

Valores = np.random.uniform(1,100, QUANTIDADE)
Pesos = np.random.uniform(1,200, QUANTIDADE)

Capacidade_Mochila = 5000

# Variaveis de decisão
# Cada Item Xi terá valor 1 se estiver na mochila ou 0 se estiver fora
# cp.Variable cria uma variável no CVX ( não confunda cp com np ) do tipo boolean do tamanho da quantidade de itens

Xi = cp.Variable((Valores.size), boolean = True)

# Constraints do problema

# A soma total dos pesos dos itens escolhidos por Xi devem ser igual ou menor que a capacidade da mochila                
constraints = [ Xi @ Pesos <= Capacidade_Mochila ]

# Gera conflitos entre os itens. Itens que não podem estar na mesma mochila
for i in range(int(QUANTIDADE / 2)):
    a = np.random.randint(0,QUANTIDADE)
    b = np.random.randint(0,QUANTIDADE)
    constraints.append(Xi[a] + Xi[b] <= 1)
                                                 
                          
# Tambem pode ser escrito com o mesmo resultado como:
#constraints = [ cp.sum( cp.multiply (Xi, Pesos ) ) <= Capacidade_Mochila ]

# O Objetivo do problema
# é maximizar os valores na mochila
objective = cp.Maximize( Xi @ Valores )

# finalmente chamamos o solver com verbose para acompanhar o progesso
# e a execução máxima de 1hr
prob = cp.Problem(objective, constraints)              
prob.solve(solver=cp.CBC,verbose=True, maximumSeconds = 1 * 60 * 60)  
     
    
    
print("Status          : ", prob.status)
print("Valor encontrado: ", prob.value)
print("Valor de Xi     : ", Xi.value)
