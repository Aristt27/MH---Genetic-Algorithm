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

        
  Maximum_day  = len(X)
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
    
    
    Dias_pen_12[cirurgia_dia - 1][cirurgia_sala - 1]      += [[cirurgia_especialidade, cirurgia_duracao]]  
    Docs_pen_3[cirurgia_medico - 1][cirurgia_dia - 1]     += [cirurgia_duracao]

  
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


def crossover(ancestors, α, cut_type = "ONE_CUT"):
    """Synapsys two ~randomly~ different ancestors chromossomes ~ parallel or not (?) α,δ ??
    
    \alpha -> probabilidade de cruzamento

    Considerando x = [[1,2,3],[3,2,1],[1,2,3],[1,2,3]] e y = [[3,2,1],[1,2,3],[3,2,1],[3,2,1]]

    Primeiro eu transformo em x = [1,2,3,3,2,1,1,2,3,1,2,3] com alguma funcao magica.

    Depois de combinar eu retorno para a forma matricial.

    Quais as chances que queremos de obter [[1,2,3],[1,2,3],[1,2,3],[1,2,3]]? 
    
    Cut_type = "ONE_CUT" or "MULTI_CUT"
    
    """

    #frequency of crossovers are proportional to the distance between two genes
    
    if cut_type not in ["ONE_CUT", "MULTI_CUT"]:
      cut_type == "ONE_CUT"

    i        = 0
    len_ance = len(ancestors)
    genes    = len(ancestors[0])  # numeros de cirurgias, talvez devesse considerar o dobro...(teste legal)
    
    aux_bias = [i for i in range(len_ance)]  # Isso daqui controla a probabilidade do crossover, 
    fit_bias = []                            # Talvez teha que ajustar isso para ser maleável.
    for i in aux_bias:
      fit_bias += aux_bias[i:]


    recombinant_ancestors = [ancestors[-1]]

    for i in range(len_ance-1):

      # Seleciono dois ancestrais, em função da fitness para o cross over

      idx1 = fit_bias[np.random.randint(len_ance)]
      idx2 = fit_bias[np.random.randint(len_ance)]

      if idx1 == idx2:
        recombinant_ancestors += [ancestors[idx1],ancestors[idx1]] # Caso sejam o mesmo, crossover nao muda

      else: # caso contrário, Cross over!!
        
        #primeiro determinamos qual tipo é:

        if cut_type == "ONE_CUT":

            break_point = np.random.randint(1, genes)

            ## Verificar a necessidade de usar deepcopy aqui...

            ancestor        = ancestors[idx1]
            ancestor_target = ancestors[idx2]

            ances = ancestor[:break_point]
            tor   = ancestor[break_point:]
            
            tar   = ancestor_target[:break_point]
            get   = ancestor_target[break_point:]
            
            recombinant_ancestors +=  [tar   +  tor]
            recombinant_ancestors +=  [ances +  get]
            recombinant_ancestors +=  [ancestor_target]
            recombinant_ancestors +=  [ancestor]
            
        if cut_type == "MULTI_CUT":

            break_point = np.random.randint(1, genes)

            ## Verificar a necessidade de usar deepcopy aqui...

            ancestor        = ancestors[idx1]
            ancestor_target = ancestors[idx2]

            ances = ancestor[:break_point]
            tor   = ancestor[break_point:]
            
            tar   = ancestor_target[:break_point]
            get   = ancestor_target[break_point:]
            
            recombinant_ancestors +=  [tar   +  tor]
            recombinant_ancestors +=  [ances +  get]
            recombinant_ancestors +=  [ancestor_target]
            recombinant_ancestors +=  [ancestor]

    
    return recombinant_ancestors


def offspringer(recombinant_ancestors, children):
  """ Função responsável por gerar a próxima geração, escolhendo pares de ancestrais recombinados e gerando K = children filhos por geração (hmm talvez tenha algo melhor).
  
  A recombinação é feita escolhendo metade dos genes do pai e metade da mãe EM MÉDIA (podendo ser iguais)"""


  Len_rec = len(recombinant_ancestors)

  offspring = recombinant_ancestors

  for child in range(children):

    baby = []
  
    idx_a   = np.random.randint(Len_rec)
    idx_b   = np.random.randint(Len_rec)
    
    for (gene_a, gene_b) in zip(recombinant_ancestors[idx_a], recombinant_ancestors[idx_b]):

      p = np.random.rand(1)

      if p > 0.5:

          baby.append(gene_a)
  
      else:

          baby.append(gene_b)
    
    offspring.append(baby)

  return offspring

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
                                altered_gene += [min(mg, Max_Rooms)]
                            if g == 1:
                                altered_gene += [min(2, Max_Rooms)]
                        else:
                            if g > 1:
                                altered_gene += [max(1, g + 2*np.random.randint(0,2) - 1)]
                            if g == 1:
                                altered_gene += [2]
                    else:
                        
                        altered_gene +=[g]
                
                altered_child += [altered_gene]
                
            mutated_offspring += [altered_child]
                        
        else:
    
            mutated_offspring += [child]  # Se ele perder de β, ele não vai ser mutado.
    
    return mutated_offspring


def select_ancestors(fit_idx_vector, elite_cut, n_sortudos):
    
    elite           = [idx[1] for idx in fit_idx_vector[-elite_cut:]]
    sortudos        = []
    Max_Sortudo     = len(fit_idx_vector) - elite_cut
    
    
    fit_idx_vector = fit_idx_vector[:-elite_cut] 
    for i in range(n_sortudos):
        
        sortudo_idx = np.random.randint(Max_Sortudo)
        sortudos += [fit_idx_vector[sortudo_idx][1]]

        fit_idx_vector = fit_idx_vector[:sortudo_idx] + fit_idx_vector[sortudo_idx+1:]
        Max_Sortudo -= 1
    
    return sortudos+elite

def Genetic_Algorithm(Instancia, F_obj, params, stop_criteria,Presolve = True, Verbose = True):

  """ Teremos que Data é da forma de Toy2 com informaçoes sobre num de salas etc 
      f_obj será utilizada como fitness provavelmente, e possui entradas:  [Cirurgias, Data, PenaltyTable]
      params são os parãmetros do algoritimo genético:  params = [\alpha,...?] 
      
      Max_Rooms = Numero de salas vem de onde??  (Razoavel supor que o máximo é o numero de  especialidades? acho que nao)


      Lembrete que Data é a matriz na forma:

      Cirurgia  k  - Prioridade - Dias_Espera - Especialidade - Cirurgião - Duração(t_c)


      params = pop_inicial, elite_cut, lucky_cut, LimitDay, generations, α, Cut_type, children, β
      
      Cut_type = "ONE_CUT" or "MULTI_CUT"
      
      """

  # primeiro calculamos o numero de cirurgias: Len(Data) vs Data[-1][0]  (por enquanto Data = Toy2)

  pop_inicial, elite_cut, lucky_cut, LimitDay, generations, α, Cut_type, children, β= params  # params assessment  (Max_Rooms é o número de salas).

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

    fit_idx_vector += [[fitness(Xi, Instancia, F_obj), Xi]]

  if Verbose == True:
    print("A população inicial é de " +str(pop_inicial))
    print(" ")
    if Verbose == "Strong":
      for idx in fit_idx_vector:
        print(idx)

      print(" ")

  fit_idx_vector.sort(reverse = True)
    
  ancestors = select_ancestors(fit_idx_vector, elite_cut, lucky_cut)

  if Verbose == "Strong":
    print("Ou seja, teremos como os ancestrais(High Scores) os seguintes, tendo em vista que elite_cut = " + str(elite_cut + lucky_cut))
    print(" ")
    for ancestor in ancestors:
      print(ancestor, fitness(ancestor, Instancia, F_obj), F_obj(ancestor, Data))
    print(" ")

  evolution = [ancestors]
  if Verbose == True:
    print(" Preparando para começar as recombinações ...")
 
  ## Considerando X na forma (Dia-sala-ordem) para gerar uma pop inicial válida precisamos garantir que os dias n durem mais de 46 intervalos de tempo
  ## Isso pode ser considerado durante um presolve que restringe quais cirurgias podem ser feitas no mesmo dia (analogo ao caso de multiplas salas para multiplos tipos de cirurgia.)
  ## Acho que são as unicas restrições. 
  ## (ordem das cirurgias nao é relevante para a f_obj) por enquanto. Precisamos alterá-la.
  ## Vou implementar a função sugerida no grupo do telegram. 


  ## Dado tudo isso, Geramos um conjunto inicial de tamanho pop_inicial onde cada individui é um X com uma ordem aleatoria distribuida uniformemente sobre as soluções viáveis (toda sol é viáve?)

  ## A partir dessa população, calculamos a fitness em todo mundo (uma modificacao da f_obj para rodar mais rapido provavlemente)

  ## O maxdays das proximas geraação é o 2*soft_max das melhores soluções+k (k = 2 algo asssim) desse mdo
  ## ele tende a manter um número perto de dias decidido pelo negocio  anterior, visto que a média vai cair
  ## perto da solucao anterior.

  K = 0
    
  evolution = []
  stop_criteria = [0]*stop_len
  t = time() - t0
  for generation in range(generations):
      t0 = time()
      if Verbose == True:
        
          print(" Estamos gerando a geração " + str(generation + 1 ) + " de " + str(generations), "a ultima demorou: {:.2f}".format(t)+"s")

      recombinant_ancestors = crossover(ancestors,α, Cut_type)
      
      if  Verbose == "Strong" and K <= 2:
        print(" ")
        print(" Aqui vai os ancestrais modificados")
        print(" ")
        for rac in recombinant_ancestors:
          print(rac,fitness(rac, Instancia, F_obj), F_obj(rac, Data))

        K = 2


      offspring  = offspringer(recombinant_ancestors,children)


      if Verbose == "Strong" and K <= 2:

        print(" ")
        print("Se prepara pra ver os filhotes")
        print(" ")
        for child in offspring:
          print(child, fitness(child, Instancia, F_obj), F_obj(child, Data))

        print(" ")
        print(" Preparando o Elemento X para as mutações ") 
        
      mutated_offspring     = mutation(offspring, Max_Rooms,β)
        
      fit_idx_vector = [[fitness(Xi, Instancia, F_obj), Xi] for Xi in mutated_offspring]
      fit_idx_vector.sort(reverse = True)
      ancestors      = select_ancestors(fit_idx_vector, elite_cut, lucky_cut)
      evolution.append(ancestors)
      
      t = time() - t0
      L = fit_idx_vector[-Zt:]
      W = np.array(L, dtype=object).T[0]
      avrg = sum(W)/Zt
      best = fit_idx_vector[-1]
        
      stop_criteria[generation%stop_len] = abs(avrg - best[0]) <= tol
      
      if sum(stop_criteria) == stop_len:
        
        print(" ")
        print(" Algoritmo encerrou devido ao criterio de parada mágico ")
        print(" ")
        
        return evolution
    
      t = time() - t0
      if fit_idx_vector[-1][0] < 0:
        
        print(" ")
        print(" Deu negativo, arruma a fitness ")
        return evolution

  ## COmo criterio de parada podemos verificar o quanto a média da geração está melhorando.
  ## Ou entao o max da solucao (algo em funçao dos dois seria melhor ainda).

  return evolution