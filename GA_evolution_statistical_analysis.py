# Imports, Dependencies

import matplotlib.pyplot as plt 
import numpy as np
import seaborn as sb
import pandas as pd

def evolution_statistical_analysis(Evo_Scores, K = 15, Mode = "Default", Verbose = True, Plots = True):
    """ Matplots a evolução.
    
    No modo Best, ele pega apenas o melhor
    
    No modo Average ele pega uma média dos melhores --cut-- da população
    
    No modo Default, ele pega os dois.  """
        
    Generations = len(Evo_Scores)
    Population  = len(Evo_Scores[0])
    
    print(" ")
    print(" O Algoritmo levou " + str(Generations) + " iterações.")
    print(" ")           
        
    avgs     = []
    cut_avgs = []
    bests    = []
    
    for generation in Evo_Scores:
        scores = np.array([])
        
        for X in generation:
             scores = np.append(scores, X)
        
 
        scores.sort()
        scores = scores[::-1]
        high_scores  = scores[-K:]
        avgs     += [np.average(scores)]
        cut_avgs += [np.average(high_scores)]
        bests += [high_scores[-1]]
     
    
    if Plots == True:
        
        if Mode == "Default":
            logcut   = np.log(np.array(cut_avgs))
            logbests = np.log(np.array(bests))
            logavgs  = np.log(np.array(avgs))   

            dataf = pd.DataFrame(data=[logcut, logavgs, logbests], index=["logcuts", "logavgs", "logbests"]).transpose()

            fig, ax = plt.subplots(figsize=(16, 8))


            ax.set_title('Average vs Best')

            ax.set_xlim([0,  Generations-1])

            ax.set_xticks(np.arange(0,Generations))

            ax.set_xticklabels(np.arange(1,Generations+1))

            sb.set_theme(style="darkgrid")

            #plt.figure(figsize=(14,8))
        if Mode == "Best":
            logbests = np.log(np.array(bests))
            dataf = pd.DataFrame(data=[logbests], index=["logbests"]).transpose()
            
            fig, ax = plt.subplots(figsize=(16, 8))


            ax.set_title('Best')

            ax.set_xlim([0,  Generations-1])

            ax.set_xticks(np.arange(0,Generations))

            ax.set_xticklabels(np.arange(1,Generations+1))

            sb.set_theme(style="darkgrid")

        sb.lineplot(data=dataf, markers = True, ax = ax)

    return cut_avgs, bests 
    