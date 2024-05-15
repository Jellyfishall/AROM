import logging
import ast
from collections import defaultdict

# Configure the logging module with the provided format
logging.basicConfig(filename='/Users/27350/Desktop/Research/MDP_data/emo_DH0.05_DE0.3.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')

# Initialize a dictionary to store counts for each number under each index
count_by_index = defaultdict(lambda: defaultdict(int))

# Open and read the log file
with open('/Users/27350/Desktop/Research/MDP_data/emo_DH0.05_DE0.3.log', 'r') as file:
    for line in file:
        # Split the log message into parts
        parts = line.strip().split(': ')

        if len(parts) == 2:
            _, hist_action_str = parts
            hist_action = ast.literal_eval(hist_action_str)
            
            # Iterate over the elements in hist_action
            for i, num in enumerate(hist_action):
                # Update the counts for each number under each index
                count_by_index[i][num] += 1

# Calculate the sum for each number under each index
sum_by_index = defaultdict(lambda: defaultdict(int))
for i in range(61):
    for num in range(3):
        sum_by_index[i][num] = count_by_index[i][num]

# Print the results
for i in range(61):
    #print(f'Index {i}: Sum of 0s = {sum_by_index[i][0]}, Sum of 1s = {sum_by_index[i][1]}, Sum of 2s = {sum_by_index[i][2]}')
    print(f'{i} {sum_by_index[i][0]/50} {sum_by_index[i][1]/50} {sum_by_index[i][2]/50}')
    

