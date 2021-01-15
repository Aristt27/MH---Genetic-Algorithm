from numpy import random

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
        
      idx1 = fit_bias[random.randint(lfb)]
      idx2 = fit_bias[random.randint(lfb)]  
      
      if random.rand(1) < alpha:
        if idx1 == idx2:
          while idx1 == idx2:
            idx1 = fit_bias[random.randint(lfb)]
            idx2 = fit_bias[random.randint(lfb)]

        else: # caso contrário, Cross over!!

          if cut_type == "ONE_CUT":

              break_point = random.randint(1, genes-1)

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

              n_break_points = random.randint(1, genes//2)

              ancestor        = ancestors[idx1]
              ancestor_target = ancestors[idx2]

              for _ in range(n_break_points):
                ## Verificar a necessidade de usar deepcopy aqui...

                break_point = random.randint(1, genes - 1)



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