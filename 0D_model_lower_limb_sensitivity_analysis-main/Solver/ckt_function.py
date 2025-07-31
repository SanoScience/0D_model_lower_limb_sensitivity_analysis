import numpy as np 
import pandas as pd
import os

from math import *

from scipy.integrate import solve_ivp 




class TransientSystem:
    def __init__(self, type, RC_vals):
        self.type=type
        params = RC_vals
                
        # Dictionaries storing values of resistance and capacitance for all elements
        self.Rs = {str(k): float(v) for (k,v) in zip(list(params['elem_name']), list(params['R']))}
        self.Cs = {str(k): float(v) for (k,v) in zip(list(params['elem_name']), list(params['C']))}
        
        self.elem_names = list(params['elem_name'])
       
    # ---------------------------
    def boundary_conditions(self, t, bcs):
        #Vin =( 0.2*np.sin(3*np.pi*t)+ (1-np.exp(-1.5*t)) )*80*133 
        
        A, B, D = bcs['A'], bcs['B'], bcs['D']
        
        # General components of the input signal
        def sinewave(A,B):
            return A * np.sin(B * np.pi * t)
            
        def exponent(D):
            return 1 - np.exp(-D * t)
        

        Vin = 80 * 133 * ( sinewave(A, B) + exponent(D))
        Vout1, Vout2, Vout3 = 0, 0, 0
        
        dic = {'Vin': Vin, 'Vout1': Vout1, 'Vout2': Vout2, 'Vout3': Vout3}       
        
        return(dic)
    
    # ---------------------------
    def solve_system_num(self, u0, t0, tf, Nsamp, dp, bcs):               
        
        # Time points to evaluate the solution
        teval = np.linspace(t0, tf, Nsamp ).round(dp)
        # The solver requires to also provide the span of the time domain
        tspan = [t0, tf]

        # Wrapper for the solver, since the solver itself does not allow functions 
        # with arguments, not very elegant, but there is no other solution to this right now
        def wrapper(t,u):
            return self.system(t, u, bcs)

        # Solver itself, calls the wrapper
        sol = solve_ivp( 
                        wrapper, 
                        t_span = tspan, 
                        t_eval = teval, 
                        y0 = u0,            # Initial conditions vector
                        method="Radau",     # Integration method
                        vectorized=True     # This is only relevant for some methods
                        )
        
        ##'RK45', 'DOP853', 'Radau'
        
        # print(f"Sol status: {sol.status}")
        return sol
    
    # ---------------------------
    def system(self, t, u, bcs):
        BCs = self.boundary_conditions(t, bcs)
        Vin = BCs['Vin']
        Vout1 = BCs['Vout1']
        Vout2 = BCs['Vout2']
        Vout3 = BCs['Vout3']
        
        Rs=self.Rs
        Cs=self.Cs
        
        V0  = u[0]
        V1L = u[1];
        V1R = u[2];
        V2L = u[3];
        V2R = u[4];
        V3L = u[5];
        V3R = u[6];
        V4L = u[7]
        V4R = u[8]
        V5L = u[9]
        V5R = u[10]
        V6L = u[11]
        V6R = u[12]
        V7L = u[13]
        V7R = u[14]
        V8L = u[15]
        V8R = u[16]
        V9L = u[17]
        V9R = u[18]
        V10L = u[19]
        V10R = u[20]
        V11L = u[21]
        V11R = u[22]
        V12L = u[23]
        V12R = u[24]
        V13L = u[25]
        V13R = u[26]
        V14L = u[27]
        V14R = u[28]
        V15L = u[29]
        V15R = u[30]
        V16L = u[31]
        V16R = u[32]
        V17 = u[33]
        V18 = u[34]
        V19 = u[35]



        iR0 = (Vin - V0)/Rs['0'];
        iR1L = (V0 - V1L)/Rs['1L'];
        iR2L = (V1L - V2L)/Rs['2L'];
        iR3L = (V1L - V3L)/Rs['3L'];
        iR4L = (V3L - V4L)/Rs['4L'];
        iR5L = (V3L - V5L)/Rs['5L'];
        iR6L = (V5L - V6L)/Rs['6L'];
        iR7L = (V5L - V7L)/Rs['7L'];
        iR8L = (V2L - V8L)/Rs['8L'];
        iR9L = (V4L - V9L)/Rs['9L'];
        iR10L = (V6L - V10L)/Rs['10L'];
        iR11L = (V7L - V11L)/Rs['11L'];
        iR12L = (V11L - V12L)/Rs['12L'];
        iR13L = (V10L - V13L)/Rs['13L'];
        iR14L = (V12L - V13L)/Rs['14L'];
        iR15L = (V9L - V14L)/Rs['15L'];
        iR16L = (V13L - V14L)/Rs['16L'];
        iR17L = (V12L - V14L)/Rs['17L'];
        iR18L = (V8L - V15L)/Rs['18L'];
        iR19L = (V14L - V15L)/Rs['19L'];
        iR20L = (V15L - V16L)/Rs['20L'];
        iR1R = (V0 - V1R)/Rs['1R'];
        iR2R = (V1R - V2R)/Rs['2R'];
        iR3R = (V1R - V3R)/Rs['3R'];
        iR4R = (V3R - V4R)/Rs['4R'];
        iR5R = (V3R - V5R)/Rs['5R'];
        iR6R = (V5R - V6R)/Rs['6R'];
        iR7R = (V5R - V7R)/Rs['7R'];
        iR8R = (V2R - V8R)/Rs['8R'];
        iR9R = (V4R - V9R)/Rs['9R'];
        iR10R = (V6R - V10R)/Rs['10R'];
        iR11R = (V7R - V11R)/Rs['11R'];
        iR12R = (V11R - V12R)/Rs['12R'];
        iR13R = (V10R - V13R)/Rs['13R'];
        iR14R = (V12R - V13R)/Rs['14R'];
        iR15R = (V9R - V14R)/Rs['15R'];
        iR16R = (V13R - V14R)/Rs['16R'];
        iR17R = (V12R - V14R)/Rs['17R'];
        iR18R = (V8R - V15R)/Rs['18R'];
        iR19R = (V14R - V15R)/Rs['19R'];
        iR20R = (V15R - V16R)/Rs['20R'];
        iR21L = (V16L - V17)/Rs['21L'];
        iR23L = (V16L - V18)/Rs['23L'];
        iR25L = (V16L - V19)/Rs['25L'];
        iR21R = (V16R - V17)/Rs['21R'];
        iR23R = (V16R - V18)/Rs['23R'];
        iR25R = (V16R - V19)/Rs['25R'];
        iR22 = (V17 - Vout1)/Rs['22'];
        iR24 = (V18 - Vout2)/Rs['24'];
        iR26 = (V19 - Vout3)/Rs['26'];
        iC8L = iR2L - iR8L; #1in
        iC8R = iR2R - iR8R; #1in
        iC9L = iR4L - iR9L; #1in
        iC9R = iR4R - iR9R; #1in
        iC10L = iR6L - iR10L; #1in
        iC10R = iR6R - iR10R; #1in
        iC11L = iR7L - iR11L; #1in
        iC11R = iR7R - iR11R; #1in
        iC12L = iR11L - iR12L; #1in
        iC12R = iR11R - iR12R; #1in
        iC13L = iR10L - iR13L; #1in
        iC13R = iR10R - iR13R; #1in
        iC15L = iR9L - iR15L; #1in
        iC15R = iR9R - iR15R; #1in
        iC18L = iR8L - iR18L; #1in
        iC18R = iR8R - iR18R; #1in
        iC22 = iR21L + iR21R - iR22; #2in
        iC24 = iR23L + iR23R - iR24; #2in
        iC26 = iR25L + iR25R - iR26; #2in
        iC16L = iR13L + iR14L - iR16L; #2in
        iC16R = iR13R + iR14R - iR16R; #2in
        iC20L = iR19L + iR18L - iR20L; #2in
        iC20R = iR19R + iR18R - iR20R; #2in
        iC19L = iR15L + iR16L + iR17L - iR19L; #3in
        iC19R = iR15R + iR16R + iR17R - iR19R; #3in
        iC17L = (iR12L - iR16L - iR14L)/(1 + Cs['14L']/Cs['17L']); #2in
        iC17R = (iR12R - iR16R - iR14R)/(1 + Cs['14R']/Cs['17R']); #2in
        iC1R = (iR0  - iR1L - iR1R)/(1 + Cs['1L']/Cs['1R']);
        iC3L = (iR1L - iR2L - iR3L)/(1 + Cs['2L']/Cs['3L']);   
        iC3R = (iR1R - iR2R - iR3R)/(1 + Cs['2R']/Cs['3R']);   
        iC5L = (iR3L - iR4L - iR5L)/(1 + Cs['4L']/Cs['5L']); #2in
        iC5R = (iR3R - iR4R - iR5R)/(1 + Cs['4R']/Cs['5R']); #2in
        iC7L = (iR5L - iR6L - iR7L)/(1 + Cs['6L']/Cs['7L']); #2in
        iC7R = (iR5R - iR6R - iR7R)/(1 + Cs['6R']/Cs['7R']); #2in
        iC25L = (iR20L - iR21L - iR23L - iR25L)/(1 + Cs['23L']/Cs['25L'] + Cs['21L']/Cs['25L']); #3in
        iC25R = (iR20R - iR21R - iR23R - iR25R)/(1 + Cs['23R']/Cs['25R'] + Cs['21R']/Cs['25R']); #3in

        # For the solver, pressure (V) needs to be calculated
        if self.type=='solver': 
            dV2L = iC8L/Cs['8L'];
            dV2R = iC8R/Cs['8R'];
            dV4L = iC9L/Cs['9L'];
            dV4R = iC9R/Cs['9R'];
            dV6L = iC10L/Cs['10L'];
            dV6R = iC10R/Cs['10R'];
            dV7L = iC11L/Cs['11L'];
            dV7R = iC11R/Cs['11R'];
            dV11L = iC12L/Cs['12L'];
            dV11R = iC12R/Cs['12R'];
            dV10L = iC13L/Cs['13L'];
            dV10R = iC13R/Cs['13R'];
            dV9L = iC15L/Cs['15L'];
            dV9R = iC15R/Cs['15R'];
            dV8L = iC18L/Cs['18L'];
            dV8R = iC18R/Cs['18R'];
            dV17 = iC22/Cs['22'];
            dV18 = iC24/Cs['24'];
            dV19 = iC26/Cs['26'];
            dV13R = iC16R/Cs['16R'];
            dV13L = iC16L/Cs['16L'];
            dV15R = iC20R/Cs['20R'];
            dV15L = iC20L/Cs['20L'];
            dV14L = iC19L/Cs['19L'];
            dV14R = iC19R/Cs['19R'];
            dV12L = iC17L/Cs['17L'];
            dV12R = iC17R/Cs['17R'];
            dV0 = iC1R/Cs['1R'];
            dV1L = iC3L/Cs['3L'];
            dV1R = iC3R/Cs['3R'];
            dV3L = iC5L/Cs['5L'];
            dV3R = iC5R/Cs['5R'];
            dV5L = iC7L/Cs['7L'];
            dV5R = iC7R/Cs['7R'];
            dV16L = iC25L/Cs['25L'];
            dV16R = iC25R/Cs['25R'];
            
            u = [dV0,dV1L,dV1R,dV2L,dV2R,dV3L,dV3R,dV4L,dV4R,dV5L,dV5R,dV6L,dV6R,dV7L,dV7R,dV8L,dV8R,dV9L,dV9R,dV10L,dV10R, dV11L,dV11R,dV12L,dV12R,dV13L,dV13R,dV14L,dV14R,dV15L,dV15R,dV16L,dV16R,dV17,dV18,dV19]
            '''
            Should also return a list of names in order, just in case
            '''
            return u
        
        # For postprocessing to flow, one can just return relvant flows
        # without calculating pressures
        
        elif self.type=='ppflow': 
            # List of names of flows through resistors
            iRnames = ["iR"+str(name) for name in self.elem_names] 
            
            # flows = pd.DataFrame(index = self.elem_names)
            
            for name in iRnames:
                flow = locals()[name]
            
            # Empty list to store flows to return
            list_flows = []
            
            # Iterater over the list of names
            for name in iRnames:
                flow = locals()[name] # Access local variables to get the flow --- this is bizzar but works
                list_flows.append(flow)    # Append it to the list
            
            return(np.asarray(list_flows))
    

    
    
         
    