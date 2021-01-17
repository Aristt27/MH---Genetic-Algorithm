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

    return (cubao > 1).sum()