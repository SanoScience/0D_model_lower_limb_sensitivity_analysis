
'''
> df_vessels: vessel data e.g.
|vessel number|length|radius| >> df 

> df_acv: capillary beds data
|acv name|'elem_name'|'Rda'|'Ral'|'Lal'|'Cal'|'Rcp'|'Lcp'|'Ccp'|'Rvn'|'Lvn'|'Cvn'|
(like in Muller and Toro paper)

'''
import numpy as np 
import pandas as pd
import json 
import os

class ResistanceCapacitance:
        
    #====================
    def __init__(self, setup_parameters, 
                 vessel_parameters, 
                 acv_parameters,
                 unit_change 
                ):
        '''
        Remember to pass dataframes in consistent units (!!!) 
        units conversion to desired state
        '''
        self.setup_parameters = setup_parameters    # setup_parameters of the simulation: constants & types of analysis to perform
        self.vessel_parameters = vessel_parameters  # vessel data, in a form of a dataframe
        self.acv_parameters = acv_parameters        # capillary beds data, in a form of a dataframe
        
        self.units_change = unit_change
        
    #====================
    # Calculate resistance of capillary beds
    def capillary_beds_resistance(self, R_vals):
        return sum(R_vals)
        
    
    #====================
    # Calculate capacitance of capillary beds
    def capillary_beds_capacitance(self, C_vals):
        return sum(C_vals)
    
    
    #====================
    # Calculate vessel resistance from Poiseuille's assumption
    def poiseuille_resistance(self, L: float, r: float) -> float:
        return (8 * self.setup_parameters['constants']['mu'] * L) / (np.pi * r**4)
    
        
    #====================
    # Calculate capacitance of vessels
    def vessel_capacitance(self, c0: float, L: float, r: float) -> float:
        """_summary_
        c0 - wave speed
        L - vessel length
        r - vessel radius
        """
        A = self.setup_parameters['constants']['rho'] / np.pi        
        return 1 / (A* c0**2 * L**(-1) * r**(-3/2))


    #====================
    def calculate(self):   
        # -------------------------------     
        # Calculate vessel resistance
        self.vessel_parameters['R'] = self.poiseuille_resistance(self.vessel_parameters['L'], 
                                                                 self.vessel_parameters['r'])
        
        # Calculate vessel capacitance; based on wave speed c0
        self.vessel_parameters['C'] = self.vessel_capacitance(self.vessel_parameters['c0'], 
                                                              self.vessel_parameters['L'], 
                                                              self.vessel_parameters['r'])
                
        # -------------------------------
        # Capillary resistances to include in calculations
        acvR_vals = (self.acv_parameters['Ral'], # aterioled
                     self.acv_parameters['Rcp'], # capillaries
                     self.acv_parameters['Rvn'], # venules
                     self.acv_parameters['Rda']) # distal

        # Capillary capacitance to include in calculations
        acvC_vals = (self.acv_parameters['Cal'], # aterioled
                     self.acv_parameters['Ccp'], # capillaries
                     self.acv_parameters['Cvn']) # venules
                     
        # Calculate resistance and capacitance of capillary beds
        self.acv_parameters['R'] = self.capillary_beds_resistance(acvR_vals)
        self.acv_parameters['C'] = self.capillary_beds_capacitance(acvC_vals)
        
        # -------------------------------
        # Change units
        if self.units_change["type"] == "acv":                        
            self.acv_parameters['R'] = self.acv_parameters['R'] * self.units_change["value"]
            self.acv_parameters['C'] = self.acv_parameters['C'] * 1 / self.units_change["value"]
            
        
        elif self.units_change["type"] == "vessels":
            self.acv_parameters['R'] = self.vessel_parameters['R'] * self.units_change["value"]
            self.vessel_parameters['C']  = self.vessel_parameters['C'] * 1 / self.units_change["value"]
        
        
        
        # =================================
        # Combine data into dictionaries
        
        # Vessel resistance
        vessel_keys = list(self.vessel_parameters['vessel_no'].astype(str))
        R_vals_vessels = list(self.vessel_parameters['R'].astype(float))
        R_vals_dict: dict[str, float] = dict(zip(vessel_keys, R_vals_vessels))
        
        # Capillary beds' resistance
        acv_keys = list(self.acv_parameters['elem_name'].astype(str))
        R_vals_acv = list(self.acv_parameters['R'].astype(float))
        R_vals_acv_dict: dict[str, float] = dict(zip(acv_keys, R_vals_acv))
        
        # ... in a common dictionary for resistance
        R_vals_dict.update(R_vals_acv_dict)
        
        # Vessel capacitance
        C_vals_vessels = list(self.vessel_parameters['C'].astype(float))
        C_vals_dict: dict[str, float] = dict(zip(vessel_keys, C_vals_vessels))
        
        # Capillary beds' capacitance
        C_vals_acv = list(self.acv_parameters['C'].astype(float))
        C_vals_acv_dict: dict[str, float] = dict(zip(acv_keys, C_vals_acv))
        
        # ... in a common dictionary cor capacitance
        C_vals_dict.update(C_vals_acv_dict)
        
        # Nested dictionary for RC values
        RC_dict = {}
        RC_dict['R'] = R_vals_dict
        RC_dict['C'] = C_vals_dict
        
        
        return RC_dict

        
# # =========================
# if __name__ == "__main__":
#     setup_params: dict[str, float] = {
#         "mu": 0.0035,
#         "rho": 1050.0
#     }
    
#     vessel_data = pd.read_csv("pre_processed/df_og_vessels.txt", header=0, index_col=0)
#     acv_data = pd.read_csv("pre_processed/df_og_acv.txt", header=0, index_col=0)
    
#     path = "test/RC_vals"
    
#     RC_vals = ResistanceCapacitance(setup_params, vessel_data, acv_data, path).calculate()

        