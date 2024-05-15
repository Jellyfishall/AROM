# Without Emotion Version
import numpy as np
import random
import time
import logging

logging.basicConfig(filename='/Users/27350/Desktop/Research/my_log.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')
# Define the MDP
num_states = 3
num_actions = 3
gamma = 0.9  # Discount factor
po1 = 0.5   # probability for action 1 to gain positive reinforcer
ne1 = 0.5   # ...negative...
po2 = 0.5 #0.3
ne2 = 0.5 #0.7  # initial values but also stable values if taking many tries
i = 1
n = 60   # run n episodes
last_state = 0 # start from state 0
#T = 0.05

# Transition probabilities: transition_probs[state][action][next_state]个 行 列
# state 0: idle, 1: positive, 2: negative
# action 0: idle, 1: go for human, 2: explore alone
transition_probs = np.array([
#state 0,   1,   2
    [[1.0, 0.0, 0.0],  # From state 0, action 0
     [0.0, po1, ne1],  # From state 0, action 1
     [0.0, po2, ne2]],  # From state 0, action 2

    [[1.0, 0.0, 0.0],  # From state 1, action 0
     [0.0, po1, ne1],  # From state 1, action 1
     [0.0, po2, ne2]],  # From state 1, action 2

    [[1.0, 0.0, 0.0],  # From state 2, action 0
     [0.0, po1, ne1],  # From state 2, action 1
     [0.0, po2, ne2]]   # From state 2, action 2
])

# Rewards: rewards[state][action][next_state]
'''
rewards = np.array([
    [[0, 0, 0],  # From state 0, action 0
     [0, 5, -2],  # From state 0, action 1
     [0, 6, -2]],  # From state 0, action 2

    [[0, 0, 0],  # From state 1, action 0
     [0, 5, -2],  # From state 1, action 1
     [0, 6, -2]],  # From state 1, action 2

    [[0, 0, 0],  # From state 2, action 0
     [0, 4, -3],  # From state 2, action 1
     [0, 5, -3]]    # From state 2, action 2
])
'''
# Rewards: rewards[state][action][next_state]
rewards = np.array([                            # equal rewards
    [[1, 0, 0],  # From state 0, action 0
     [0, 4, -2],  # From state 0, action 1
     [0, 4, -2]],  # From state 0, action 2

    [[1, 0, 0],  # From state 1, action 0
     [0, 4, -2],  # From state 1, action 1
     [0, 4, -2]],  # From state 1, action 2

    [[1, 0, 0],  # From state 2, action 0
     [0, 4, -2],  # From state 2, action 1
     [0, 4, -2]]    # From state 2, action 2
])

# Value iteration algorithm  return the largest Q_values each current state can reach
def value_iteration():
    values = np.zeros(num_states)
    while True:
        prev_values = np.copy(values)
        for state in range(num_states):
            Q_values = []
            for action in range(num_actions):
                Q_value = sum(
                    transition_probs[state][action][next_state] * (rewards[state][action][next_state] + gamma * prev_values[next_state])
                    for next_state in range(num_states)
                )
                Q_values.append(Q_value)
            values[state] = max(Q_values)
        if np.max(np.abs(values - prev_values)) < 1e-6:
            break
    return values


# Optimal policy extraction   return to the index of the largest Q_value, which is the action being taken when achieving the largest value
def extract_policy(values, last_state=None):
    policy = np.zeros(num_states, dtype=int)
    for state in range(num_states):
        Q_values = []
        for action in range(num_actions):
            Q_value = sum(
                transition_probs[state][action][next_state] * (rewards[state][action][next_state] + gamma * values[next_state])
                for next_state in range(num_states)
            )
            Q_values.append(Q_value)
        policy[state] = np.argmax(Q_values)
    if last_state is not None:
        return policy[last_state]
    return policy


def human_react(times):  # times: at which time to trigger specific human reactions
    #probabilities = [0.5, 0.5]  # Probability of positive result and negative result, respectively
    #result = random.choices([1, 2], probabilities)[0]
    
    # Situation 1: human would like to play at first but don't want to play later
    if times <= 15:
        result = 1
    else:
        result = 2
    
    # Situation 2: human don't want to play at first but want to play later
    #if times <= 15:
    #    result = 2
    #else:
    #    result = 1
    
    #print("human_react:", result)
    return result

def envio_react(times):  # times: at which time to trigger specific environment reactions     
    #probabilities = [0.7, 0.3]  # Probability of positive result and negative result, respectively
    probabilities = [0.6, 0.4]
    result = random.choices([1, 2], probabilities)[0]
    
    #print("envio_react:", result)
    return result

def thompson_sampling(n_positive, n_selection): # 2 arms here for action 1 and 2, reward can be 1 (po) or 0 (ne)

    # Sample rewards for each arm using beta distribution
    theta_samples = np.random.beta(n_positive + 1, n_selection - n_positive + 1)
    #print("thompson_sampling", theta_samples)
    return theta_samples


if __name__ == '__main__':
    # initial episode
    # Run value iteration and extract the optimal policy
    #time.sleep(T)
    
    hist_a1 = [] # history of states after taking action a1
    hist_a2 = []
    hist_state = []
    hist_action = []
    n_positive = [0,0] #[total positive of action 1, of action 2]
    n_selection = [0,0] #[total selection of action 1, of action 2]
    optimal_values = value_iteration()
    optimal_policy = extract_policy(optimal_values)
    #print("Optimal Values:", optimal_values)
    #print("Optimal Policy: 0 ", optimal_policy)
    # Calculate optimal actions for the last state
    last_action = extract_policy(optimal_values, last_state)
    #print("Last state: 0 ", last_state)
    #print("Last action: 0 ", last_action)
    hist_state.append(last_state)
    hist_action.append(last_action)
    
    # then run n episodes
    for i in range(1,n):
        if last_action == 0:
            last_state = 0
        if last_action == 1:
            last_state = human_react(i) # result state after interaction
            hist_a1.append(last_state)
            n_selection[0] = len(hist_a1)
            n_positive[0] = len(hist_a1)-(np.sum(hist_a1)-len(hist_a1))
        if last_action == 2:
            last_state = envio_react(i)
            hist_a2.append(last_state)
            n_selection[1] = len(hist_a2)
            n_positive[1] = len(hist_a2)-(np.sum(hist_a2)-len(hist_a2))
        #print("N_positive:", n_positive)    
        #print("N_selection", n_selection)
        
        # probability of po and ne results occur, calculate like thin because the array is composed by 1 and 2
        po1 = thompson_sampling(n_positive[0], n_selection[0])
        ne1 = 1-po1
        # probability of po and ne results occur, calculate like thin because the array is composed by 1 and 2
        po2 = thompson_sampling(n_positive[1], n_selection[1])
        ne2 = 1-po2
        #ne2 = np.mean(hist_a2)-1 
        hist_state.append(last_state)
        transition_probs = np.array([  # here again because if not the array won't change
        #state 0,   1,   2
            [[1.0, 0.0, 0.0],  # From state 0, action 0
            [0.0, po1, ne1],  # From state 0, action 1
            [0.0, po2, ne2]],  # From state 0, action 2

            [[1.0, 0.0, 0.0],  # From state 1, action 0
            [0.0, po1, ne1],  # From state 1, action 1
            [0.0, po2, ne2]],  # From state 1, action 2

            [[1.0, 0.0, 0.0],  # From state 2, action 0
            [0.0, po1, ne1],  # From state 2, action 1
            [0.0, po2, ne2]]   # From state 2, action 2
            ])
        # Run value iteration and extract the optimal policy
        optimal_values = value_iteration()
        optimal_policy = extract_policy(optimal_values)

        #print("Optimal Values:", optimal_values)
        #print("Optimal Policy:", i, optimal_policy)
        #print("transition_probs", transition_probs)
        
        # Calculate optimal actions for the last state
        last_action = extract_policy(optimal_values, last_state)
        hist_action.append(last_action)
        # Print the action taken for the last turn
        #print("Last state:", i, last_state)
        #print("Last action:", i, last_action)
        i+1
    print("State history", hist_state)
    print("Action history", hist_action)
    logging.debug(f'{hist_action}')
