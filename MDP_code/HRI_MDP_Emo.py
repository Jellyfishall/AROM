# With Emotion Version
import numpy as np
import random
import time
import logging

logging.basicConfig(filename='/Users/27350/Desktop/Research/MDP_data/physio_DH0.3_DE0.05.log', level=logging.DEBUG, format='%(message)s')
# Define the MDP
num_states = 3
num_actions = 3
gamma = 0.9  # Discount factor
P_thomp1 = 0.0   # Probability of original thompson sampling
P_thomp2 = 0.0
P_po1 = 0.5   # probability for action 1 to gain positive reinforcer
P_ne1 = 0.5   # ...negative...
P_po2 = 0.5 #0.3
P_ne2 = 0.5 #0.7  # initial values but also stable values if taking many tries
# Standard weights
W_spo1 = 4.0
W_sne1 = -2.0
W_spo2 = 4.0
W_sne2 = -2.0
W_sidle = 1
# Variable weights
W_po1 = 4.0
W_ne1 = -2.0
W_po2 = 4.0
W_ne2 = -2.0
W_idle = 1
i = 1
n = 60   # run n episodes
m = 6   # memory of actions, used in calculation of D
last_state = 0 # start from state 0
#T = 0.05

# Emotion parameters
P = 0.0
#P_2 = 0.0
A = 0.0   # [-1, 1]
D = 0.0
D_1 = 0.0   # Dominance related to playing with human (action 1)
D_2 = 0.0   # Dominance related to exploring alone (action 2)
#DA_0 = 0.0  # "wanting" of taking a rest (action 0)
DA_1 = 0.0  # "wanting" of playing with human (action 1)
DA_2 = 0.0  # "wanting" of exploring alone (action 2)
k = 0.5  # The threshold that Arousal influences understanding of probability distribution


# Transition probabilities: transition_probs[state][action][next_state]个 行 列
# state 0: idle, 1: positive, 2: negative
# action 0: idle, 1: go for human, 2: explore alone
transition_probs = np.array([
#state 0,   1,   2
    [[1.0, 0.0, 0.0],  # From state 0, action 0
     [0.0, P_po1, P_ne1],  # From state 0, action 1
     [0.0, P_po2, P_ne2]],  # From state 0, action 2

    [[1.0, 0.0, 0.0],  # From state 1, action 0
     [0.0, P_po1, P_ne1],  # From state 1, action 1
     [0.0, P_po2, P_ne2]],  # From state 1, action 2

    [[1.0, 0.0, 0.0],  # From state 2, action 0
     [0.0, P_po1, P_ne1],  # From state 2, action 1
     [0.0, P_po2, P_ne2]]   # From state 2, action 2
])


# Rewards: rewards[state][action][next_state]
rewards = np.array([                            # equal rewards
    [[W_idle, 0, 0],  # From state 0, action 0
     [0, W_po1, W_ne1],  # From state 0, action 1
     [0, W_po2, W_ne2]],  # From state 0, action 2

    [[W_idle, 0, 0],  # From state 1, action 0
     [0, W_po1, W_ne1],  # From state 1, action 1
     [0, W_po2, W_ne2]],  # From state 1, action 2

    [[W_idle, 0, 0],  # From state 2, action 0
     [0, W_po1, W_ne1],  # From state 2, action 1
     [0, W_po2, W_ne2]]    # From state 2, action 2
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
    hist_reward = []
    hist_reward_1 = []
    hist_reward_2 = []
    sum_reward = []  # total rewards of all actions
    sum_reward_1 = [] # total rewards that received when taking action 1
    sum_reward_2 = [] # total rewards that received when taking action 2
    
    hist_P = []
    hist_A = []
    hist_D = []
    hist_D1 = []
    hist_D2 = []
    hist_DA1 = []
    hist_DA2 = []
    
    n_positive = [0,0] #[total positive of action 1, of action 2]
    n_selection = [0,0] #[total selection of action 1, of action 2]
    Satiety_1 = []  # If action = 1, resulting state = 1, then append 2; state = 2, append -2; not asking and not get anything, append -1
    Satiety_2 = []  # If action = 2, ......
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
    hist_reward.append(0) # Initialization of rewards, used for the first time of reward comparison
    hist_reward_1.append(0)
    hist_reward_2.append(0)
    sum_reward.append(0)
    sum_reward_1.append(0)
    sum_reward_2.append(0)
    Satiety_1.append(0)
    Satiety_2.append(0)
    
    hist_P.append(P)
    hist_A.append(A)
    hist_D.append(D)
    hist_D1.append(D_1)
    hist_D2.append(D_2)
    hist_DA1.append(DA_1)
    hist_DA2.append(DA_2)
    
    # then run n episodes
    for i in range(1,n):
        if last_action == 0:
            last_state = 0
            Satiety_1.append(-1)
            Satiety_2.append(-1)
        if last_action == 1:
            last_state = human_react(i) # result state after interaction
            if last_state == 1:
                Satiety_1.append(2)
            if last_state == 2:
                Satiety_1.append(0)
            Satiety_2.append(-1)  
            
            hist_reward_1.append(rewards[hist_state[i-1]][hist_action[i-1]][last_state])    
            sum_reward_1.append(sum(hist_reward_1))      
            hist_a1.append(last_state)
            n_selection[0] = len(hist_a1)                        
            n_positive[0] = len(hist_a1)-(np.sum(hist_a1)-len(hist_a1))
                
        if last_action == 2:
            last_state = envio_react(i)
            if last_state == 1:
                Satiety_2.append(2)
            if last_state == 2:
                Satiety_2.append(0)
            Satiety_1.append(-1)    
            
            hist_reward_2.append(rewards[hist_state[i-1]][hist_action[i-1]][last_state])    
            sum_reward_2.append(sum(hist_reward_2))           
            hist_a2.append(last_state)
            n_selection[1] = len(hist_a2)
            n_positive[1] = len(hist_a2)-(np.sum(hist_a2)-len(hist_a2))
            
        hist_reward.append(rewards[hist_state[i-1]][hist_action[i-1]][last_state])  
        sum_reward.append(sum(hist_reward))     
        #print("N_positive:", n_positive)    
        #print("N_selection", n_selection)
        #print("hist_reward:", hist_reward)
        #print("sum_reward:", sum_reward)
        #print("Satiety_1:", Satiety_1)
        #print("Satiety_2:", Satiety_2)
        # Calculation of emotions
        
        P = np.minimum(1, np.maximum(-1, P * 0.7 + 0.05 * (sum_reward[i]-sum_reward[i-1]) ))
        A = np.minimum(1, np.maximum(-1, A * 0.7 + 0.05 * abs(sum_reward[i]-sum_reward[i-1]) ))
        #A = np.minimum(1, np.maximum(-1, A * 0.7 + 0.00 * abs(sum_reward[i]-sum_reward[i-1]) ))
        
        D = np.minimum(1, np.maximum(-1, D * 0.7 + 0.15 * ((sum_reward[i]-sum_reward[i-1])-(sum_reward[i]-sum_reward[int(np.maximum(0, i-m))])/np.minimum(i,m)) ))
        D_1 = np.minimum(1, np.maximum(-1, D_1 * 0.7 + 0.3 * (hist_reward_1[n_selection[0]]-(sum_reward_1[n_selection[0]]-sum_reward_1[int(np.maximum(0, n_selection[0]-m))])/np.minimum(np.maximum(1, n_selection[0]),m)) ))
        D_2 = np.minimum(1, np.maximum(-1, D_2 * 0.7 + 0.05 * (hist_reward_2[n_selection[1]]-(sum_reward_2[n_selection[1]]-sum_reward_2[int(np.maximum(0, n_selection[1]-m))])/np.minimum(np.maximum(1, n_selection[1]),m)) ))        
        #no D
        #D = np.minimum(1, np.maximum(-1, D * 0.7 + 0.0 * ((sum_reward[i]-sum_reward[i-1])-(sum_reward[i]-sum_reward[int(np.maximum(0, i-m))])/np.minimum(i,m)) ))
        #D_1 = np.minimum(1, np.maximum(-1, D_1 * 0.7 + 0.0 * (hist_reward_1[n_selection[0]]-(sum_reward_1[n_selection[0]]-sum_reward_1[int(np.maximum(0, n_selection[0]-m))])/np.minimum(np.maximum(1, n_selection[0]),m)) ))
        #D_2 = np.minimum(1, np.maximum(-1, D_2 * 0.7 + 0.0 * (hist_reward_2[n_selection[1]]-(sum_reward_2[n_selection[1]]-sum_reward_2[int(np.maximum(0, n_selection[1]-m))])/np.minimum(np.maximum(1, n_selection[1]),m)) ))
        
        DA_1 = np.minimum(1, np.maximum(-1, DA_1 * 0.8 - 0.2 * Satiety_1[i]))
        DA_2 = np.minimum(1, np.maximum(-1, DA_2 * 0.8 - 0.2 * Satiety_2[i]))
        #DA_1 = np.minimum(1, np.maximum(-1, DA_1 * 0.8 - 0.0 * Satiety_1[i]))  # no DA
        #DA_2 = np.minimum(1, np.maximum(-1, DA_2 * 0.8 - 0.0 * Satiety_2[i]))
        
        hist_P.append(P)
        hist_A.append(A)
        hist_D.append(D)
        hist_D1.append(D_1)
        hist_D2.append(D_2)
        hist_DA1.append(DA_1)
        hist_DA2.append(DA_2)
        
        #print("For ith episode, P, A, D, D_1, D_2, DA_1, DA_2:", i, P, A, D, D_1, D_2, DA_1, DA_2)
        # probability of po and ne results occur, calculate like thin because the array is composed by 1 and 2
        if A > k:
            P_thomp1 = thompson_sampling(n_positive[0] - 1 + 1/(A+1), n_selection[0])
            P_po1 = P_thomp1 - A * (P_thomp1 - 0.5)  # Only valid when 0 <= A <= 1
        else:
            P_thomp1 = thompson_sampling(n_positive[0], n_selection[0])
            P_po1 = P_thomp1
        P_ne1 = 1-P_po1
        # probability of po and ne results occur, calculate like thin because the array is composed by 1 and 2
        
        if A > k:
            P_thomp2 = thompson_sampling(n_positive[1] - 1 + 1/(A+1), n_selection[1])
            P_po2 = P_thomp2 - A * (P_thomp2 - 0.5)
        else:
            P_thomp2 = thompson_sampling(n_positive[1], n_selection[1])
            P_po2 = P_thomp2
        P_ne2 = 1-P_po2
        
        #ne2 = np.mean(hist_a2)-1 
        hist_state.append(last_state)
        transition_probs = np.array([  # here again because if not the array won't change
        #state 0,   1,   2
            [[1.0, 0.0, 0.0],  # From state 0, action 0
            [0.0, P_po1, P_ne1],  # From state 0, action 1
            [0.0, P_po2, P_ne2]],  # From state 0, action 2

            [[1.0, 0.0, 0.0],  # From state 1, action 0
            [0.0, P_po1, P_ne1],  # From state 1, action 1
            [0.0, P_po2, P_ne2]],  # From state 1, action 2

            [[1.0, 0.0, 0.0],  # From state 2, action 0
            [0.0, P_po1, P_ne1],  # From state 2, action 1
            [0.0, P_po2, P_ne2]]   # From state 2, action 2
            ])
        
        if D < 0:
            W_idle = np.minimum(4, np.maximum(-2, W_sidle / (np.exp(0.5 * D) )))  # here we don't consider influences of robot's energy and tiredness
            W_po1 = np.minimum(8, np.maximum(-4, W_spo1 * np.exp( DA_1) * np.exp(0.5 * D_1) ))
            W_ne1 = np.minimum(8, np.maximum(-4, W_sne1 * np.exp( DA_1) * np.exp(0.5 * D_1) ))
            W_po2 = np.minimum(8, np.maximum(-4, W_spo2 * np.exp( DA_2) * np.exp(0.5 * D_2) ))
            W_ne2 = np.minimum(8, np.maximum(-4,  W_sne2 * np.exp( DA_2) * np.exp(0.5 * D_2) ))
        else:
            W_idle = W_sidle
            W_po1 = np.minimum(8, np.maximum(-4, W_spo1 * np.exp( DA_1) ))
            W_ne1 = np.minimum(8, np.maximum(-4, W_sne1 * np.exp( DA_1) ))
            W_po2 = np.minimum(8, np.maximum(-4, W_spo2 * np.exp( DA_2) ))
            W_ne2 = np.minimum(8, np.maximum(-4,  W_sne2 * np.exp( DA_2) ))
        
        
        rewards = np.array([                            # equal rewards
            [[W_idle, 0, 0],  # From state 0, action 0
            [0, W_po1, W_ne1],  # From state 0, action 1
            [0, W_po2, W_ne2]],  # From state 0, action 2

            [[W_idle, 0, 0],  # From state 1, action 0
            [0, W_po1, W_ne1],  # From state 1, action 1
            [0, W_po2, W_ne2]],  # From state 1, action 2

            [[W_idle, 0, 0],  # From state 2, action 0
            [0, W_po1, W_ne1],  # From state 2, action 1
            [0, W_po2, W_ne2]]    # From state 2, action 2
            ])
        # Run value iteration and extract the optimal policy
        optimal_values = value_iteration()
        optimal_policy = extract_policy(optimal_values)

        #print("Optimal Values:", optimal_values)
        #print("Optimal Policy:", i, optimal_policy)
        
        #print("transition_probs:", transition_probs)
        #print("rewards:", rewards)
        # Calculate optimal actions for the last state
        last_action = extract_policy(optimal_values, last_state)
        hist_action.append(last_action)
        # Print the action taken for the last turn
        #print("Last state:", i, last_state)
        #print("Last action:", i, last_action)
        i+1
    #print("State history", hist_state)
    #print("Action history", hist_action)
    
    #logging.debug(f'hist_action: {hist_action}')
    
    logging.debug(f'hist_P = {hist_P}')
    logging.debug(f'hist_A = {hist_A}')
    logging.debug(f'hist_D = {hist_D}')
    logging.debug(f'hist_D1 = {hist_D1}')
    logging.debug(f'hist_D2 = {hist_D2}')
    logging.debug(f'hist_DA1 = {hist_DA1}')
    logging.debug(f'hist_DA2 = {hist_DA2}')
    
