# Imports, Dependencies

from GA_genetic_algorithm import fitness
import matplotlib.pyplot as plt 
import numpy as np
import seaborn as sb
import pandas as pd

def evolution_statistical_analysis(Evolution, fitness, fitness_data, cut = 15, Mode = "Default", Verbose = True, plots = True):
    """ Matplots a evolução.
    
    
    No modo Best, ele pega apenas o melhor
    
    No modo Average ele pega uma média dos melhores --cut-- da população
    
    No modo Default, ele pega os dois.  """
    
    Generations = len(Evolution)
    Population  = len(Evolution[0])
    
    print(" ")
    print(" O Algoritmo levou " + str(Generations) + " iterações.")
    print(" ")
    #Pop_cut     = ((cut*100)*(Population))//100
    Pop_cut     = cut
    #print(Pop_cut, Population)
    
    Instance, F_obj = fitness_data
        
        
    avgs     = []
    cut_avgs = []
    bests    = []
    
    for generation in Evolution:
        scores = np.array([])
        pop         = generation[:]
        
        for X in pop:
             scores = np.append(scores, fitness(X, Instance, F_obj))
        
 
        scores.sort()
        scores = scores[::-1]
        high_scores  = scores[-cut:]
        avgs     += [np.average(scores)]
        cut_avgs += [np.average(high_scores)]
        bests += [high_scores[-1]]
     
    
    if plots == True:
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
        sb.lineplot(data=dataf, markers = True, ax = ax)

    return cut_avgs, bests 
    