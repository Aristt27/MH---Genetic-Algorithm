import numpy as np
from itertools import groupby
from time import time

def all_equal(iterable):
    " Função que verifica se todos os elementos de uma lista são iguais, BEM RAPIDO"
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def get_horariomax(Data):
  
  t  = 47
  for C in Data:
    x = C[-1]
    if x < t:
      t = x


  return 46//t


def fitness(X, Instance, F_obj, verbose = False, penalty_check = False):

  """ Aplica a função objetivo e tambem penaliza X caso ocorra o seguinte:
  
  - Dias com mais de 46 intervalos;
  - Sobreposição de horários;
  - Salas sendo usadas pra multiplas especialidades;
  - Cirurgião em mais de uma cirurgia ao mesmo tempo;
  
  Data = (Data, Max_Rooms)
  Começando dando uma penalização de 10% da F_obj para cada uma das infrações (dualizando as restrições)
  A FAZER: 
  - Inserir penalização para cirurgião em dois lugares ao mesmo tempo(Help)
  - Inserir uma maior penalização para cirurgias no mesmo dia (quanto mais ultrapassa do limite, mais penaliza)(Feito)
  """

  penalty1     = 0 # Salas com mais de 46 intervalos
  penalty2     = 0 # Salas com mais de um tipo de cirurgia
  penalty3     = 0 # Cirurgiao em mais de um lugar, ao mesmo tempo, hmmm

        
  Maximum_day  = 2*len(X)
  Maximum_docs = Maximum_day

  Data, Max_Rooms = Instance 

  Dias_pen_12        = [[[] for j in range(Max_Rooms)] for i in range(Maximum_day)]
  Docs_pen_3         = [[[] for j in range(Maximum_day)] for i in range(Maximum_docs)]     

  max_days      = 0
  max_medicos   = 0

  time_interval = 2

  for idx, cirurgia in enumerate(X):

    cirurgia_dia           = cirurgia[0]
    cirurgia_sala          = cirurgia[1]

    if cirurgia_dia > max_days:

      max_days = cirurgia_dia
    
    if cirurgia_sala > Max_Rooms:

      Max_Rooms = cirurgia_sala
    
    cirurgia_medico        = Data[idx][4]
    
    if cirurgia_medico > max_medicos:
        
      max_medicos = cirurgia_medico

    cirurgia_especialidade = Data[idx][3]
    cirurgia_duracao       = Data[idx][-1] + time_interval
    
    
    Dias_pen_12[cirurgia_dia - 1][cirurgia_sala - 1].append([cirurgia_especialidade, cirurgia_duracao])
    Docs_pen_3[cirurgia_medico - 1][cirurgia_dia - 1].append(cirurgia_duracao)

  
  Dias_pen_12 = Dias_pen_12[:max_days]
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
        
  for doc in Docs_pen_3:
    
    doc = doc[:max_days]
    
    for diazinho in doc:
      pen_3_weight = 48 - sum(diazinho)
        
      if pen_3_weight < 0:
        
        penalty3 += ((pen_3_weight)**2)/2
          
    
  if penalty_check == True:
        
    if verbose == True:
            
      if penalty1:
        print(" Essa solução não respeita a restrição que o dia só tem 24h e ultrapassa por " + str(penalty1))
                
      if penalty2:
        print("Essa solução não respeita a restrição que uma sala só pode ser usada para uma especialidade")

      if penalty3:
        print("Essa solução possui uma disposição impossivel para algum cirurgião")
        
      return penalty1, penalty2, penalty3
    
  x_val = F_obj(X, Data)
    
  return x_val*(1+ ((penalty1) + (penalty3)+ penalty2)) 


def crossover(ancestors, pop_inicial, cut_type = "ONE_CUT"):
    """ \alpha -> probabilidade de cruzamento

    Considerando x = [[1,2,3],[3,2,1],[1,2,3],[1,2,3]] e y = [[3,2,1],[1,2,3],[3,2,1],[3,2,1]]

    Quais as chances que queremos de obter [[1,2,3],[1,2,3],[1,2,3],[1,2,3]]? 
    
    Cut_type = "ONE_CUT" or "MULTI_CUT"
    
    """
    
    if cut_type not in ["ONE_CUT", "MULTI_CUT"]:
      cut_type == "ONE_CUT"

    i        = 0
    len_ance = len(ancestors)
    genes    = len(ancestors[0])
    
    aux_bias = [i for i in range(len_ance)]  # Isso daqui controla a probabilidade do crossover, 
    fit_bias = []                            # Talvez teha que ajustar isso para ser maleável.
    for i in aux_bias:
      fit_bias += aux_bias[i:]
    lfb      = len(fit_bias)

    offspring = []
    
    while len(offspring) < pop_inicial - len_ance:
        
      idx1 = fit_bias[np.random.randint(lfb)]
      idx2 = fit_bias[np.random.randint(lfb)]  
        
      if idx1 == idx2:
        while idx1 == idx2:
          idx1 = fit_bias[np.random.randint(lfb)]
          idx2 = fit_bias[np.random.randint(lfb)]
        
      else: # caso contrário, Cross over!!

        if cut_type == "ONE_CUT":

            break_point = np.random.randint(1, genes)

            ## Verificar a necessidade de usar deepcopy aqui...
            ancestor        = ancestors[idx1]
            ancestor_target = ancestors[idx2]

            ances = ancestor[:break_point]
            tor   = ancestor[break_point:]

            tar   = ancestor_target[:break_point]
            get   = ancestor_target[break_point:]

            offspring.append(tar   +  tor)
            offspring.append(ances +  get)
            offspring.append(ancestor_target)
            offspring.append(ancestor)

        if cut_type == "MULTI_CUT":

            n_break_points = np.random.randint(1, genes//2)
            
            ancestor        = ancestors[idx1]
            ancestor_target = ancestors[idx2]

            for _ in range(n_break_points):
            ## Verificar a necessidade de usar deepcopy aqui...

                break_point = np.random.randint(1, genes)



                ances = ancestor[:break_point]
                tor   = ancestor[break_point:]

                tar   = ancestor_target[:break_point]
                get   = ancestor_target[break_point:]

            offspring.append(tar   +  tor)
            offspring.append(ances +  get)
            offspring.append(ancestor_target)
            offspring.append(ancestor)
    return ancestors, offspring

def faz_torneios(individuos, fos, n_torneios, size_torneios):
    # define quem vai participar dos torneios
    participantes = np.random.randint(0, len(individuos), size=(n_torneios * size_torneios))

    # pega as FO's dos participantes e divide nos torneios
    torneios = fos[participantes].reshape(n_torneios, size_torneios)

    # divide os participantes nos torneios
    participantes = participantes.reshape(n_torneios, size_torneios)

    # determina os vencedores de cada torneio
    vencedores = [i[j] for i,j in zip(participantes, torneios.argmin(1))]

    # elimina da lista de individuos e FO's todos os não vencedores
    return np.vstack([vencedores, individuos[vencedores]]).T

def crossover2(ancestors, indices, fit_idx_vector, pop_inicial, cut_type = "ONE_CUT"):
    """ \alpha -> probabilidade de cruzamento
    Considerando x = [[1,2,3],[3,2,1],[1,2,3],[1,2,3]] e y = [[3,2,1],[1,2,3],[3,2,1],[3,2,1]]
    Quais as chances que queremos de obter [[1,2,3],[1,2,3],[1,2,3],[1,2,3]]? 
    
    Cut_type = "ONE_CUT" or "MULTI_CUT"
    
    """
    
    if cut_type not in ["ONE_CUT", "MULTI_CUT"]:
      cut_type == "ONE_CUT"

    i        = 0
    len_ance = len(ancestors)
    genes    = len(ancestors[0])

    offspring = []

    n_torneios = 2*(pop_inicial - len_ance)
    size_torneios = 3
    A = np.array(fit_idx_vector, dtype=object)
    B = A[:, 1]
    C = A[:, 0]
    vencedores_torneio = faz_torneios(B,C,n_torneios,size_torneios)
    
    while len(offspring) < pop_inicial - len_ance:
        
      aux = np.random.choice(len(vencedores_torneio),2,replace = False)

      idx1, winner1 = vencedores_torneio[aux[0]]
      idx2, winner2 = vencedores_torneio[aux[1]]
        
      if idx1 == idx2:
        offspring.append(winner1)          
        
      else: # caso contrário, Cross over!!

        if cut_type == "ONE_CUT":

            break_point = np.random.randint(1, genes)

            ## Verificar a necessidade de usar deepcopy aqui...
            ancestor        = winner1
            ancestor_target = winner2

            ances = ancestor[:break_point]
            tor   = ancestor[break_point:]

            tar   = ancestor_target[:break_point]
            get   = ancestor_target[break_point:]

            offspring.append(tar   +  tor)
            offspring.append(ances +  get)
            offspring.append(ancestor_target)
            offspring.append(ancestor)

        if cut_type == "MULTI_CUT":

            n_break_points = np.random.randint(1, genes//2)
            
            ancestor        = winner1
            ancestor_target = winner2

            for _ in range(n_break_points):
            ## Verificar a necessidade de usar deepcopy aqui...

                break_point = np.random.randint(1, genes)



                ances = ancestor[:break_point]
                tor   = ancestor[break_point:]

                tar   = ancestor_target[:break_point]
                get   = ancestor_target[break_point:]

            offspring.append(tar   +  tor)
            offspring.append(ances +  get)
            offspring.append(ancestor_target)
            offspring.append(ancestor)
    return ancestors, offspring


def mutation(offspring,Max_Rooms,β):
    
    'Ocurrs a random mutation in a random collection of genes of different cells over a given offspring ~ what is ϵ?'
    """Para cada unidade em offsprig, existe uma probabilidade $\beta$ para ocorrer 1 troca entre seus genes. 
     E uma probabilidade $\varepslon$ de dar +=1 no dia ou na sala de um gene.
     
     Isso ta uma loucura. 
     
     Com probabilidade β ele escolhe o filho para mutar
     
     """
    
    mutated_offspring = []
    
    for child in offspring:
        
        altered_child = []
        
        if np.random.rand(1) < β: ## Caso ele ganhe de β, ele vai ser mutado.
                
            for idxs, gene in enumerate(child):
                
                altered_gene = []
                
                for idx, g in enumerate(gene):
                    
                    q = np.random.rand(1)
                    
                    if q < 0.3:
                        
                        if idx == 1:
                            
                            if g > 1:
                                mg = max(1, g + 2*np.random.randint(0,2) - 1)
                                altered_gene.append(min(mg, Max_Rooms))
                            if g == 1:
                                altered_gene.append(min(2, Max_Rooms))
                        else:
                            if g > 1:
                                altered_gene.append(max(1, g + 2*np.random.randint(0,2) - 1))
                            if g == 1:
                                altered_gene.append(2)
                    else:
                        
                        altered_gene.append(g)
                
                altered_child .append(altered_gene)
                
            mutated_offspring .append(altered_child)

                        
        else:
    
            mutated_offspring.append(child) # Se ele perder de β, ele não vai ser mutado.
    
    return mutated_offspring


def select_ancestors(fit_idx_vector, elite_cut, n_sortudos):
    
    elite           = [idx[1] for idx in fit_idx_vector[-elite_cut:]]
    sortudos        = []
    Max_Sortudo     = len(fit_idx_vector) - elite_cut
    
    indices         = [i for i in range(len(fit_idx_vector))][-elite_cut:]
    
    fit_idx_vector = fit_idx_vector[:-elite_cut] 
    for i in range(n_sortudos):
        
        sortudo_idx = np.random.randint(Max_Sortudo)
        sortudos.append(fit_idx_vector[sortudo_idx][1])

        fit_idx_vector = fit_idx_vector[:sortudo_idx] + fit_idx_vector[sortudo_idx+1:]
        Max_Sortudo -= 1
        
        indices.append(sortudo_idx)
    return sortudos+elite, indices

def Genetic_Algorithm(Instancia, F_obj, params, stop_criteria,Presolve = True, Verbose = True):

  """ Teremos que Data é da forma de Toy2 com informaçoes sobre num de salas etc 
      f_obj será utilizada como fitness provavelmente, e possui entradas:  [Cirurgias, Data, PenaltyTable]
      params são os parãmetros do algoritimo genético:  params = [\alpha,...?] 
      
      Max_Rooms = Numero de salas vem de onde??  (Razoavel supor que o máximo é o numero de  especialidades? acho que nao)
      Lembrete que Data é a matriz na forma:
      Cirurgia  k  - Prioridade - Dias_Espera - Especialidade - Cirurgião - Duração(t_c)
      params = pop_inicial, elite_cut, lucky_cut, LimitDay, generations, Cut_type, β
      
      Cut_type = "ONE_CUT" or "MULTI_CUT"
      
      """

  # primeiro calculamos o numero de cirurgias: Len(Data) vs Data[-1][0]  (por enquanto Data = Toy2)

  pop_inicial, elite_cut, lucky_cut, LimitDay, generations, Cut_type, β = params  # params assessment  (Max_Rooms é o número de salas).


  stop_len, Zt, tol = stop_criteria
    
  if elite_cut < 1:
    
    elite_cut = int(((100*elite_cut)*pop_inicial)//100)

  if lucky_cut < 1:
    
    lucky_cut = int(((100*lucky_cut)*pop_inicial)//100)
    
  Data, Max_Rooms = Instancia
    
  Cs         = len(Data)
  HorarioMax = get_horariomax(Data)

  fit_idx_vector = []

  t0  = time()
    
  for i in range(pop_inicial):
    # Aqui vamos sortear um dia, uma sala e um horário para cada cirurgia. Primeiro vamos sortear um dia para cada cirurgia
    Max_Days = np.random.randint(2,LimitDay)

    Xi  = [[np.random.randint(1,Max_Days), np.random.randint(1, Max_Rooms+1), np.random.randint(1,HorarioMax+1)] for j in range(Cs)]


    # Falta verificarmos as salas bem como horários sobrepostos (acho que podemos colocar isso na função fitness, penalizando exponencialmente caso isso aconteça)

    # Para maximizar as chances de que a solução seja viável, como fazer? Talvez possamos confiar cegamente na função objetivo pra gerar uma população boa no final....

    fit_idx_vector.append([fitness(Xi, Instancia, F_obj), Xi])

  fit_idx_vector.sort(reverse = True)
    
  ancestors, indices = select_ancestors(fit_idx_vector, elite_cut, lucky_cut)

  evolution = [ancestors]
    
  evolution = []
  stop_criteria = [0]*stop_len
  t = time() - t0

  for generation in range(generations):
      t0 = time()
      if Verbose == True:
        
          print(" Estamos gerando a geração " + str(generation + 1 ) + " de " + str(generations), "a ultima demorou: {:.2f}".format(t)+"s")
        
      if generation %2 == 1:
        
        recombinant_ancestors = crossover(ancestors, pop_inicial, Cut_type)
      else:
        recombinant_ancestors = crossover2(ancestors, indices ,fit_idx_vector, pop_inicial, Cut_type)
        
      ancestors, offspring  = recombinant_ancestors 

      #abcde
        
      mutated_offspring     = mutation(offspring, Max_Rooms,β)
    
      save_fit       = [fit_idx_vector[idc] for idc in indices]
      fit_idx_vector = [[fitness(Xi, Instancia, F_obj), Xi] for Xi in mutated_offspring]
      fit_idx_vector = fit_idx_vector + save_fit
        
      fit_idx_vector.sort(reverse = True)
    
      ancestors, indices      = select_ancestors(fit_idx_vector, elite_cut, lucky_cut)
      evolution.append(ancestors)
      
      lindices = indices[:]
      lindices.sort()
      L = [fit_idx_vector[ifx] for ifx in lindices][-Zt:]
      W = np.array(L, dtype=object).T[0]
      avrg = sum(W)/Zt
      best = fit_idx_vector[-1]
      
      stop_criteria[generation%stop_len] = abs(avrg - best[0]) <= tol
      
      if sum(stop_criteria) == stop_len:
        
        print(" ")
        print(" Algoritmo encerrou devido ao criterio de parada mágico ")
        print(" ")
        
        return evolution
    
        
      if fit_idx_vector[-1][0] < 0:
        
        print(" ")
        print(" Deu negativo, arruma a fitness ")
        

        
        return evolution

      t = time() - t0

  return evolution