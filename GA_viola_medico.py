import numpy as np

def viola_medico(instancia,solucao, LIM, FIX = False):
#Primeiro temos que saber que medico ira fazer cada cirurgia e quanto irá durar
#SALA - DIA - TO - MEDICO - DURACAO
    solucao_medico = np.array([solucao[i]+instancia[i][4:] for i in range(len(solucao))])

    #Quantos medicos diferentes tem? Para poder iterar:
    medicos = set(np.array(instancia)[:,4])

    for medico in medicos:
        for dia in range(1,6):
            agendadas = solucao_medico[(solucao_medico[:,4]==medico) & (solucao_medico[:,0]==dia)]
            agendadas_ordem = agendadas[agendadas[:,2].argsort()]

            #verifica se de fato tem cirurgias naquele dia
            if len(agendadas) == 0:
                break
            #startamos com o termino da primeira cirurgia do medico
            #print(agendadas_ordem)
            tempo = [agendadas_ordem[0,2]+agendadas_ordem[0,3]]
            for cirurgia in agendadas_ordem[1:] :
                #se o tempo inicial da proxima cirurgia for menor que o tempo final da cirurgia anterior, TRUE
                if cirurgia[2] < tempo[-1]:
                    #print(["True",medico,dia])
                    if FIX == False:
                        return True, [dia]
                    else:
                        return sol_fixer(dia, instancia, solucao, LIM)
                #senao, faz a cirurgia (acrescenta o tempo dela)
                else:
                    tempo.append(cirurgia[2]+cirurgia[3])
    return False, [-1]

def sol_fixer(dia, instancia, solucao, LIM = 100):
    A = True
    salas = 0
    for C in solucao:
        if C[1] > salas:
            salas = C[1]
        
    
    while A == True and LIM > 0:
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
            
        roomms = np.array(roomms)
        
        for room in roomms:
            room = np.array(room)
            r = room[room[:,3].argsort()]
            hours = 0
            for cn in r:
                for kk in list(cn[1:-1])+[hours]:
                    new_sol[cn[0]].append(kk)
                    hours += instancia[cn[0]][-1]

 
        LIM -= 1
        solucao = new_sol
        A, d = viola_medico(instancia,solucao)
    return A, new_sol


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
            
        roomms = np.array(roomms)
        
        for room in roomms:
            
            room = np.array(room)
            if len(room) > 0:
                r = room[room[:,3].argsort()]
                hours = 0
                for cn in r:
                    for kk in list(cn[1:-1])+[hours]:
                        new_sol[cn[0]].append(kk)
                        hours += instancia[cn[0]][-1]

 
        solucao = new_sol
    
    return new_sol
        
        