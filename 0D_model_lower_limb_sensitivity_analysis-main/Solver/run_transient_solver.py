import numpy as np
import pandas as pd 

import os
import json
from csv import writer
from tqdm import tqdm

from prepare_sample import PrepSample
from get_resistance_and_capacitance import ResistanceCapacitance
from set_model import SetModel

from transient_solver import RunSingleSample


class ExecuteSamples:
    def __init__(self, 
                 setup: dict,
                 problem: dict,
                 path_to_input_data: str,
                 path_to_SA_input_samples: str,
                 path_to_save_code_outputs: str

                 ) -> None:
        
        self.path_to_input_data = path_to_input_data
        self.simulation_setup_params = setup
        
        # Number of packs to split input parameter samples
        self.N_containers = self.simulation_setup_params["N_containers"]
        
        # Get sensitivity analysis type (local or global)
        self.type = self.simulation_setup_params['type']


        # Unit system to operate in 
        unit_factor: dict[str, float] = { 
                                         "SI" : {"value": 133000000,
                                                 "type": "acv"},
                                         }
        
        self.unit_conversion_factor = unit_factor[self.simulation_setup_params['units']]
        

        # Parameters of bounary condition functions
        self.boundary_conditions_params = self.simulation_setup_params['transient_boundary_params']

        self.initcondpath = path_to_input_data
                
        self.problem = problem                
        self.preprocesspath = path_to_input_data
        self.samplpath = path_to_SA_input_samples
        

        # Path to output samples
        self.outpath = path_to_save_code_outputs
        os.makedirs(self.outpath, exist_ok=True)
        
        
        # ===============================================================================================================
        # Load vessel data
        self.df_og_vessels = pd.read_csv(f"{self.preprocesspath}/df_vessels.txt", header=0, index_col=0)
        self.df_og_vessels = self.df_og_vessels.set_index('vessel_no')
        
        self.df_og_acv = pd.read_csv(f"{self.preprocesspath}/df_acv.txt", header=0, index_col=0)
        
        self.df_og_key = pd.read_csv(f"{self.initcondpath}/key.txt", sep='\t', names=['elem_name', 'R']).astype(str)
        self.df_og_key['R'] = self.df_og_key['R'].astype(str)
   
        
    # ==========================
    def get_one_sample_for_analysis(self, raw_sample, df_vessels, df_acv, df_key):
        sample = pd.Series(raw_sample) 
        

        objSample = PrepSample( 
                                self.simulation_setup_params['analysis_params'],
                                df_vessels, 
                                df_acv, 
                                self.simulation_setup_params['transient_boundary_params']
                                )
        
        objSample.put_sample_in_data(sample)
        
        # Change parameters of boundary conditions
        self.simulation_setup_params['transient_boundary_params'] = objSample.boundary_params
                    
        # Vessel and capillary beds data >> needed to calculate RC values
        sampl_df_vessels =  objSample.df_vessels    
        sampl_df_vessels['vessel_no'] = sampl_df_vessels.index
        
        sampl_df_acv =  objSample.df_acv
        
        
        #----------------------       
        # Calculate RC_values for the sample
        RC_vals = ResistanceCapacitance( 
                                        self.simulation_setup_params, 
                                        sampl_df_vessels, 
                                        sampl_df_acv,
                                        self.unit_conversion_factor, 
                                        ).calculate()     

        #----------------------
        # Set model - assign vessels to model elements
        objSet = SetModel( 
                          self.simulation_setup_params['constants']['mu'],
                          self.simulation_setup_params['constants']['rho'],
                          df_key,
                          'transient',
                          RC_vals
                          )
        
        
        # df_model contains R and C values 
        df_model = objSet.df_key
        
        # Combine parameters setting up the analysis with RC values for all elements into nested dictionary
        params_send_to_model = {}
        params_send_to_model['params'] = self.simulation_setup_params
        params_send_to_model['RC_vals'] = df_model.to_dict()
        
        return params_send_to_model
    
    
    #==========================
    def merge_sample_and_run_patch(self, path_to_inputs, patch_id):       
        
        # Read in parameter sample patch
        patch_of_samples = pd.read_csv(f"{path_to_inputs}", header=0, index_col=0)
        
        paramnames = list(patch_of_samples.columns)        
        output_file = os.path.join(self.outpath, f"output_patch_{patch_id}.json")
                
        if os.path.isfile(output_file):
            os.remove(output_file)
        
        for row in tqdm(patch_of_samples.itertuples(), total=len(patch_of_samples)):
                
            param_sample = {key: value for key, value in zip(paramnames, list(row[1:]))}
        
            full_sample = self.get_one_sample_for_analysis(
                param_sample,
                self.df_og_vessels.copy(),
                self.df_og_acv.copy(),
                self.df_og_key.copy()
            )
                                    
            full_sample['id'] = row.Index
            
            
            ########################
            # Run TRANSIENT solver
            ########################
            self.transient_executor(full_sample, patch_id)
                   

    # ===================================
    def transient_executor(self, sample, patch_id):
        mean_flow, pulse_flow, mean_pressure, pulse_pressure, conv = RunSingleSample(sample).converge_in_cycles()
        
        # id = int(sample['id']) # works for global
        id = str(sample['id'])   # works for local
        
        # --------------------------------------------
        mf_file = f"{self.outpath}/patch_{patch_id}_mean_flow.csv"
        mp_file = f"{self.outpath}/patch_{patch_id}_mean_pressure.csv"
        
        pf_file = f"{self.outpath}/patch_{patch_id}_pulse_flow.csv"
        pp_file = f"{self.outpath}/patch_{patch_id}_pulse_pressure.csv"
        
        conv_file = f"{self.outpath}/patch_{patch_id}_convergence.csv" 
        # err_file = f"{self.outpath}/patch_{patch_id}_error.csv"
        
        # --------------------------------------------
        mf = pd.DataFrame(mean_flow, columns=[id]).T   #.round(6)
        pf = pd.DataFrame(pulse_flow, columns=[id]).T  #.round(6)
        
        mp = pd.DataFrame(mean_pressure, columns=[id]).T   #.round(6)
        pp = pd.DataFrame(pulse_pressure, columns=[id]).T  #.round(6)
        
        conv_bool = pd.DataFrame([conv], columns=[id]).T
        # err = pd.DataFrame(df_error, columns=[id]).T
        
        
        # --------------------------------------------
        mf.to_csv(mf_file, mode='a', header=False)
        pf.to_csv(pf_file, mode='a', header=False)
        
        mp.to_csv(mp_file, mode='a', header=False)
        pp.to_csv(pp_file, mode='a', header=False)
        
        # err.to_csv(err_file, mode='a', header=False)
        conv_bool.to_csv(conv_file, mode='a', header=False)
        
  
    # ====================
    def run(self):
        sample_patches_files = [file for file in os.listdir(self.samplpath) if "samples_patch" in file]
        
        for filename in sample_patches_files:
            
            patch_id = filename.split("_")[2].split(".")[0]
            filepath = os.path.join(self.samplpath, filename)

            self.merge_sample_and_run_patch(filepath, patch_id)
            

        
# ===================================================
if __name__ == "__main__":
    
    path_to_input_data = "C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/input_data/" 
    path_to_problem = "C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Sampling/problem.json"
    
    path_to_SA_input_samples ="C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Sampling/input_samples"
    path_to_save_code_outputs = "C:/Users/MagdalenaOtta/Documents/0D_SA_publication_FV/Solver/outputs"
    
    # ------------------------
    # Read in setup file
    with open(os.path.join(path_to_input_data, "setup.json")) as fr:
        setup = json.loads(fr.read())
    
    # ------------------------
    # Read in problem file
    with open(path_to_problem) as fr:
        problem = json.loads(fr.read())
    
    
    objExec = ExecuteSamples(setup, problem, path_to_input_data, path_to_SA_input_samples, path_to_save_code_outputs)
    objExec.run()
