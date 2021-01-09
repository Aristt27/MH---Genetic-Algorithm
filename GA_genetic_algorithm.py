import numpy as np
from itertools import groupby

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


def fitness(X, Data, F_obj, verbose = False):

  """ Aplica a função objetivo e tambem penaliza X caso ocorra o seguinte:
  
  - Dias com mais de 46 intervalos;
  - Sobreposição de horários;
  - Salas sendo usadas pra multiplas especialidades;
  - Cirurgião em mais de uma cirurgia ao mesmo tempo;

  Começando dando uma penalização de 10% da F_obj para cada uma das infrações (dualizando as restrições)

  A FAZER: 
  - Inserir penalização para cirurgião em dois lugares ao mesmo tempo
  - Inserir uma maior penalização para cirurgias no mesmo dia (quanto mais ultrapassa do limite, mais penaliza)
  """

  x_val = F_obj(X, Data)

  penalty1     = 0
  penalty2     = 0
  max_days      = 0
  max_rooms     = 0
  time_interval = 2
  blocos        = []
  ans           = []

  for idx, cirurgia in enumerate(X):

    cirurgia_dia  = cirurgia[0]
    cirurgia_sala = cirurgia[1]

    if cirurgia_dia > max_days:

      max_days = cirurgia_dia
    
    if cirurgia_sala > max_rooms:

      max_rooms = cirurgia_sala


    duration   = Data[idx][-1] + time_interval   # a ultima entrada de data[idx] possui a duracao da cirurgia e ela é acrescida do intervalo entre as cirurgias.
    especialidade = Data[idx][3]

    blocos.append([cirurgia_dia, cirurgia_sala, duration, especialidade])


  for day in range(max_days):
    diax = []
    for room in range(max_rooms):
      roomx = []
      for bloco in blocos:
        if bloco[0] == day+1:
          if bloco[1] == room+1:
            roomx += [[bloco[2], bloco[3]]]   #eu coloco a duração e a especialidade de cada cirurgia na sala

      roomx = np.array(roomx)  
      roomx = roomx.T
      if len(roomx) != 0 :
        pen_1_weight =  48 - sum(roomx[0])  #aqui eu verifico se o horario está maior que o limite
        if pen_1_weight < 0:
          penalty1 = -pen_1_weight
        if all_equal(roomx[1]) == False:  #aqui eu verifico se ela possui sómente cirurgias de mesma especialidade
         penalty2 = 1

        diax += [roomx]

    ans.append(diax)

  if verbose == True:
    print(ans)

  return x_val*(1+ ((penalty1**2) + penalty2)*(50)) 


def crossover(ancestors, α, cut_type = "ONE_CUT"):
    """Synapsys two ~randomly~ different ancestors chromossomes ~ parallel or not (?) α,δ ??
    
    \alpha -> probabilidade de cruzamento

    Considerando x = [[1,2,3],[3,2,1],[1,2,3],[1,2,3]] e y = [[3,2,1],[1,2,3],[3,2,1],[3,2,1]]

    Primeiro eu transformo em x = [1,2,3,3,2,1,1,2,3,1,2,3] com alguma funcao magica.

    Depois de combinar eu retorno para a forma matricial.

    Quais as chances que queremos de obter [[1,2,3],[1,2,3],[1,2,3],[1,2,3]]? """

    #frequency of crossovers are proportional to the distance between two genes
    
    if cut_type not in ["ONE_CUT", "MULTI_CUT", "MASK_CUT"]:
      cut_type == "ONE_CUT"

    i        = 0
    len_ance = len(ancestors)
    genes    = len(ancestors[0])  # numeros de cirurgias, talvez devesse considerar o dobro...(teste legal)
    
    aux_bias = [i for i in range(len_ance)]  # Isso daqui controla a probabilidade do crossover, 
    fit_bias = []                            # Talvez teha que ajustar isso para ser maleável.
    for i in aux_bias:
      fit_bias += aux_bias[i:]


    recombinant_ancestors = []

    for i in range(len_ance):

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

            pass

        if cut_type == "MASK_CUT":

            pass
    
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


def mutation(offspring,β,ϵ):
    
    'Ocurrs a random mutation in a random collection of genes of different cells over a given offspring ~ what is ϵ?'
    """Para cada unidade em offsprig, existe uma probabilidade $\beta$ para ocorrer 1 troca entre seus genes. 
     E uma probabilidade $\varepslon$ de dar +=1 no dia ou na sala de um gene.
     
     Isso ta uma loucura. 
     
     """
    
    mutated_offspring = []
    
    for chromossomes in offspring:
        
        if np.random.rand(1) < β:
            
            if np.random.rand(1) > 0.5:  # se ele tirar coroa, ele shifta dia ou sala
              
                for gene in chromossomes:

                    if np.random.rand(1) < ϵ:
                        new_gene = []

                        for c in gene:

                            new_gene += []
            
            else: # se ele tirar cara, ele da uma bagunçada nas cirurgias, perturbando um pouco
               
                altered_genes = []
                
                for idxs, gene in enumerate(chromossomes):
                    
                    if np.random.rand(1) < ϵ:
                        
                        altered_idx += [idx]
                        altered_chromossomes = []
                altered_len = len(altered_genes)
                
                if altered_len > 0:
                    
                    genes = genes[:altered_len]+altered
                mutated offspring += [altered_genes]
                        
        else:
            
            mutated_offspring += [chromossomes]
    
    return mutated_offspring


    ## Queremos fornecer como entrada apenas Toy2(Data) e alguns outros parametros chatos para obter de saída X e X_bd (com a melhor fitness encontrado)


def Genetic_Algorithm(Data, F_obj, params, Presolve = True, Verbose = True):

  """ Teremos que Data é da forma de Toy2 com informaçoes sobre num de salas etc 
      f_obj será utilizada como fitness provavelmente, e possui entradas:  [Cirurgias, Data, PenaltyTable]
      params são os parãmetros do algoritimo genético:  params = [\alpha,...?] 
      
      Ss = Numero de salas vem de onde??  (Razoavel supor que o máximo é o numero de  especialidades? acho que nao)


      Lembrete que Data é a matriz na forma:

      Cirurgia  k  - Prioridade - Dias_Espera - Especialidade - Cirurgião - Duração(t_c)


      se verbose = True...
      Se Presolve = True fazemos algumas otimizaçoes antes de comecar a resolver
      Retorna X_bd. """

  # primeiro calculamos o numero de cirurgias: Len(Data) vs Data[-1][0]  (por enquanto Data = Toy2)

  pop_inicial, gen_cut, LimitDay, Ss, generations, α, children = params  # params assessment  (Ss é o número de salas).

  Cs         = len(Data)
  HorarioMax = get_horariomax(Data)

  fit_idx_vector = []

  #Aqui vamos agrupar as cirurgias de mesmas especialidades:
  # Especialidades = []

  # for j in range(100): #Até a especialidade máxima
  #   Escpecialidadej = []
  #   for C in Data:
  #     if C[3] == j:
  #       Especialidades.append(Especialidadej)
    
  #   if Especialidadej == []:
  #     print(j)
  #     break
  
  for i in range(pop_inicial):
    # Aqui vamos sortear um dia, uma sala e um horário para cada cirurgia. Primeiro vamos sortear um dia para cada cirurgia
    Max_Days = np.random.randint(2,LimitDay)

    Xi  = [[np.random.randint(1,Max_Days), np.random.randint(1, Ss+1), np.random.randint(1,HorarioMax+1)] for j in range(Cs)]


    # Falta verificarmos as salas bem como horários sobrepostos (acho que podemos colocar isso na função fitness, penalizando exponencialmente caso isso aconteça)

    # Para maximizar as chances de que a solução seja viável, como fazer? Talvez possamos confiar cegamente na função objetivo pra gerar uma população boa no final....

    fit_idx_vector += [[fitness(Xi, Data, F_obj), Xi]]

  if Verbose == True:
    print("A população inicial é de " +str(pop_inicial))
    print(" ")
    if Verbose == "Strong":
      for idx in fit_idx_vector:
        print(idx)

      print(" ")

  fit_idx_vector.sort(reverse = True)

  ancestors = [idx[1] for idx in fit_idx_vector[-gen_cut:]]

  if Verbose:
    print("Ou seja, teremos como os ancestrais(High Scores) os seguintes, tendo em vista que gen_cut = " + str(gen_cut))
    print(" ")
    for ancestor in ancestors:
      print(ancestor, fitness(ancestor, Data, F_obj), F_obj(ancestor, Data))
    print(" ")

  evolution = [ancestors]

  print(" Preparando para começar as recombinações ...")
 
  ## Considerando X na forma (Dia-sala-ordem) para gerar uma pop inicial válida precisamos garantir que os dias n durem mais de 46 intervalos de tempo
  ## Isso pode ser considerado durante um presolve que restringe quais cirurgias podem ser feitas no mesmo dia (analogo ao caso de multiplas salas para multiplos tipos de cirurgia.)
  ## Acho que são as unicas restrições. 
  ## (ordem das cirurgias nao é relevante para a f_obj) por enquanto. Precisamos alterá-la.
  ## Vou implementar a função sugerida no grupo do telegram. 


  ## Dado tudo isso, Geramos um conjunto inicial de tamanho pop_inicial onde cada individui é um X com uma ordem aleatoria distribuida uniformemente sobre as soluções viáveis (toda sol é viáve?)

  ## A partir dessa população, calculamos a fitness em todo mundo (uma modificacao da f_obj para rodar mais rapido provavlemente)
  ## Otimizamos nessa f_obj e geramos novas populações.

  ## Discussão sobre Crossing-over e Mutação na solução e alguns testes são importantes. 

  ## O maxdays das proximas geraação é o 2*soft_max das melhores soluções+k (k = 2 algo asssim) desse mdo
  ## ele tende a manter um número perto de dias decidido pelo negocio  anterior, visto que a média vai cair
  ## perto da solucao anterior.

  K = 0

  for generation in range(generations):

      recombinant_ancestors = crossover(ancestors,α)
      
      if  Verbose == True and K <= 2:
        print(" ")
        print(" Aqui vai os ancestrais modificados")
        print(" ")
        for rac in recombinant_ancestors:
          print(rac,fitness(rac, Data, F_obj), F_obj(rac, Data))

        K = 2


      offspring  = offspringer(recombinant_ancestors,children)


      if Verbose == True and K <= 2:

        print(" ")
        print("Se prepara pra ver os filhotes")
        print(" ")
        for child in offspring:
          print(child, fitness(child, Data, F_obj), F_obj(child, Data))

        print(" ")
        print(" é isto imrão ") 
        
      #mutated_offspring     = mutation(offspring,β,ϵ)
        
  #       fit_idx_vector = [[fitness(xs,ws),i]for xs,i in zip(mutated_offspring,range(population))]
  #       fit_idx_vector.sort()
  #       ancestors  = [mutated_offspring[idx[1]] for idx in fit_idx_vector[-gen_cut:]]
        
  #       evolution.append(ancestors)
  #   evolved = evolution[-1]


  ## COmo criterio de parada podemos verificar o quanto a média da geração está melhorando.
  ## Ou entao o max da solucao (algo em funçao dos dois seria melhor ainda).



  return 0