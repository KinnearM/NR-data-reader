## NR-data-reader

A Python toolkit for reading, processing, and analysing data from numerical relativity simulations. This project uses `numpy`, `pandas` and `SciPy` to transform raw, multi-level simulation output into clean, analysis-ready datasets and generates plots of key physical quantities.

## Key Features

-   Automatically scans a directory to discover all available physical variables.
-   All complex file parsing and data processing logic is encapsulated within a clean, reusable `NRDataReader` class which implements pandas data frames to reshape and analyse data.
-   Combines data from multiple Adaptive Mesh Refinement (AMR) levels, ensuring that data from the finest available grid is always used.
-   **Numerical Methods:**
    -   Deals with physical singularities by regularising divergent quantities before performing sensitive operations like interpolation.
    -   Uses numerical integration (`scipy.integrate.quad`) to calculate derived physical quantities like proper distance.
-    Generates plots using Matplotlib with LaTeX support.

## Contents

1.  **`NR_data_reader.py`:** A Python file containing the self-contained `NRDataReader` class. This is the reusable "toolkit" for loading any data that follows the BAM output format.
2.  **`analysis_notebook.ipynb`:** A Jupyter Notebook that imports the `NRDataReader` class and uses it to perform the specific scientific analysis and generate the final plots.

   I intended to include some complementary data to demonstrate the use of the data reader but it was too big for github! Maybe I'll add some zipped data later.

## Requirements

-   Python 3.x
-   `numpy`
-   `pandas`
-   `SciPy`
-   `matplotlib`



