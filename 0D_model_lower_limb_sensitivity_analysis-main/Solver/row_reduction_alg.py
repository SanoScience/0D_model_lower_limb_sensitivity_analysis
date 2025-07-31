import numpy as np 
import pandas as pd
import time

class RowReduction():
    def __init__(self, matrix, df_model, dP):
        self.matrix = matrix
        self.df_model = df_model       
        self.dP = dP
 
    #====================
    def replace_in_matrix(self, matrix, df_model):       
        d = dict(df_model.values)
        for key in d.keys(): 
            matrix = matrix.replace(f"R{key}", d[key])
        matrix = matrix.replace('V', self.dP) 
        
        for row in matrix.itertuples():
            for elem in row:
                if isinstance(elem, str) == True and '+' in elem:
                    foo = elem.replace('+', ' ').split()                    
                    value=sum([d[item[1:]] for item in foo])
                    matrix = matrix.replace(elem, value)
        
        return(matrix)
    
    
    #====================
    # Row-reduction function for matrix A
    def manual_rref(self, A, tol):
        m, n = A.shape
        i, j = 0, 0
        jb = []

        while i < m and j < n:
            # Find value and index of largest element in the remainder of column j
            k = np.argmax(np.abs(A[i:m, j])) + i
            p = np.abs(A[k, j])
            # p is the specified 'precision'
            if p <= tol:
                # The column is negligible, zero it out
                A[i:m, j] = 0.0
                j += 1
            else:
                # Remember the column index
                jb.append(j)
                if i != k:
                    # Swap the i-th and k-th rows
                    A[[i, k], j:n] = A[[k, i], j:n]
                # Divide the pivot row i by the pivot element A[i, j]
                A[i, j:n] = A[i, j:n] / A[i, j]
                # Subtract multiples of the pivot row from all the other rows
                for k in range(m):
                    if k != i:
                        A[k, j:n] -= A[k, j] * A[i, j:n]
                i += 1
                j += 1
        # Return reduced matrix  
        return A, jb
    
    
    #====================
    def solve_system(self, matrix, tol=1.0e-10):
        M_rref, jb = self.manual_rref(matrix, tol)
        
        # Get rid of rows which contain zeros only
        M_rref = M_rref[~np.all(M_rref == 0, axis = 1)]
        
        A = np.delete(M_rref, -1, axis = 1)
        b = M_rref[:, -1]
        
        if A.shape[0] == A.shape[1] and np.linalg.det(A) != 0:
            return(np.linalg.solve(A, b))
        
        else:
            print("Ooops, something went wrong...")
            print('Matrix with shape: {}'.format(np.shape(A)))
            return int(0)
        
    #====================
    def run(self):
        new_matrix = self.replace_in_matrix(self.matrix, self.df_model)
        flow_names = [name[1:] for name in list(new_matrix.columns)[0:-1]] 
        
        M = new_matrix.to_numpy()
        flow_vals = self.solve_system(M)
        
        if isinstance(flow_vals, int)==True:
            print('Error encountered. Model could not be solved.\n')
            print('Sys of eqns is wrong OR occlusion in a vessel is too big\n')
            return(pd.DataFrame([0,0]))
        
        else:
            df_solutions = pd.DataFrame({'elem_name': flow_names, 'Q': flow_vals})
            df_solutions['R'] = list(self.df_model['R'])
                        
            df_solutions['P_drop'] = df_solutions['Q'] * df_solutions['R']
            return( df_solutions )