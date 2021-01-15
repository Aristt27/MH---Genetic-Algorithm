import numpy as np
import random
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

        
  Maximum_day  = len(X)
  Maximum_docs = Maximum_day

  Data, Max_Rooms = Instance 

  Dias_pen_12        = [[[] for j in range(Max_Rooms)] for i in range(Maximum_day)]
  Docs_pen_3         = [[[] for j in range(Maximum_day)] for i in range(Maximum_docs)]     

  max_days      = 0
  max_medicos   = 0

  time_interval = 2

  for idx, cirurgia in enumerate(X):

    #print(idx,cirurgia)
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


def crossover(ancestors, pop_inicial, alpha, cut_type = "ONE_CUT"):
    """ \alpha é approx a probabilidade de crossover
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
    
    nonrec    = [] # Indices de quem nao mudou
    rec_idxs  = [] # Indices de quem mudou, para recalcular a FO
    offspring = []
    
    while len(offspring) < pop_inicial - len_ance:
        
      idx1 = fit_bias[np.random.randint(lfb)]
      idx2 = fit_bias[np.random.randint(lfb)]  
      
      if np.random.rand(1) < alpha:
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

            
              offlen = len(offspring)
              rec_idxs.append(offlen)
              rec_idxs.append(offlen+1)
              offspring.append(tar   +  tor)
              offspring.append(ances +  get)

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
                
                offlen = len(offspring)
                rec_idxs.append(offlen)
                rec_idxs.append(offlen+1)
                
                offspring.append(tar   +  tor)
                offspring.append(ances +  get)
      else:
        offlen = len(offspring)
        nonrec.append([offlen, idx1])
        nonrec.append([offlen+1, idx2])
        offspring.append(ancestors[idx1])   
        offspring.append(ancestors[idx2])
            
    return ancestors, offspring, rec_idxs, nonrec
        

def mutation(offspring,Max_Rooms,β):
    
    'Ocurrs a random mutation in a random collection of genes of different cells over a given offspring ~ what is ϵ?'
    """Para cada unidade em offsprig, existe uma probabilidade $\beta$ para ocorrer 1 troca entre seus genes. 
     E uma probabilidade $\varepslon$ de dar +=1 no dia ou na sala de um gene.
     
     Isso ta uma loucura. 
     
     Com probabilidade β ele escolhe o filho para mutar
     
     """
    Prob              = (β*3)/2
    nonmut            = []
    mut_idxs          = []
    mutated_offspring = []
    
    for child in offspring:
        
        altered_child = []
        
        if np.random.rand(1) < Prob: ## Caso ele perca de β, ele vai ser mutado.
                
            for idxs, gene in enumerate(child):
                
                altered_gene = []
                
                for idx, g in enumerate(gene):
                    
                    q = np.random.rand(1)
                    
                    if q < 0.3:
                        
                        if idx == 1:
                            
                            if g > 1 or g < 1:
                                mg = max(1, g + 2*np.random.randint(0,2) - 1)
                                altered_gene.append(min(mg, Max_Rooms))
                            if g == 1:
                                altered_gene.append(min(2, Max_Rooms))
                        else:
                            if g > 1 or g < 1:
                                altered_gene.append(max(1, g + 2*np.random.randint(0,2) - 1))
                            if g == 1:
                                altered_gene.append(2)
                    else:
                        
                        altered_gene.append(g)
                
                altered_child .append(altered_gene)
                
            mut_idxs.append(len(mutated_offspring))    
            mutated_offspring .append(altered_child)

                        
        else:
            lmo = len(mutated_offspring)
            
            nonmut.append([lmo])
    
            mutated_offspring.append(child) # Se ele perder de β, ele não vai ser mutado.
    
    return mutated_offspring, mut_idxs, nonmut


def select_ancestors(fit_idx_vector, elite_cut, n_sortudos):
    
    elite           = [idx[1] for idx in fit_idx_vector[-elite_cut:]]
    elite_fit       = [idx[0] for idx in fit_idx_vector[-elite_cut:]]
    
    sortudos        = []
    sortudos_fit    = []
    
    Max_Sortudo     = len(fit_idx_vector) - elite_cut
    sortudos_idxs = random.sample(range(Max_Sortudo), n_sortudos)

    sortudos_idxs.sort()
    for sidx in sortudos_idxs:
        sortudos.append(fit_idx_vector[sidx][1])
        sortudos_fit.append(fit_idx_vector[sidx][0])
    
    soeli = sortudos+elite
    soeli_fit = sortudos_fit+elite_fit


    return soeli, soeli_fit


#entrada com a instancia importada do csv, maximo de dias, salas (5), intervalos de tempo (48)
def aloca_cirurgias(instancia,  n_sala, n_dia = 5, max_dia = 48):
    # cria uma copia das instancias e dá um shuffle
    instancia = np.array(instancia)
    instancia[:,-1] +=2 
    instancias_alteradas = instancia[:]
    np.random.shuffle(instancias_alteradas)

    # matrizes auxiliares pra dividir as cirurgias nas salas
    cubao = np.zeros((n_dia, n_sala, max_dia))
    especialidades = np.zeros((n_dia, n_sala))

    # saida: cirurgia, dia, sala, hora
    cirurgias = []


    for prioridade in range(1, 5):
        for cirurgia in instancias_alteradas[instancias_alteradas[:, 1] == prioridade]:
            # pega informacoes das cirurgias
            codigo = cirurgia[0]
            especialidade = cirurgia[3]
            duracao = cirurgia[-1]

            # variavel para parar o for quando alocar a cirurgia
            c = False

            for i in range(n_dia):
                for j in range(n_sala):
                    # se a sala/dia ta vazia
                    if especialidades[i, j] == 0:
                        # ocupa a sala com aquela especialidade
                        especialidades[i, j] = especialidade

                        # ocupa os horarios com aquela cirurgia
                        cubao[i, j, :duracao] = codigo
                        cirurgias.append([codigo, i+1, j+1, 0])
                        c = True
                        break

                    # se a sala/dia tem outra especialidade, pula
                    elif especialidades[i, j] != especialidade:
                        continue

                    # caso contrario, a sala/dia tem a mesma especialidade da cirurgia
                    else:
                        #verifica se a cirurgia cabe naquela sala/dia
                        ocupados = sum(cubao[i, j, :] > 0)
                        if ocupados + duracao <= max_dia:
                            # ocupa os horarios com aquela cirurgia
                            cubao[i, j, ocupados:ocupados+duracao] = codigo
                            cirurgias.append([codigo, i+1, j+1, ocupados])
                            c = True
                            break
                # se a cirurgia conseguiu ser alocada naquel dia, pula pra proxima
                if c:
                    break
            #para cirurgias nao agendadas        
            if c == False: 
                cirurgias.append([codigo, 6, -1, -1])
    #SAIDA: cirurgia - dia - sala - t0            
    resultado = np.array(cirurgias)
    
    #SAIDA: dia- sala - t0 com cirurgias em ORDEM
    return resultado[resultado[:,0].argsort()][:,1:].tolist()


def Genetic_Algorithm(Instancia, F_obj, params, stop_criteria,Presolve = True, Verbose = True):

  """ 
      Instancia contém a dupla (Data, Max_Rooms)
            (Max_Rooms é o número de salas).

      Lembrete que Data é a matriz na forma:
      Cirurgia  k  - Prioridade - Dias_Espera - Especialidade - Cirurgião - Duração(t_c)
      
      params = pop_inicial_total, elite_cut, lucky_cut, generations, alpha, Cut_type, β  # params assessment  
      
      pop_inicial_total = (greedy_pop, random_pop)

      Cut_type = "ONE_CUT" or "MULTI_CUT"
      
      """

  # primeiro calculamos o numero de cirurgias: Len(Data) vs Data[-1][0]  (por enquanto Data = Toy2)

  pop_inicial_total, elite_cut, lucky_cut, generations, alpha, Cut_type, β = params  # params assessment  (Max_Rooms é o número de salas).

  greedy_pop, random_pop = pop_inicial_total
  
  pop_inicial = greedy_pop + random_pop
  

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
  for i in range(random_pop):
    Xi  = [[np.random.randint(1,6), np.random.randint(1, Max_Rooms+1), np.random.randint(1,HorarioMax+1)] for j in range(Cs)]

    fit_idx_vector.append([fitness(Xi, Instancia, F_obj), Xi])

  for i in range(greedy_pop):
    Xi  = aloca_cirurgias(Data,  Max_Rooms)

    fit_idx_vector.append([fitness(Xi, Instancia, F_obj), Xi])

  fit_idx_vector.sort(reverse = True)
    
  ancestors, ans_fits = select_ancestors(fit_idx_vector, elite_cut, lucky_cut)
  evolution = [ancestors[:]]
    
  stop_criteria = [0]*stop_len
  t = time() - t0

  for generation in range(generations):
      t0 = time()
      if Verbose == True:
        
          print(" Estamos gerando a geração " + str(generation + 1 ) + " de " + str(generations), "a ultima demorou: {:.2f}".format(t)+"s")

      recombinant_ancestors = crossover(ancestors, pop_inicial, alpha, Cut_type)
        
      ancestors, offspring, rec_idxs, nonrec  = recombinant_ancestors 

      nonrec_dict = {mn: nm for mn, nm in nonrec}
        
      mutated_offspring, mut_idxs, nonmut  = mutation(offspring, Max_Rooms,β)
      
      fit_idx_vector = [[afit, ancs] for ancs, afit in zip(ancestors, ans_fits)]
    
      for midx, mXi in enumerate(mutated_offspring):
        if midx in mut_idxs:
          fit_idx_vector.append([fitness(mXi, Instancia, F_obj), mXi])
        elif midx in rec_idxs:
          fit_idx_vector.append([fitness(mXi, Instancia, F_obj), mXi])
        else:
          indc = nonrec_dict[midx]
          #print(nonrec_dict, midx)
          #print(fitness(mXi, Instancia, F_obj), ans_fits[indc], 'cueio')
          fit_idx_vector.append([ans_fits[indc], mXi])
          #fit_idx_vector.append([fitness(mXi, Instancia, F_obj), mXi])
            
      fit_idx_vector.sort(reverse = True)
          
      ancestors, ans_fits      = select_ancestors(fit_idx_vector, elite_cut, lucky_cut)
      evolution.append(ancestors[:])
     
      ans_fits.sort(reverse = True)
      L = ans_fits[-Zt:]
      #print(L)
      avrg = sum(L)/Zt
      best = L[-1]
      stop_criteria[generation%stop_len] = abs(avrg - best) <= tol
      
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
