def viola_medico(instancia,solucao):
    #Primeiro temos que saber que medico ira fazer cada cirurgia e quanto irá durar
    #SALA - DIA - TO - MEDICO - DURACAO
    solucao_medico = np.array([solucao[i]+instancia[i][4:] for i in range(len(solucao))])

    #Quantos medicos diferentes tem? Para poder iterar:
    medicos = set(np.array(instancia)[:,4])

    for medico in medicos:
        for dia in range(1,6):
            agendadas = solucao_medico[(solucao_medico[:,3]==medico) & (solucao_medico[:,1]==day)]
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
                    return True
                #senao, faz a cirurgia (acrescenta o tempo dela)
                else:
                    tempo.append(cirurgia[2]+cirurgia[3])