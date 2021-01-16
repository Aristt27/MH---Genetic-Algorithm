from random import sample
from numpy import random as rd

def mutation(offspring,Instancia,β):
    
    """
      Lembrete que Data é a matriz na forma:
      Cirurgia  k  - Prioridade - Dias_Espera - Especialidade - Cirurgião - Duração(t_c)
      
     
     Com probabilidade β ele escolhe o filho para mutar.
     
     Ideias:
          
     Quase safe:
     Ele seleciona uma cirurgia com especialidade e0 e outra com mesma e troca ambas de lugar. (Pode invalidar o dia);
     
     Valida:
     Ele seleciona uma cirurgia com especialidade e0 e duração d0, ele seleciona uma outra cirurgia com mesma 
     especialidade e duração d1 <= d0. Troca essas duas de lugar. (Unica coisa q pode dar errado é com o médico sobreposto);
     
     """
    Prob              = β
    nonmut            = []
    mut_idxs          = []
    mutated_offspring = []
    genes             = len(offspring[0])
    
    Data, Max_Rooms   = Instancia
    
    for idx, child in enumerate(offspring):
                
        if rd.rand(1) < Prob: ## Caso ele perca de β, ele vai ser mutado.
            new_child = []
            muta_g = rd.randint(genes)
            e0     = Data[muta_g][3]
            candidates = []
            for cir in range(genes):
                if cir != muta_g:
                    e1  = Data[cir][3]
                    if e0 == e1: # se tiverem a mesma especialidade
                        candidates.append(cir)
            candidate = sample(candidates, 1)[0]
            for cid, cen in enumerate(child):
                if cid == muta_g:
                    new_child.append(child[candidate])
                if cid == candidate:
                    new_child.append(child[muta_g])
                if cid != muta_g and cid != candidate:
                    new_child.append(child[cid])
 #           new_child = corrected_time(new_child, Data)
            mutated_offspring.append(new_child)
            mut_idxs.append(idx)
        else:
            
            nonmut.append(idx)
    
            mutated_offspring.append(child) # Se ele perder de β, ele não vai ser mutado.
    
    return mutated_offspring, mut_idxs, nonmut


def mutation_insertion(offspring,Instancia,β):
    
    """
      Lembrete que Data é a matriz na forma:
      Cirurgia  k  - Prioridade - Dias_Espera - Especialidade - Cirurgião - Duração(t_c)
      
     
     Com probabilidade β ele escolhe o filho para mutar.
     
     Ideias:
          
     Quase safe:
     Ele seleciona uma cirurgia com especialidade e0 e outra com mesma e troca ambas de lugar. (Pode invalidar o dia);
     
     Valida:
     Ele seleciona uma cirurgia com especialidade e0 e duração d0, ele seleciona uma outra cirurgia com mesma 
     especialidade e duração d1 <= d0. Troca essas duas de lugar. (Unica coisa q pode dar errado é com o médico sobreposto);
     
     """
    Prob              = β
    nonmut            = []
    mut_idxs          = []
    mutated_offspring = []
    genes             = len(offspring[0])
    
    Data, Max_Rooms   = Instancia
    
    for idx, child in enumerate(offspring):
                
        if rd.rand(1) < Prob: ## Caso ele perca de β, ele vai ser mutado.
            new_child = []
            muta_g = rd.randint(genes)
            e0     = Data[muta_g][3]
            candidates = []
            for cir in range(genes):
                if cir != muta_g:
                    e1  = Data[cir][3]
                    if e0 == e1: # se tiverem a mesma especialidade
                        candidates.append(cir)
            candidate = sample(candidates, 1)[0]
            for cid, cen in enumerate(child):
                if cid == muta_g:
                    new_child.append(child[muta_g])
                if cid == muta_g+1:
                    new_child.append(child[candidate])
                if cid != muta_g and cid != muta_g+1:
                    new_child.append(child[cid])
 #           new_child = corrected_time(new_child, Data)
            mutated_offspring.append(new_child)
            mut_idxs.append(idx)
        else:
            
            nonmut.append(idx)
    
            mutated_offspring.append(child) # Se ele perder de β, ele não vai ser mutado.
    
    return mutated_offspring, mut_idxs, nonmut