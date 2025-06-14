import os
import glob
import numpy as np
import pandas as pd
from collections import defaultdict # We'll use this for a clean way to group files

class NRDataReader:
    """
    A class to find, read, process, and combine Numerical Relativity data 
    from text files with Adaptive Mesh Refinement (AMR).
    """
    
    def __init__(self, data_directory: str):
        if not os.path.isdir(data_directory):
            raise FileNotFoundError(f"Data directory not found at: {data_directory}")
        self.data_dir = data_directory
        
        # These will be populated when .load() is called
        self.variables = [] 
        self.variable_paths = defaultdict(list)
        self.times = []
        self.data = {}

    def _discover_and_group_files(self):
        """
        Scans the data directory, discovering all variables and grouping
        their file paths.
        """
        print(" Scanning directory... ")
        # Find all files matching the general .x* pattern
        all_x_files = glob.glob(os.path.join(self.data_dir, "*.x*"))
        
        for fpath in all_x_files:
            filename = os.path.basename(fpath)
            variable_stem = filename.split('.x')[0]
            self.variable_paths[variable_stem].append(fpath)
        
        for var in self.variable_paths:
            self.variable_paths[var].sort()
            
        self.variables = sorted(self.variable_paths.keys())
        print(f"✅ Discovered variables: {self.variables}")

    def load(self):
        """
        Main method to discover, load, and process all data in the directory.
        """
        # Discover what variables are present in the folder
        self._discover_and_group_files()
        if not self.variables:
            print("Error: No data files found in the specified format 'variable.x*'.")
            return

        # Determine file structure using the first discovered variable as a reference (will this ever be a bad assumption?)
        ref_var = self.variables[0]
        ref_paths = self.variable_paths[ref_var]

        # Calculate block size for each file of the reference variable
        ref_lines_per_block = [self._get_lines_per_block(p) for p in ref_paths]
        
        # Read off time steps
        self.times = self._parse_times_from_file(ref_paths[0], ref_lines_per_block[0])
        
        # Loop through and process each variable
        for var in self.variables:
            file_paths = self.variable_paths[var]
            var_lines_per_block = [self._get_lines_per_block(p) for p in file_paths]
            
            self.data[var] = self._process_variable(var, file_paths, var_lines_per_block)
        
        print("\n✅ Data loading process complete.")

    def _process_variable(self, variable_name: str, file_paths: list, lines_per_block: list) -> pd.DataFrame:
        """The main processing function for a single variable."""
        
        print(f" Processing variable: {variable_name} ")
        
        all_levels_dfs = []
        for i, filepath in enumerate(file_paths):
            block_size = lines_per_block[i]
            rows_per_data_block = block_size - 2
            if rows_per_data_block <= 0: continue
                
            df_level = pd.read_csv(filepath, comment='"', sep=r'\s+', names=['x_coordinate', 'value'])
            
            num_timesteps = len(df_level) // rows_per_data_block
            if num_timesteps == 0: continue
                
            num_rows_to_keep = num_timesteps * rows_per_data_block
            df_complete = df_level.iloc[:num_rows_to_keep].copy()
            
            time_column = np.repeat(self.times[:num_timesteps], rows_per_data_block)
            df_complete['time'] = time_column
            df_complete['level'] = i
            
            all_levels_dfs.append(df_complete)
            print(f"  - Loaded level {i} ({os.path.basename(filepath)}), found {num_timesteps} time steps.")

        if not all_levels_dfs: return pd.DataFrame()
        master_df = pd.concat(all_levels_dfs, ignore_index=True)
        master_df.sort_values(by=['time', 'x_coordinate', 'level'], inplace=True)
        final_df = master_df.drop_duplicates(subset=['time', 'x_coordinate'], keep='last')
        final_df = final_df.rename(columns={'value': variable_name})
        final_df = final_df.set_index(['time', 'x_coordinate'])
        return final_df.drop(columns='level')
    
    def _find_file_paths(self, variable_name: str) -> list[str]:
        """Finds all file paths for a given variable, sorted by level."""
        pattern = os.path.join(self.data_dir, f"{variable_name}.x*")
        return sorted(glob.glob(pattern))
        
    def _get_lines_per_block(self, filepath: str) -> int:
        """Determines the number of lines in a single time-step block for a file."""
        time_header_indices = []
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                if 'Time' in line:
                    time_header_indices.append(i)
                    if len(time_header_indices) == 2:
                        break
        if len(time_header_indices) < 2:
            return 0
        return time_header_indices[1] - time_header_indices[0]
        
    def _parse_times_from_file(self, filepath: str, block_size: int) -> list[float]:
        """Reads a file and  extracts the list of time steps."""
        times = []
        if block_size == 0: return []
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                if i % block_size == 0:
                    try:
                        time_str = line.split('=')[1].strip().strip('"')
                        times.append(float(time_str))
                    except (IndexError, ValueError):
                        continue
        return times
        
    def get_variable(self, variable_name: str) -> pd.DataFrame:
        """
        Returns the fully processed DataFrame for a given variable.
        
        Args:
            variable_name (str): The name of the variable, e.g., 'bssn_gzz'.
        
        Returns:
            pd.DataFrame: A MultiIndex DataFrame of the requested data.
        """
        return self.data.get(variable_name, pd.DataFrame())     
        
    def get_times(self) -> list:
        """Returns the list of time steps."""
        return self.times