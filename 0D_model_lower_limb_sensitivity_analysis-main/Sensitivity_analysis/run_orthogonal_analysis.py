import pandas as pd 
import numpy as np 
import os
import json
import seaborn as sns 
import matplotlib.pyplot as plt


class Orthogonality:
    
    # ---------------------------
    def __init__(self, path_to_file, title, plotpath):

        df_input = pd.read_csv(path_to_file, index_col = 0, header=0)       
        df_indices = df_input.T        
        df_indices = df_indices.drop("r160", axis=0)
        
        input_param_names = list(df_indices.index)
        
        # Turn dataframe into numpy array
        array_indices= df_indices.to_numpy()
                    
        # Prepare an array of zeros to fill in with orthogonal indices
        array_ortho = np.zeros((len(input_param_names),len(input_param_names)))
        

        # Calculate orthogonal sensitivity by iterating over sensitivity vectors for every input parameter
        # get a normalised inner product of each vector with every other vector
        for i in range(len(input_param_names)):
            vi = array_indices[i,:]

            for j in range(len(input_param_names)):
                vj = array_indices[j,:]

                array_ortho[i,j] = self.calculate_normalised_inner_product(vi, vj)

        # Turn the array into dataframe, to add names of parameters
        df = pd.DataFrame(array_ortho, index = input_param_names, columns = input_param_names)

        
        df_reversed = df.loc[::-1]

        title_2 = title.replace(" ", "_")
        
        figpath = os.path.join(plotpath, title_2)
        fig_filename = f'{figpath}.pdf'
            
        data_filename = f"{figpath}.csv"
        
        df_reversed.to_csv(data_filename)
                    
            
        fig = plt.figure(figsize=(18,7))
        plt.suptitle(title)              # Add title above all subplots       
        
        plt.subplot(122) # Plot second subplot; (122) means one row, two columns, plot #2
        
        ax = sns.heatmap( 
                    df_reversed,               # Plot dataframe as a heatmap
                    vmin = 0,        # Set limits of the colourbar
                    vmax = 1,
                    cmap = "viridis", # color palettee of the heatmap
                    xticklabels=True, # Keep all x and y-labels
                    yticklabels=True,
                    # linewidths=0.1,
                    linecolor='white',
                    # mask=mask
                    )
    
        plt.subplot(121) # Plot first subplot; (122) means one row, two columns, plot #1
        plt.hist(df.to_numpy().flatten(), range = (-1, 1), bins = 20)
        
        
        # Save figure
        plt.tight_layout()
        

        plt.savefig(fig_filename, format ='pdf', bbox_inches="tight", dpi=600) #dpi = 300
        

    # ---------------------------
    # For the ith input parameter
    def calculate_normalised_inner_product(
        self, 
        vi: np.array, 
        vj: np.array
        ):
        
        # Dot product 
        numerator = np.dot(vi, vj) 
        # Multiplication of the norms of vectors vi and vj
        denominator = np.linalg.norm(vi)*np.linalg.norm(vj) 
        
        # Return normalised inner product
        return numerator / denominator




# =======================
if __name__=="__main__":
    title = "pulse pressure (t) global"
    path = f"C:/Users/MagdalenaOtta/Documents/0D_SA_for_publication_FV/data/pulse_pressure_S1_transient_data_ordered.txt"
    
    plotpath = f"C:/Users/MagdalenaOtta/Documents/0D_SA_for_publication_FV/data/orthoplots"
    os.makedirs(plotpath, exist_ok=True)
    
    obj = Orthogonality(path, title, plotpath)

