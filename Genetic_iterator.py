import numpy as np
from GA_Genetic_algorithm import Genetic_Algorithm
from time import time

def genetic_iterator(Instancia, set_params, set_stop_criteria, Iterations, output = False):
    ans = []
    tts = []
    its = []
    winners = []
    bestsol = 9999999999999
    for _ in range(Iterations):
        t0 = time()
        Evo, Evo_Scores =  Genetic_Algorithm(Instancia, set_params, set_stop_criteria, Verbose = False)
        tf = time() - t0
        al = len(Evo)
        sx = Evo_Scores[-1][-1]
        if sx < bestsol:
            bestsol = sx
            winners = Evo[-1][-1]
        its.append(al)
        tts.append(tf)
        ans.append(sx)
        if output:
            with open(output, 'a') as file:
                file.write(str(sx)+','+str(tf)+','+str(al) + '\n')
            with open("solution/" + output[:-4]+'sol.csv', 'w') as file2:
                file2.write("Cirurgia (c),Sala (r),Dia (d),Horário (t)\n")
                for wdx, col in enumerate(winners):
                    file2.write(str(wdx+1)+', '+str(col[:-1])[1:-1]+', '+str(col[-1]+1) + '\n')

    if output:
        
        with open(output, 'a') as file:
            file.write(str(min(ans))+' , '+ str(max(ans))+' , '+ str(np.average(ans))+' , '+str(np.std(ans))+'\n')
            file.write(str(np.average(tts))+'\n')
    return ans, tts, its