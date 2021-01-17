import numpy as np
from itertools import groupby
from Objective_function import funcao_objetivo as F_obj
from GA_viola_medico import viola_medico, all_sol_fixer

def all_equal(iterable):
    " Função que verifica se todos os elementos de uma lista são iguais, BEM RAPIDO"
    g = groupby(iterable)
    return next(g, True) and not next(g, False)

def fitness(X, Instance, verbose = False, penalty_check = False):

  """ Aplica a função objetivo e tambem penaliza X caso ocorra o seguinte:
  
  - Dias com mais de 46 intervalos;
  - Sobreposição de horários;
  - Salas sendo usadas pra multiplas especialidades;
  - Cirurgião em mais de uma cirurgia ao mesmo tempo;
  
  Data = (Data, Max_Rooms)
  Começando dando uma penalização de 100% da F_obj para cada uma das infrações (dualizando as restrições)
  A FAZER: 
  - Inserir penalização para cirurgião em dois lugares ao mesmo tempo(Help)
  - Inserir uma maior penalização para cirurgias no mesmo dia (quanto mais ultrapassa do limite, mais penaliza)(Feito)
  """

  penalty1     = 0 # Salas com mais de 46 intervalos
  penalty2     = 0 # Salas com mais de um tipo de cirurgia
  penalty3     = 0 # Cirurgiao em mais de um lugar, ao mesmo tempo, hmmm

        
  Maximum_day  = len(X)
  Maximum_docs = Maximum_day

  Data, Max_Rooms = Instance 

  Dias_pen_12        = [[[] for j in range(Max_Rooms)] for i in range(Maximum_day)]
  Docs_pen_3         = [[[] for j in range(Maximum_day)] for i in range(Maximum_docs)]     

  max_medicos   = 0

  time_interval = 2

  for idx, cirurgia in enumerate(X):

    cirurgia_dia           = cirurgia[0]
    cirurgia_sala          = cirurgia[1]
    
    cirurgia_medico        = Data[idx][4]
    
    if cirurgia_medico > max_medicos:
        
      max_medicos = cirurgia_medico

    cirurgia_especialidade = Data[idx][3]
    cirurgia_duracao       = Data[idx][-1] + time_interval
    
    
    Dias_pen_12[cirurgia_dia - 1][cirurgia_sala - 1].append([cirurgia_especialidade, cirurgia_duracao])
    Docs_pen_3[cirurgia_medico - 1][cirurgia_dia - 1].append(cirurgia_duracao)

  
  Dias_pen_12 = Dias_pen_12[:5]
  Docs_pen_3  = Docs_pen_3[:max_medicos]

  for dia in Dias_pen_12:  # Aqui eu penalizo por 1 e 2
    
    for room in dia:  # Temos que checar pra cada sala se ela respeita a especialidade [0] e o horario
    
      C = room
      C = np.array(C).T
      
      if len(C) > 0:
        if all_equal(C[0]) == False: # Especialidades
          penalty2 = 1
    
        pen_1_weight = 48 - sum(C[1])
    
        if pen_1_weight < 0:    # Horário
          penalty1 += ((pen_1_weight)**2)/2
  
  if Max_Rooms > 2:
    X = all_sol_fixer(Data, X)    # Arruma T0's  
  penalty3, penalty4 = viola_medico(Data,X)

  #Verifica se os médicos estão trabalhando em mais de um lugar ao mesmo tempo      
  
  if penalty_check == True:
        
    if verbose == True:
            
      if penalty1:
        print(" Essa solução não respeita a restrição que o dia só tem 24h e ultrapassa por " + str(penalty1))
                
      if penalty2:
        print("Essa solução não respeita a restrição que uma sala só pode ser usada para uma especialidade")

      if penalty3:
        print("Essa solução possui uma disposição impossivel para algum cirurgião")

      if penalty4:
        print("Essa solução possui algum cirurgião trabalhando mais que 26 tempos em um dia")
        
      return penalty1, penalty2, penalty3, penalty4
    
  x_val = F_obj(X, Data)
    
  return x_val * float(1 + 10 * (penalty1 + penalty2 + penalty3 + penalty4)), X
