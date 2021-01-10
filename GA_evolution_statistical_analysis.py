# Imports, Dependencies

from GA_genetic_algorithm import fitness
import matplotlib.pyplot as plt 
import numpy as np
import seaborn as sb
import pandas as pd

def evolution_statistical_analysis(Evolution, fitness, fitness_data, cut = 5, Mode = "Default", Verbose = True):
    """ Matplots a evolução.
    
    
    No modo Best, ele pega apenas o melhor
    
    No modo Average ele pega uma média dos melhores --cut-- da população
    
    No modo Default, ele pega os dois.  """
    
    Generations = len(Evolution)
    Population  = len(Evolution[0])
    
    #Pop_cut     = ((cut*100)*(Population))//100
    Pop_cut     = cut
    #print(Pop_cut, Population)
    
    Instance, F_obj = fitness_data
        
        
    avgs  = []
    bests = []
    
    for generation in Evolution:
        high_scores = np.array([])
        best_pop    = generation[-Pop_cut:]

        for X in best_pop:
            high_scores = np.append(high_scores, fitness(X, Instance, F_obj))
        

        avgs += [np.average(high_scores)]
        bests += [high_scores[-1]]
        
    logbests = np.log(np.array(bests))
    logavgs  = np.log(np.array(avgs))   
    
    dataf = pd.DataFrame(data=[logavgs, logbests], index=["logavgs", "logbests"]).transpose()
    
    fig = plt.figure(figsize=(12, 6))

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    
    ax1.set_title('Average vs Best')
    ax2.set_title('Best')
    
    ax1.set_xlim([0,  Generations-1])
    ax2.set_xlim([0, Generations-1])
    
    ax1.set_xticks(np.arange(0,Generations))
    ax2.set_xticks(np.arange(0,Generations))
    
    ax1.set_xticklabels(np.arange(1,Generations+1))
    ax2.set_xticklabels(np.arange(1,Generations+1))
    
    sb.set_theme(style="darkgrid")
    sb.lineplot(data=dataf, markers = True, ax = ax1)

    sb.lineplot(data=dataf["logbests"], markers = True, ax = ax2)
    return avgs, bests 
    