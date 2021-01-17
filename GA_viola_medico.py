import numpy as np

def viola_medico(instancia, solucao, n_dias=5, n_horarios=48):
    # pega os medicos existentes
    medicos = np.unique(np.array(instancia)[:, 4])

    # inicializa o cubo de busca
    cubao = np.zeros((max(medicos), n_dias, n_horarios))

    # para cada cirurgia
    for i, j in zip(solucao, instancia):
        # pego as ionformacoes da solucao
        dia, sala, comeco = i

        # pego as informacoes da cirurgia
        medico = j[-2]
        duracao = j[-1]

        # se a cirurgia foi marcada
        if dia <= n_dias:
            cubao[medico-1, dia-1, comeco:comeco+duracao] += 1

    return (cubao > 1).sum(), ((cubao > 0).sum(2) > 26).sum()

def all_sol_fixer(instancia, solucao):

    salas = 0
    dias  = 0
    
    for C in solucao:
        if C[1] > salas:
            salas = C[1]
        if C[0] > dias:
            dias  = C[0]
         
    
    for dia in range(1,dias+1): 
        solucao = np.array(solucao)   
        new_sol = [[]for i in range(len(solucao))] 
        cirurgias = []
        
        for idx,L in enumerate(solucao):
            if L[0] == dia:
                cirurgias.append(np.array([idx]+list(L)))
            else:
                for jj in L:
                    new_sol[idx].append(jj)
        
        roomms = [[] for i in range(salas)]
        for j in cirurgias:
            roomms[j[2]-1].append(j)
            
        roomms = np.array(roomms, dtype=object)
        
        for room in roomms:
            hours = 0
            room = np.array(room)
            if len(room) > 0:
                r = room[room[:,3].argsort()]
                for cn in r:
                    asddsa = list(cn[1:-1])
                    asddsa.append(hours)
                    for kk in asddsa:
                        new_sol[cn[0]].append(kk)
                    hours += instancia[cn[0]][-1]

 
        solucao = new_sol
    
    return new_sol