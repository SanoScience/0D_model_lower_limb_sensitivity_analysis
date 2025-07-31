import pandas as pd
import numpy as np
import os

'''
This code merges patches of outputs for 4 specific output metrics of the model:
- mean_flow
- pulse_flow
- mean_pressure
- pulse_pressure


You need to provide path to directory where the output patches are saved
and a path to directory where the merged patches for the same output should be saved (this directory doesn't have to exist prior to running the script). 
'''


# -----------------------------------
def merge_single_metric(list_of_filenames, metric_name, path_to_output_patches, merged_output_directory):
    
    os.makedirs(merged_output_directory, exist_ok=True)

    list_of_df = []
    merged_data = pd.DataFrame()
    for filename in list_of_filenames:       
        df = pd.read_csv(os.path.join(path_to_output_patches, filename), index_col=0, header=None)
        list_of_df.append(df)
        
    merged_data = pd.concat(list_of_df)

    path = os.path.join(merged_output_directory, f"merged_output_{metric_name}.csv")
    merged_data.to_csv(path) # index=False
        

# -----------------------------------
def merge(path_to_output_patches, path_to_merged_output):

    # List of CSV file names to merge
    filenames_mean_flow = [file for file in os.listdir(path_to_output_patches) if "patch" in file and "mean_flow" in file]
    filenames_pulse_flow = [file for file in os.listdir(path_to_output_patches) if "patch" in file and "pulse_flow" in file]

    filenames_mean_pressure = [file for file in os.listdir(path_to_output_patches) if "patch" in file and "mean_pressure" in file]
    filenames_pulse_pressure = [file for file in os.listdir(path_to_output_patches) if "patch" in file and "pulse_pressure" in file]


    merge_single_metric(filenames_mean_flow, "mean_flow", path_to_output_patches, path_to_merged_output)
    merge_single_metric(filenames_pulse_flow, "pulse_flow", path_to_output_patches, path_to_merged_output)
    merge_single_metric(filenames_mean_pressure, "mean_pressure", path_to_output_patches, path_to_merged_output)
    merge_single_metric(filenames_pulse_pressure, "pulse_pressure", path_to_output_patches, path_to_merged_output)
    
    
    
if __name__ == "__main__":
    
    path_to_outputs = "C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Solver/outputs"

    # Path to where merged patches should go
    path_to_merged_output = "C:/Users/MagdalenaOtta/Documents/0D_SA_for_publication_FV/Solver/merged_outputs"
    # os.makedirs(path_to_merged_output, exist_ok=True)
    

    merge(path_to_outputs, path_to_merged_output)
