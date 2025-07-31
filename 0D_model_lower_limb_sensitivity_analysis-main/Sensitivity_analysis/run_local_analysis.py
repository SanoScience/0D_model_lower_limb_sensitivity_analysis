    
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt


import json
import os

class LocalSA:
    def __init__(self,
                 problem: dict, 
                 all_outputs: pd.DataFrame,
                 param_deltas: pd.DataFrame,

                 ) -> None:
        
        self.input_parameter_names = problem['names']
        self.input_parameter_bounds = problem['bounds']
        self.param_deltas = param_deltas
        # self.metric_name = metric_name
        
        self.output_sample_names = ["base"]

        for input_name in self.input_parameter_names:
            self.output_sample_names.append(f"{input_name}_min")
            self.output_sample_names.append(f"{input_name}_max")
            
    
        self.all_outputs = all_outputs
        
    # ============================
    def get_indices(self):
    
        df_metric = self.all_outputs.copy()

        # print(df_metric.head(10))

        abs_indices = pd.DataFrame()
        rel_indices = pd.DataFrame()
        
        
        for paramname in self.input_parameter_names:
            maxname = f"{paramname}max"
            minname = f"{paramname}min"
            
            abs_metric_deltas = df_metric[maxname] - df_metric[minname] # abs()
            rel_metric_deltas = abs_metric_deltas/ df_metric["base"]
            

            abs_indices[paramname] = abs_metric_deltas / self.param_deltas.loc[paramname]["delta_abs"]
            rel_indices[paramname] = rel_metric_deltas / self.param_deltas.loc[paramname]["delta_rel"]   
        
        return abs_indices, rel_indices
    
# =====================================================
if __name__ == "__main__":
    
    path_to_problem = "C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Sampling/problem.json"
    path_to_deltas = "C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Sampling/input_samples/base_deltas_local.txt"
    
    # Path to the solver output for the output of choice
    metric_name = "mean_pressure" # "pulse_pressure", "mean_flow", "pulse_flow"
    path_to_outputs = f"C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Solver/outputs/patch_0_{metric_name}.csv"
    
    path_to_save_SA_indices = "C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Sensitivity_analysis/local_indices_unordered"
    os.makedirs(path_to_save_SA_indices, exist_ok=True)
    
    
    with open(path_to_problem) as fo:
        problem = json.loads( fo.read() )   
    
    param_deltas = pd.read_csv(path_to_deltas, index_col = 0)   
    all_outputs = pd.read_csv(path_to_outputs, sep=",", index_col=0, header=None).T 
    
    objLocalSA = LocalSA(problem, all_outputs, param_deltas)
    
    abs_indices, rel_indices = objLocalSA.get_indices()        
    rel_indices.to_csv(os.path.join(path_to_save_SA_indices, f"{metric_name}.csv"))
