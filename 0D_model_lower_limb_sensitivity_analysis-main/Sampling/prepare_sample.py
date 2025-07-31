import numpy as np 
import pandas as pd 
import os


class PrepSample:
    def __init__(self,  analysis_params, df_vessels, df_acv, boundary_params):
        
        self.analysis_params = analysis_params
        
        self.df_og_vessels = df_vessels
        
        # Make a copy to avoid verwriting data
        self.df_vessels = self.df_og_vessels.copy() 
        self.df_acv = df_acv
        
        self.boundary_params = boundary_params
    
    # -----------------
    def update_vessels(self, df, parameter):
        """ 
        Add parameter to index of vessel dataframe
        The same indices are necessary to join columns from
        different dataframes
        """
        self.df_vessels.index=f"{parameter}" + self.df_vessels.index.astype(str)

        # Drop column with data of the parameter
        new_df_vessels = self.df_vessels.drop([parameter], axis = 1)
        
        

        # Add new values of that parameter as a column in vessel data
        new_df_vessels = pd.concat([new_df_vessels, df[parameter]], axis = 1)
        
        # Sample object vessel data reassigned
        self.df_vessels = new_df_vessels
        
        # Get the index back to the original one
        self.df_vessels.index = self.df_og_vessels.index.astype(str)
        
    
    # -----------------
    def update_boundaries(self, df, parameter):
        
        # This gets rid of first two string elems
        # it will work provided thatr we keep 'bc' as
        # acronym for boundary conditions
        df.index = df.index.str[2:] 
        
        for index, row in df.iterrows():
            self.boundary_params[index] = row[parameter]
            

    # -----------------
    def put_sample_in_data(self, sample):
        
        where_to_go = {
            "r": self.update_vessels,
            "L": self.update_vessels,
            "c0": self.update_vessels,
            "bc": self.update_boundaries
            }
        
        for parameter in self.analysis_params:
            keys = [k for k in sample.keys() 
                    if k.startswith(parameter)]
            
            vals = [sample[key] for key in keys]
                
            df = pd.DataFrame(index=keys)
            df[parameter] = vals
                
            where_to_go[parameter](df, parameter)
            
        
