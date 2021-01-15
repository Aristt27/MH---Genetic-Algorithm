### Função objetivo decidida pela amanda e cia

import numpy as np

DefaultTable = [[90,3],[20,15],[8,60],[3,365]]

### Funções Auxiliares (Controlam as Estruturas de dados)

def get_wc(idx, Data):
    #Tempo de espera
    return int(Data[idx][2])

def get_pc(idx, Data):
    #prioridade
    return int(Data[idx][1])

def get_penalty(p_c, PenaltyTable):
    #Busca a penalidade e o tempo limite da cirurgia, em função de sua prioridade
    return PenaltyTable[p_c - 1]

def get_dia(idx, Cirurgias):
    #Dia agendado para a cirurgia de indice dado
    return Cirurgias[idx][0]


def funcao_objetivo(Cirurgias, Data, PenaltyTable = DefaultTable):

  """ Input(Cirurgias): É a solução do problema dada pela forma: X = [[Dia,Sala,T0], ..., [Dia, Sala, T0]]
      Data : É o quadro das informações necessárias para obter valores para as variaveis de decisao e os coeficientes utilizados (A meta é diminuir essa entrada, ao máximo).
  Lembrete que toda DATA que temos é a matriz na forma:
  Cirurgia  k  - Prioridade - Dias_Espera - Especialidade - Cirurgião - Duração(t_c)
  Função objetiva dada pela fórmula da amanda.
  wc = Tempo de Espera;
  d  = dia do agendamento;
  xi_p = fator de penalidade (en função da prioridade) para o não agendamento na semana;
  l_p = prazo limite de atendimento (dias) (em função da prioridade);
  Observe que para a FO, não importa o tempo que a cirurgia foi marcada...
  Variaveis de decisão::
  x_cstd:  Cirurgia, prioridade agendada na semana no tempo t;
  z_c   :  Cirurgia não agendada na semana
  V_c   :  Cirurgia com prazo limite vencido;
  p1    :  Cirurgia com prioridade 1 não atendida na segunda-feira.
  
  """

  objective = 0

  for idx, cirurgia in enumerate(Cirurgias):

    w_c   = get_wc(idx, Data)   
    p_c   = get_pc(idx, Data) 

    xi_p, l_p  = get_penalty(p_c, PenaltyTable)

    d_p   = get_dia(idx, Cirurgias)

    if p_c == 1 and d_p > 1: ## Caso prioridade 1 não tenha sido atendida no primeiro dia(segunda feira);

      objective += (10*(w_c + 2))**(d_p) 
    
    if d_p == False: # Caso a cirurgia não tenha sido marcada

      objective += (xi_p)*((w_c + 7))**2 
      
      if d_p + w_c > l_p: #Caso a cirurgia tenha vencido
        
        objective += (xi_p)*(w_c + 9 - l_p)**2 

    if True: #Caso a cirurgia tenha sido marcada

      objective += (w_c + 2 + d_p)**2
                    
      if d_p + w_c > l_p:  #Caso a cirurgia estiver vencida

        objective += (w_c + 2 + d_p - l_p)**2

  return objective
