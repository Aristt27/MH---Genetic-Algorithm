import numpy as np
from Objective_function import funcao_objetivo as F_obj
from GA_fitness import fitness

def get_tempo(room):
  j = 0
  for i in room:
    if (i != -2): 
      j += 1
  return j


def solution_visualize(X, Instance, verbose = True):
  """ Retorna um quadrado, possivelmente bonitinho, com as informações sobre salas ocupadas e etc 
  
  A meta é transformar X= [[1,1,1],[1,1,8],[2,1,1],[2,1,11],[3,1,1],[4,1,1],[3,1,13],[4,1,17]] (Dia-sala-t0) em 
  
     [[1, 1, 1, 1, 1, -1, -1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [3, 3, 3, 3, 3, 3, 3, 3, -1, -1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, -1, -1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, -1, -1, 8, 8, 8, 8, 8, 8, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        
     Podemos ganhar memória colocando um -2 ao inves de uma sequencia de zeros pra definir fechamento da sala no dia ( ou o fechamento do dia) essa implementacao ainda nao assume multiplas salas.
     para asssumir multiplas salas cada dia pode ser uma lista contendo as salas disponiveis X = [D[S1,S2], D2[S1,S2] e cada sala terá seus intervalos de tempo.

     Talvez seja melhor ainda retornarmos:

     [[1,-1,2,-2]
      [3,-1,4,-2]
      [5,-1,7,-2]
      [6,-1,8,-2]]

      Ignorando a duração de cada cirurgia, dado que se uma cirurgia começou ela nao pode parar entao essa informacao acaba sendo pouco relevante (bem como T0).
      T0 só é importante pra saber a ordem que as cirurgias aparecem, para isso a gente pode simplismente dar um numero pra elas ao inves de calcularmos o horario certinho.
      
      COMO NA F_OBJ NAO IMPORTA A ORDEM DAS CIRURGIAS NEM ISSO PARECE IMPORTANTE (MUDAR A F_OBJ)
      
      Com isso, o X passaria a ser uma lista da forma (Dia,sala,ordem), ex:
      X = [[1,1,1],[1,1,2],[2,1,1],[2,1,2],[3,1,1],[4,1,1],[3,1,2],[4,1,2]] """

     # primeiro eu preciso saber quantos dias eu tenho na solução (obtido pelo valor máximo na primeira coluna de X)

  Data, aux = Instance
  
  dia      = 0
  sala     = 1
  ordem    = 2

  max_days  = 0
  max_rooms = 0

  time_discret  = 46       # intervalos em um dia;
  time_interval = 2        # intervalo entre as cirurgias;

  blocos = []
  ans    = []

  if verbose:
    print("calculando o número de dias da solução")

  for idx, cirurgia in enumerate(X):
    cirurgia_dia  = cirurgia[dia]
    cirurgia_sala = cirurgia[sala]

    if cirurgia_dia > max_days:

      max_days = cirurgia_dia
    
    if cirurgia_sala > max_rooms:

      max_rooms = cirurgia_sala

    duration   = Data[idx][-1]   # a ultima entrada de data[idx] possui a duracao da cirurgia
    blocos.append([cirurgia_dia, cirurgia_sala, [idx+1]*duration + [-1]*time_interval]) # ja coloco os numeros de intervalo apos a cirurgia (menos quando é a ultima mas ai é detalhe rs)

  if verbose:
    print("O numero de dias são " + str(max_days), "o de salas são " + str(max_rooms))

  for day in range(max_days):
    diax = []
    for room in range(max_rooms):
      roomx = []
      for bloco in blocos:
        if bloco[0] == day+1:
          if bloco[1] == room+1:

            roomx += bloco[2]   #eu coloco a duração na sala

      diax += [roomx[:-2] + [-2]]

    ans.append(diax)

  if verbose == True:
    for an in ans:
     print(an)
    print(" ")
    print(" O Valor da Função objetivo é de: " + str(F_obj(X, Data)))
    print(" O Valor da Fitness é de: " +str(fitness(X,Instance)))
    print(fitness(X,Instance, verbose = True, penalty_check = True))
    print(" Legenda: ")
    print("-2 significa final do turno na sala, naquele dia.")
    print("-1 significa intervalo entre as duas cirurgias.")
    print(" ")

    for idx, day in enumerate(ans):
      print(" No dia " + str(idx +1)+ ":")
      for idx2, room in enumerate(day):
        print(" Tivemos na sala " + str(idx2 + 1)+ ": " + str(get_tempo(room)))

  return ans
