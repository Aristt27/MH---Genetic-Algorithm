import numpy as np

from GA_fitness import fitness
from GA_crossover import crossover, crossover_tournament
from GA_mutation import mutation, mutation_insertion

from random import sample
from time import time


def select_ancestors(fit_idx_vector, elite_cut, n_sortudos):
    
    elite           = [idx[1] for idx in fit_idx_vector[-elite_cut:]]
    elite_fit       = [idx[0] for idx in fit_idx_vector[-elite_cut:]]
    
    sortudos        = []
    sortudos_fit    = []
    
    Max_Sortudo     = len(fit_idx_vector) - elite_cut
    sortudos_idxs   = sample(range(Max_Sortudo), n_sortudos)
    sortudos_idxs.sort()
    
    for sidx in sortudos_idxs:
        sortudos.append(fit_idx_vector[sidx][1])
        sortudos_fit.append(fit_idx_vector[sidx][0])
    
    soeli = sortudos+elite
    soeli_fit = sortudos_fit+elite_fit


    return soeli, soeli_fit

def aloca_cirurgias_random(instancia,  n_sala, n_dia = 5, max_dia = 48, max_tentativas = 20, tol = 0.1):
    # cria uma copia das instancias e dá um shuffle
    instancia = np.array(instancia)
    instancia[:,-1] +=2 
    instancias_alteradas = instancia[:]
    
    while True:
        #np.random.shuffle(instancias_alteradas)
        cubao = np.zeros((n_dia, n_sala, max_dia))
        resultado = []

        n_medicos = max(set(instancias_alteradas[:, -2]))
        especialidades = np.zeros((n_dia, n_sala))
        medicos = np.ones((n_medicos, n_dia, max_dia), bool)

        for i in instancias_alteradas:
            tentativas = max_tentativas
            duracao = i[-1]
            especialidade = i[-3]
            prioridade = i[1]
            cirurgiao = i[-2] - 1
            codigo = i[0]
            c = True

            while tentativas > 0:
                tentativas -= 1
                if prioridade == 1:
                  p = 0.95
                else:
                  p = 0.05

                if np.random.rand() < p:
                  dia = 0
                else:
                  dia = np.random.randint(1, n_dia)
                sala = np.random.randint(n_sala)

                ocupados = sum(cubao[dia, sala, :] > 0)
                # cabe no dia
                if ocupados + duracao <= max_dia:
                    # é da especialidade certa
                    if (especialidades[dia, sala] == especialidade) or (especialidades[dia, sala] == 0):
                        # o cirurgiao ta livre
                        if all(medicos[cirurgiao, dia, ocupados:ocupados+duracao]):
                            cubao[dia, sala, ocupados:ocupados+duracao] = codigo
                            medicos[cirurgiao, dia, ocupados:ocupados+duracao] = False
                            resultado.append([codigo, dia + 1, sala + 1, ocupados])
                            c = False
                            if especialidades[dia, sala] == 0:
                                especialidades[dia, sala] = especialidade
                            break
            if c:
                resultado.append([codigo, n_dia + 1, -1, -1])
        resultado = np.array(resultado)
        if sum(resultado[:, 0] == n_dia + 1) / len(resultado) < tol:
            break
    return resultado[resultado[:,0].argsort()][:,1:].tolist()

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


def Genetic_Algorithm(Instance, params, stop_criteria, Target = False, Presolve = True, Verbose = True):

  """ 
      Instance contém a dupla (Data, Max_Rooms)
            (Max_Rooms é o número de salas).

      Lembrete que Data é a matriz na forma:
      Cirurgia  k  - Prioridade - Dias_Espera - Especialidade - Cirurgião - Duração(t_c)
      
      params = pop_inicial_total, gen_cuts, cross_params, mutation_params  
      gen_cuts = elite_cut, lucky_cut
      cross_params = Cross_selection, alpha, Cut_type, tournament_size
      mutation_params =  Mutation_type, prob
      pop_inicial_total = (greedy_pop, random_pop)

      Cut_type = "ONE_CUT" or "MULTI_CUT"
      
      """

  # primeiro calculamos o numero de cirurgias: Len(Data) vs Data[-1][0]  (por enquanto Data = Toy2)

  pop_inicial_total, gen_cuts, cross_params, mutation_params = params  # params assessment  (Max_Rooms é o número de salas).

  greedy_pop, greedy_pop2, random_pop  = pop_inicial_total
  pop_inicial            = greedy_pop + random_pop + greedy_pop2

  elite_cut, lucky_cut   = gen_cuts
    
  Cross_selection, alpha, Cut_type, tournament_size  = cross_params

  Mutation_type, beta    = mutation_params
    
  generations, stop_len, Zt, tol = stop_criteria

  FIX_bool = False
    
  if elite_cut < 1:
    
    elite_cut = int(((100*elite_cut)*pop_inicial)//100)

  if lucky_cut < 1:
    
    lucky_cut = int(((100*lucky_cut)*pop_inicial)//100)
    
  Data, Max_Rooms = Instance
    
  Cs         = len(Data)

  fit_idx_vector = []

  t0  = time()
  for i in range(greedy_pop2):
    Xi  = aloca_cirurgias_random(Data,  Max_Rooms)
    
    aa, bb = fitness(Xi, Instance)
    fit_idx_vector.append([aa, bb])

     
  for i in range(random_pop):
    Xi  = [[np.random.randint(1,7), np.random.randint(1, Max_Rooms+1), np.random.randint(1,3)] for j in range(Cs)]

    aa, bb = fitness(Xi, Instance)
    fit_idx_vector.append([aa, bb])

  for i in range(greedy_pop):
    Xi  = aloca_cirurgias(Data,  Max_Rooms)
    
    aa, bb = fitness(Xi, Instance)
    fit_idx_vector.append([aa, bb])

  fit_idx_vector.sort(reverse = True)
  ancestors, ans_fits = select_ancestors(fit_idx_vector, elite_cut, lucky_cut)

  evolution  = [ancestors[:]]
  evo_scores = [ans_fits[:]]
  stop_criteria = [0]*stop_len
    
  t = time() - t0
  FIX_boo = False
    
  for generation in range(generations):
      t0 = time()
      if Verbose == True:
        
          print(" Estamos gerando a geração " + str(generation + 1 ) + " de " + str(generations), "a ultima demorou: {:.2f}".format(t)+"s")

      if Cross_selection == "Ranking":
        recombinant_ancestors = crossover(ancestors, pop_inicial, alpha, Cut_type)
      if Cross_selection == "Tournament":
        recombinant_ancestors = crossover_tournament(ancestors, ans_fits, pop_inicial, alpha, Cut_type, tournament_size)
      if Cross_selection == "Mix":
        if generation % 2 == 0:
          recombinant_ancestors = crossover(ancestors, pop_inicial, alpha, Cut_type)
        if generation % 2 == 1:
          recombinant_ancestors = crossover_tournament(ancestors, ans_fits, pop_inicial, alpha, Cut_type, tournament_size)

      ancestors, offspring, rec_idxs, nonrec  = recombinant_ancestors 

      nonrec_dict = {mn: nm for mn, nm in nonrec}
        
      if Mutation_type == "Swap":  
        mutated_offspring, mut_idxs, nonmut  = mutation(offspring, Instance, beta)
      if Mutation_type == "Insertion":
        mutated_offspring, mut_idxs, nonmut  = mutation_insertion(offspring, Instance, beta)
      if Mutation_type == "Mix":
        if generation % 2 == 0:
          mutated_offspring, mut_idxs, nonmut  = mutation(offspring, Instance, beta)
        if generation % 2 == 1:
          mutated_offspring, mut_idxs, nonmut  = mutation_insertion(offspring, Instance, beta)
        
      fit_idx_vector = [[afit, ancs] for ancs, afit in zip(ancestors, ans_fits)]
      if generation % 2 == 0:
        FIX_boo = (FIX_boo + 1) % 2
      for midx, mXi in enumerate(mutated_offspring):
        if midx in mut_idxs or midx in rec_idxs:
          aa, bb = fitness(mXi, Instance, FIX = FIX_boo)
          fit_idx_vector.append([aa, bb]) 
        else:
          indc = nonrec_dict[midx]
          fit_idx_vector.append([ans_fits[indc], mXi])
            
      fit_idx_vector.sort(reverse = True)
   
      ancestors, ans_fits      = select_ancestors(fit_idx_vector, elite_cut, lucky_cut)

      evolution.append(ancestors[:])
      evo_scores.append(ans_fits[:])
    
      ans_fits.sort(reverse = True)
      L = ans_fits[-Zt:]
      avrg = sum(L)/Zt
      best = L[-1]
        
      stop_criteria[generation%stop_len] = abs(avrg - best) <= tol
      if Target:
        if best < Target:
            return evolution, evo_scores
      if sum(stop_criteria) == stop_len:
        
        print(" ")
        print(" Algoritmo encerrou devido ao criterio de parada mágico ")
        print(" ")
        
        return evolution, evo_scores

      t = time() - t0
        
  print(" ")
  print(" Algoritmo encerrou devido ao número máximo de iterações/gerações.")
  print(" ")

  return evolution, evo_scores
