# Import necessary libaries
import numpy as np
import pandas as pd 
import os
import json 

from tqdm import tqdm
from SALib.sample import saltelli

# Import classes from other files
from prepare_sample import PrepSample
from get_resistance_and_capacitance import ResistanceCapacitance
from set_model import SetModel


class GenerateSamples:
    def __init__(self, 
                 setup: dict, 
                 path_to_save: str,
                 path_to_input_data: str
                 ):
        
        self.simulation_setup_params = setup
        

        # Number of packs to split input parameter samples
        self.N_containers = self.simulation_setup_params["N_containers"]

        # Get sensitivity analysis type (local or global)
        self.type = self.simulation_setup_params['type']


        # Unit system to operate in - currently only SI
        unit_factor: dict[str, float] = { 
                                         "SI" : {"value": 133000000,
                                                 "type": "acv"},
                                         }
        
        self.unit_conversion_factor = unit_factor[self.simulation_setup_params['units']]
        
        
        # Parameters of bounary condition functions
        self.boundary_conditions_params = self.simulation_setup_params['transient_boundary_params']
        
        # Path to save problem file & output of the sampling
        self.path_to_save = path_to_save

        self.path_to_input_data = path_to_input_data
              

        self.samplpath = f"{self.path_to_save}/input_samples"
        os.makedirs(self.samplpath, exist_ok=True)
        

    
    #====================
    def set_analysis_vector(self):
        # Empty dictionary to append SA parameters to
        analysis_params: dict[str, float] = {}
        
        # Read in pre-processed vessel data into a dataframe
        df_vessels = pd.read_csv(f"{self.path_to_input_data}/df_vessels.txt", header=0, index_col=0)
        df_vessels = df_vessels.set_index("vessel_no")
        
        
        """
        All vessel parameters and boundary conditions' parameters are
        put into 'parameters_dictionary'
        """
        
        # Turn the dataframe into dictionary
        parameters_dictionary = df_vessels.to_dict()

        # Add boundary conditions parameters to the dictionary
        parameters_dictionary['bc'] = self.boundary_conditions_params
        

        """
        Chosen parameters are put into 'analysis_params' dictionary 
        """
        # Take the chosesn analysis parameter types and extract them from the data sets into 
        # analysis params dictionary
        for parameter in self.simulation_setup_params['analysis_params']:
            
            names = [ 
                     parameter + str(key) 
                     for key in parameters_dictionary[parameter].keys()
                     ]
            
            vals = list(parameters_dictionary[parameter].values())
            
            for name, val in zip(names, vals):
                analysis_params[name] = val
        
        
        # Save analysis parameters to a json file
        with open(f"{self.path_to_input_data}/analysis_params.json", "w") as fp:
            json.dump(analysis_params, fp, indent = 4)
            
    #====================
    # Pre-processing data into sensitivity analysis problem
    # saved as a json for both local and sobol analysis
    def pre_process_analysis(self): 
        
        # Read in parameters for sensitivity analysis
        with open(f"{self.path_to_input_data}/analysis_params.json") as f:
            analysis_params = json.loads(f.read())      

        # Create a list of bounds of parameters for sensitivity analysis
        bounds = [ 
                  [val * (1 - self.simulation_setup_params['bound']), val * (1 + self.simulation_setup_params['bound'])] 
                  for val in analysis_params.values()
                  ]
        
        # Define SA problem (as required by SALib, but kept the same for local analysis)
        problem = {
                    'num_vars': len(analysis_params),
                    'names': list(analysis_params.keys()),
                    'bounds': bounds
                  }
        
        self.problem = problem
        
        with open(f"{self.path_to_save}/problem.json", "w") as fp:
            json.dump(problem, fp, indent = 4)

            
        
    #====================
    # Generate sensitivity analysis samples based on problem 
    def generate_parameters(self):
        """
        The function reads in SA problem and vector of parameters included in SA.
        
        self.type determines analysis type (e.g. local or global), based on this, 
        either local or global sample generatror is called. 
        
        Global samples are created using SALib saltelli sequence. 

        """
        problem = self.problem
        
        # Read in necessary data
        with open(f"{self.path_to_save}/problem.json") as fp:
            problem = json.loads(fp.read())
        
        with open(f"{self.path_to_input_data}/analysis_params.json") as f:
            analysis_params = json.loads(f.read())
            

        # Names of parameters involved in the analysis
        param_names = list(analysis_params.keys())
               
      
        #----------------------
        # Sobol samples generation with SAlib
        def generate_sobol():
            samples = pd.DataFrame( 
                                   saltelli.sample( 
                                                   problem, 
                                                   2**self.simulation_setup_params['n'], 
                                                   calc_second_order = True
                                                   ), 
                                   columns = param_names
                                   )
            
            return (samples)
            
        
        #----------------------
        # Local SA samples generation
        def generate_local():
            # Dataframe to store samples
            df = pd.DataFrame(index = param_names, columns = ['base'])
            
            df['base'] = list(analysis_params.values())
            
            
            df['min_param'] = [ bound[0] for bound in problem['bounds'] ]
            df['max_param'] = [ bound[1] for bound in problem['bounds'] ]
            
            delta_abs = df['max_param'] - df['min_param']
            delta_rel = delta_abs / df['base']
            
            # Add delta columns to df dataframe
            df = pd.concat([df, delta_abs.rename('delta_abs')], axis = 1)
            df = pd.concat([df, delta_rel.rename('delta_rel')], axis = 1)
            

            df.to_csv(f"{self.samplpath}/base_deltas_local.txt")
            
            
            # Prepare dataframe for samples
            samples = pd.DataFrame(index = param_names)
            samples['base'] = df['base'].copy()
            
            # Iterate over parameters, to create samples
            for parameter in tqdm(param_names):
                # Names of min and max sample
                min_name = f'{parameter}min' 
                max_name = f'{parameter}max'
                

                # Copy base values to a new column
                samples = pd.concat([samples, samples['base'].rename(min_name)], axis = 1)
                samples = pd.concat([samples, samples['base'].rename(max_name)], axis = 1)
                
                # Replace relevant parameter with its min or max value
                samples[min_name].loc[parameter] = df['min_param'].loc[parameter]
                samples[max_name].loc[parameter] = df['max_param'].loc[parameter]
            

            # Transpose >> each row is a sample (vector of params) to run 
            return (samples.T)

        #----------------------
        # Call function depending on the type of analysis being performed  
        func_map = {
                    "global": generate_sobol, 
                    "local": generate_local
                    }

        samples = func_map[self.type]()
        
        # =======================
        # split between files here
        
        def round_up(number): 
            return int(number) + (number % 1 > 0)
        
        init_samples_per_container = len(samples.index) /self.N_containers
        samples_per_container = round_up(init_samples_per_container)
    
        
        for nc in range(self.N_containers):
            container_df = samples[nc*samples_per_container:(nc+1)*samples_per_container]
            
            if int(nc == self.N_containers): 
                container_df = samples[nc*samples_per_container:-1]
                
            container_df.to_csv(f"{self.samplpath}/samples_patch_{nc}.txt")


if __name__ ==  "__main__" :    
    path_to_setup_file = "./input_data/setup.json"
    
    path_to_save_code_outputs = "./Sampling/"
    
    path_to_input_data = "./input_data/"
    
    
    
    # ------------------------
    # Read in setup file
    with open(path_to_setup_file) as fr:
        setup = json.loads(fr.read())
    
    
   
    objMain = GenerateSamples(
        setup,
        path_to_save_code_outputs,
        path_to_input_data,
        
        
        )

    objMain.set_analysis_vector()         # call function extracting relevant parameters from data
    objMain.pre_process_analysis()        # pre-proces sens. analysis

    objMain.generate_parameters()         # generate input samples for SA
