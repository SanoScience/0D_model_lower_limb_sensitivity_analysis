import numpy as np 
import pandas as pd 

import json
import os

from tqdm import tqdm, trange

from SALib.analyze import sobol

# ================= 
def sobol_analyser(
    df_outputs: pd.DataFrame, 
    dict_problem: dict, 
    bootstrap: int = 1000):
    
    '''
    Sobol analysis for one output metric type,
    e.g., mean_flow.
    
    Returns a dictionary with Total-order S-index, first-order and 2nd-order S-indices
    '''
    
    Y = df_outputs.to_numpy()
    
    S1 = {}; S1_conf = {}
    S2 = {}; S2_conf = {}
    ST = {}; ST_conf = {}
    
    i = 0
    for output_i in tqdm(list(df_outputs.index)):
        row = Y[i,:]
                
        S_row = sobol.analyze( 
                                problem = dict_problem,
                                Y = row,
                                num_resamples = bootstrap,
                                calc_second_order = True,
                                parallel=True,
                                n_processors=3
                                ) 
        
        S1[output_i] = S_row["S1"].tolist()
        S1_conf[output_i] = S_row["S1_conf"].tolist()
        
        S2[output_i] = S_row["S2"].tolist()
        S2_conf[output_i] = S_row["S2_conf"].tolist()
        
        ST[output_i] = S_row["ST"].tolist()
        ST_conf[output_i] = S_row["ST_conf"].tolist()
        
        i += 1
    
    return {"S1": S1, "S1_conf":S1_conf, "S2":S2, "S2_conf":S2_conf, "ST":ST, "ST_conf":ST_conf}

# ================= 
def run(metric_name, n_outputs, bootstrap, path_to_output, path_to_indices):
    colnames = [i for i in range(n_outputs)]

    df_data = pd.read_csv(path_to_output, sep=",", index_col=0, names=colnames, header=0)
    

    s_indices = sobol_analyser(df_data.T, problem, bootstrap) 
    
    index_path = os.path.join(path_to_indices, f"s_{metric_name}_b{bootstrap}.json")
    
    with open(index_path, "w") as fw:
        json.dump(s_indices, fw, indent=4)

# =========================================
# =========================================
if __name__ == "__main__":

    path_to_problem = "C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Sampling/problem.json"

    
    with open(path_to_problem) as fr:
        problem = json.loads( fr.read() )
    
    
    
    metric_name = "mean_pressure"
    N_outputs = 36 # for pressure metrics 36, for flow metrics 50
    bootstrap = 100
    
    path_to_output = f"C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Solver/merged_outputs/merged_output_{metric_name}.csv"
    
    
    path_to_indices =f"C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Sensitivity_analysis/indices"
    os.makedirs(path_to_indices, exist_ok=True)
       
    
    run(metric_name, N_outputs, bootstrap, path_to_output, path_to_indices)