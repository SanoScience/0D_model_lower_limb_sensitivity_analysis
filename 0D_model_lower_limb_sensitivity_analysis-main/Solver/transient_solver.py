import pandas as pd
import numpy as np
import os
from ckt_function import TransientSystem

class RunSingleSample:
    def __init__(self, 
                 all_params: dict): 
        
        # parameters defining simulation e.g. boundary conditions parameters
        self.params = all_params['params']                         
        
        # Resistance and capacitance values for all model elements
        self.RC_vals = pd.DataFrame.from_dict(all_params['RC_vals'])
        
        # list of names of model elements
        self.elem_names = list(self.RC_vals['elem_name'])
        
        
    # ====================
    def converge_in_cycles(self):
        # Unpack parameters
        t0 = self.params['t0']            # Start the solver at t0
        tstep = self.params['tstep']      # Time step size
        kmax = self.params['kmax']        # Maximum number of cycles to run if convergence of all signals is not reached
        conv_th = self.params['conv_th']  # Convergence threshold (error between two consequitive cycles)
        
        # Period of the signal
        sig_T = 2/self.params['transient_boundary_params']['B']
        ts = t0 # ts means start time, set it to t0 as initial condition
        k = 1   # start cycles at 1 

        dp = str(tstep)[::-1].find('.')   # number of decimal places of tstep
        ts = np.round(ts, dp)             # round ts to the same no. of decimal places
        sig_T = np.round(sig_T, dp)       # round the period to that dp too
        Nsamp = int(sig_T / tstep)        # number of steps in one cycle

        # Initial conditions of the system - all 36 pressure signals at zero
        u0 = np.zeros(36)

        # -----------------------------------------------
        # Wait 3 cycles before checking for convergence
        while k < 4: 
            ts, k, u0, sol = self.single_call_to_solver(u0, ts, tstep, k, Nsamp, dp, self.params['transient_boundary_params'])
           
        # -----------------------------------------------
        # Check for convergence after every cycle from now on
        # Dataframe to store "error" values for each cycle
        df_error = pd.DataFrame()       
        
        
        while True:
            # solutions from previous step 
            prev_sol_y, prev_sol_t = sol.y, sol.t                                  
            
            # solve for 'current' step
            ts, k, u0, sol = self.single_call_to_solver(u0, ts, tstep, k, Nsamp, dp, self.params['transient_boundary_params'])
                   
            # colutions from current step
            current_sol_y, current_sol_t = sol.y, sol.t                 

            # List of errors between the last two cycles of the simulation
            error_list=[ 
                        np.sum(( 2 / (prev_sol_y[i,:] + current_sol_y[i,:])) * np.abs(prev_sol_y[i,:] - current_sol_y[i,:])) / (len(current_sol_t)) 
                        for i in range(len(current_sol_y)) 
                        ]
            
            df_error = pd.concat([df_error,  pd.Series(error_list).rename(k)], axis=1)

            # continue
                
        # if all(np.asarray(error_list) < conv_th):    
        #     conv = True 
        
        # # Put solutions of the last two cycles into dataframes
        # df_prev_sol = pd.DataFrame(prev_sol_y, columns = list(prev_sol_t))
        # df_curr_sol = pd.DataFrame(current_sol_y, columns = list(current_sol_t))    
            
        # bcs = self.params["transient_boundary_params"]
                
        # df_prev_flows = self.get_flows_for_single_sample( 
        #                                                 df_prev_sol,
        #                                                 self.RC_vals,
        #                                                 bcs
        #                                                 )
        
        # df_curr_flows = self.get_flows_for_single_sample( 
        #                                                 df_curr_sol,
        #                                                 self.RC_vals,
        #                                                 bcs
        #                                                 )   
            
        # # Take the average here from the last cycle/2cycles
        # pulse_flow = (df_curr_flows.max(axis=1) - df_curr_flows.min(axis=1)) #.to_numpy() #.to_dict()
        # pulse_pressure = (df_curr_sol.max(axis=1) - df_curr_sol.min(axis=1)) #.to_numpy() #.to_dict()
        
        # mean_flow = df_curr_flows.mean(axis=1)   #.to_numpy()    #.to_dict()
        # mean_pressure = df_curr_sol.mean(axis=1) #.to_numpy()  #.to_dict()
        
        # return mean_flow, pulse_flow, mean_pressure, pulse_pressure, conv    
    
            if all(np.asarray(error_list) < conv_th):
                
                """ 
                Convergence reached for all pressures
                Errors for all signals below the convergence threshold
                """
                conv=True # convergence occured
                
                # Put solutions of the last two cycles into dataframes
                df_prev_sol = pd.DataFrame(prev_sol_y, columns = list(prev_sol_t))
                df_curr_sol = pd.DataFrame(current_sol_y, columns = list(current_sol_t))
                
                # print(df_prev_sol)
                
                # quit()
                # # Turn dataframes into dictionaries
                # dcurr_sol = df_curr_sol.to_dict()
                # dprev_sol = df_prev_sol.to_dict()
                # 
                
        
                bcs = self.params["transient_boundary_params"]
                
                df_prev_flows = self.get_flows_for_single_sample( 
                                                             df_prev_sol,
                                                             self.RC_vals,
                                                             bcs
                                                             )
                
                df_curr_flows = self.get_flows_for_single_sample( 
                                                             df_curr_sol,
                                                             self.RC_vals,
                                                             bcs
                                                             )
                
                
                df_prev_sol = df_prev_sol.iloc[:,:-1]
                df_prev_flows = df_prev_flows.iloc[:,:-1]
                
                
                df_press = pd.concat([df_prev_sol, df_curr_sol], ignore_index=False, axis=1)
                df_flows = pd.concat([df_prev_flows, df_curr_flows], ignore_index=False, axis=1)
                
                # return df_press, df_flows
                prev_flow = df_prev_flows.to_dict()
                curr_flow = df_curr_flows.to_dict()
                
                # Take the average here from the last cycle/2cycles
                pulse_flow = (df_curr_flows.max(axis=1) - df_curr_flows.min(axis=1)) #.to_numpy() #.to_dict()
                pulse_pressure = (df_curr_sol.max(axis=1) - df_curr_sol.min(axis=1)) #.to_numpy() #.to_dict()
                
                mean_flow = df_curr_flows.mean(axis=1)   #.to_numpy()    #.to_dict()
                mean_pressure = df_curr_sol.mean(axis=1) #.to_numpy()  #.to_dict()
                
                return mean_flow, pulse_flow, mean_pressure, pulse_pressure, conv
                
                
                # ###### Return as dictionaries ######

                # derr = df_error.to_dict()
                # return {"mean_flow": mean_flow, "mean_pressure": mean_pressure, "pulse_flow": pulse_flow, "pulse_pressure": pulse_pressure, "conv":conv, "error":derr}
                # #####################################
                
                # Return nested dictionary
                # return {"curr_pressure":dcurr_sol, "prev_pressure":dprev_sol, "error":derr, "conv":conv, "curr_flow":curr_flow, "prev_flow":prev_flow}
    
            elif k == kmax:
                """
                Maximum number of cycles reached without reaching convergence
                """
                conv=False    # convergence did not happen
                
                # Put solutions of the last two cycles into dataframes
                df_prev_sol = pd.DataFrame(prev_sol_y, columns = list(prev_sol_t))
                df_curr_sol = pd.DataFrame(current_sol_y, columns = list(current_sol_t))
                
                # # Turn dataframes into dictionaries
                # dcurr_sol = df_curr_sol.to_dict()
                # dprev_sol = df_prev_sol.to_dict()
                
                
                
                bcs = self.params["transient_boundary_params"]
                
                df_prev_flows = self.get_flows_for_single_sample( 
                                                             df_prev_sol,
                                                             self.RC_vals,
                                                             bcs
                                                             )
                
                df_curr_flows = self.get_flows_for_single_sample( 
                                                             df_curr_sol,
                                                             self.RC_vals,
                                                             bcs
                                                             )
                
                df_prev_sol = df_prev_sol.iloc[:,:-1]
                df_prev_flows = df_prev_flows.iloc[:,:-1]
                
                # print(list(df_prev_sol.columns)[-1])
                # print(list(df_curr_sol.columns)[-1])
                
                # quit()
                # df_press = pd.concat([df_prev_sol, df_curr_sol], ignore_index=False, axis=1)
                # df_flows = pd.concat([df_prev_flows, df_curr_flows], ignore_index=False, axis=1)
                
                # return df_press, df_flows
                
                # prev_flow = df_prev_flows.to_dict()
                # curr_flow = df_curr_flows.to_dict()
                
                # Take the average here from the last cycle/2cycles
                pulse_flow = (df_curr_flows.max(axis=1) - df_curr_flows.min(axis=1)) #.to_numpy() #.to_dict()
                pulse_pressure = (df_curr_sol.max(axis=1) - df_curr_sol.min(axis=1)) #.to_numpy() #.to_dict()
                
                mean_flow = df_curr_flows.mean(axis=1)   #.to_numpy()    #.to_dict()
                mean_pressure = df_curr_sol.mean(axis=1) #.to_numpy()  #.to_dict()
                
                return mean_flow, pulse_flow, mean_pressure, pulse_pressure, conv
                
                
                # ###### Return as dictionaries ######

                # derr = df_error.to_dict()
                
                # return {"mean_flow": mean_flow, "mean_pressure": mean_pressure, "pulse_flow": pulse_flow, "pulse_pressure": pulse_pressure, "conv":conv, "error":derr}
                # #####################################
                
                
                # Return nested dictionary
                # return {"curr_pressure":dcurr_sol, "prev_pressure":dprev_sol, "error":derr, "conv":conv, "curr_flow":curr_flow, "prev_flow":prev_flow}
    
    # =========================
    def get_flows_for_single_sample(self, 
                                    sample_of_pressures: pd.DataFrame, 
                                    RC_vals: dict, 
                                    bcs: dict):

        objSystem = TransientSystem('ppflow', RC_vals)
        
        sample_array = sample_of_pressures.T.to_numpy()
        time_points = np.asarray(list(sample_of_pressures.columns.astype(float)))
        sample_array_with_t = np.c_[ sample_array, time_points ] 

        flows = np.asarray([ 
                            objSystem.system( row[-1], row[0:-1], bcs ) 
                            for row in sample_array_with_t
                            ])
        
        return pd.DataFrame(flows.T, columns = time_points)
    
          
    # ====================
    def single_call_to_solver(self, 
                    u0, 
                    ts: float, 
                    tstep: float, 
                    k: int, 
                    Nsamp: int, 
                    decimal_places: int,
                    boundary_params: dict):
        
        
        # tf is rounded to the no. decimal places determined by tstep accuracy
        tf = np.round(tstep * Nsamp * k, decimal_places) 
        
        
        # Call class with the system of equations
        objSystem = TransientSystem( 
                                    'solver',     # the system is called as equations to the solver, another option is post-processing flow
                                    self.RC_vals
                                    )
        # solve the system
        sol = objSystem.solve_system_num( u0, ts, tf, Nsamp, decimal_places, boundary_params)
        

        # the last solution becomes new initial conditions
        new_u0 = sol.y[:,-1]          
        
        k += 1      # move to the next cycle
        ts = tf     # last time point becomes new starting time point for the next cycle
        
        return(ts, k, new_u0, sol)
