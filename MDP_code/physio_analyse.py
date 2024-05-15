
import ast
from collections import defaultdict

# Initialize dictionaries to store sums for each index
sum_hist_P = defaultdict(float)
sum_hist_A = defaultdict(float)
sum_hist_D = defaultdict(float)
sum_hist_D1 = defaultdict(float)
sum_hist_D2 = defaultdict(float)
sum_hist_DA1 = defaultdict(float)
sum_hist_DA2 = defaultdict(float)

# Initialize the number of sets
num_sets = 60

# Open and read the log file
with open('/Users/27350/Desktop/Research/MDP_data/physio_DH0.05_DE0.3.log', 'r') as file:
    data = file.read()

# Split the log data into sets
sets = data.split('\n\n')  # Assumes each set is separated by two newline characters

# Iterate through the sets and calculate the sums
for set_index, data_set in enumerate(sets):
    if set_index >= num_sets:
        break  # Stop if we have processed the desired number of sets

    # Split the set into individual lines
    lines = data_set.strip().split('\n')

    # Extract data from each line
    for line in lines:
        parts = line.strip().split(' = ')
        if len(parts) == 2:
            variable, values = parts
            values = ast.literal_eval(values)
            for i, value in enumerate(values):
                if variable == 'hist_P':
                    sum_hist_P[i] += value
                elif variable == 'hist_A':
                    sum_hist_A[i] += value
                elif variable == 'hist_D':
                    sum_hist_D[i] += value
                elif variable == 'hist_D1':
                    sum_hist_D1[i] += value
                elif variable == 'hist_D2':
                    sum_hist_D2[i] += value
                elif variable == 'hist_DA1':
                    sum_hist_DA1[i] += value
                elif variable == 'hist_DA2':
                    sum_hist_DA2[i] += value


# Print the sums for each index
for i in range(60):
    print(f'{i} {sum_hist_P[i]/50} {sum_hist_A[i]/50} {sum_hist_D[i]/50} {sum_hist_D1[i]/50} {sum_hist_D2[i]/50} {sum_hist_DA1[i]/50} {sum_hist_DA2[i]/50}')
