import numpy as np
import pandas as pd
from scipy.stats import pearsonr

# Load your data from a CSV file
data = pd.read_csv('Beha_exp_data.csv')

# Separate the data into your data and reference data
your_data = data.iloc[0:21, :]  # Assuming your data columns start from the 2nd column
reference_data = data.iloc[21:, :]  # Assuming reference data columns start from the 23rd column

# Initialize arrays to store the correlation coefficients
correlations_P = []
correlations_A = []
correlations_D = []

# Calculate correlations for each dimension
for i in range(3):
    your_dimension = your_data.iloc[:, i::3].values
    reference_dimension = reference_data.iloc[:, i::3].values

    # Calculate Pearson correlation for this dimension
    correlation_coefficients = [pearsonr(your_dimension[:, j], reference_dimension[:, j])[0] for j in range(15)]

    if i == 0:
        correlations_P = correlation_coefficients
    elif i == 1:
        correlations_A = correlation_coefficients
    else:
        correlations_D = correlation_coefficients

# Print the correlation coefficients for each dimension
print("Correlation for P dimension:", correlations_P)
print("Correlation for A dimension:", correlations_A)
print("Correlation for D dimension:", correlations_D)
