import numpy as np 
import pandas as pd
import os
from get_resistance_and_capacitance import ResistanceCapacitance

class SetModel():
    def __init__(self, mu, rho, df_key, simtype, RC_vals):
        self.mu = mu
        self.rho = rho
        
        self.df_key = df_key.copy()
        self.type = simtype
        self.RC_vals = RC_vals      
                
        self.set_key_with_values()
        
    
    # =============================
    def set_key_with_values(self):
        self.df_key['C'] = self.df_key['R'].copy()
               
        # -----------------------
        for entry in self.df_key['R']:            
            if '+' in str(entry):
                foo = entry.replace('+', ' ').split()
                value = sum([self.RC_vals['R'][vessel] for vessel in foo])
            
            else:
                value = self.RC_vals['R'][entry]
                    
            self.df_key['R'] = self.df_key['R'].replace(entry, value)


        # -----------------------
        for entry in self.df_key['C']:
            
            if '+' in str(entry):
                foo = entry.replace('+', ' ').split()
                value=0
                for vessel in foo:
                    val = self.RC_vals['C'][vessel]
                    value += 1/val
                value = 1/value
                
            else: 
                value = self.RC_vals['C'][entry]
        
            self.df_key['C'] = self.df_key['C'].replace(entry, value)

    

