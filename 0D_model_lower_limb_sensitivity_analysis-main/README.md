# 0D_model_sensitivity_analysis
This is a code used to conduct sensitivity analysis of the generic 0D model in the venous modelling project. 


> input_data
- contains all necessary input files to the model
- type of SA is defined in setup.json file
  - "type" can be changed from "local" to "global"
  - "n" should stay 1 for local analysis; it is the sampling depth for Sobol analysis (for steady state n=10, for transient n=15 for convergence of Sobol indices)
  - "bound" is the variation in input parameters, by default set to 0.1 (+/- 10%)
  - "N_containers": 1 -- number of files to split the sensitivity analysis into -- keep at 1 for local, for global it is worth changing if the solver is run in parallel (cloud, HPC)


> Sampling
- to generate sensitivity analysis input samples, run "run_samples_for_SA.py"
  - specify relative paths inside the file
    - path_to_input_data: path to the input_data directory
    - path_to_save_code_outputs: path to desired directory (to be created) for saving generated samples

- the code will generate a "problem.json" file for sensitivity analysis
- the code will create "input_samples" directory within "Sampling" containing files necessary for SA; 

> Solver
- to solve the model for the generated samples
- run_execute_model.py - to run transient model - requires providing appropriate paths to data inside the script
- merge_outputs.py - merges outputs from different patches (if samples were saved as such)

> Sensitivity_analysis
- run_local_analysis.py - run local SA if such samples were generated
- run_sobol_analysis.p - run global Sobol SA if such samples were generated - requires providing the path to the merged outputs from Solver

- run_orthogonal_analysis.py - run orthogonal sensitivity on the previosuly computed SA indices
