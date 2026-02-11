# AROM: A Robotic Mind Model for Affective Decision Making and Behaviour Generation
This repository accompanies the paper “A Robotic Mind Model for Affective Decision Making and Behaviour Generation”, published in the International Journal of Social Robotics (2026).

System Structure:
![image](https://github.com/Jellyfishall/AROM/blob/0c9807ee4180419cc351a2ae563953091b272ffc/Figures/System%20Structure.png)

## Overview
AROM (Affective RObotic Mind) is a biomimetic cognitive architecture for affective robots that tightly integrates emotion dynamics, decision making, and behaviour generation.
Unlike many existing affective robotics approaches that treat emotion as a purely expressive layer, AROM embeds continuous emotional states directly into the control logic of the robot, influencing both what the robot decides to do and how it moves.

The model is inspired by vertebrate monoamine systems and combines:

### 1. A four-dimentional continuous emotion model including PAD emotion dimensions (Pleasure, Arousal, Dominance) and Dopamine-driven motivation and satiation
Emotion Model:
![image](https://github.com/Jellyfishall/AROM/blob/0c9807ee4180419cc351a2ae563953091b272ffc/Figures/Emotional%20Model.png)
Emotion Dynamics:
![image](https://github.com/Jellyfishall/AROM/blob/0c9807ee4180419cc351a2ae563953091b272ffc/Figures/Screenshot%20from%202026-02-06%2014-31-13.png)

### 2. MDP-based decision making with emotion-modulated rewards and transition probabilities
Decision Making Module:
![image](https://github.com/Jellyfishall/AROM/blob/0c9807ee4180419cc351a2ae563953091b272ffc/Figures/Decision-Making%20Module.png)
Decision Making MDP:
![image](https://github.com/Jellyfishall/AROM/blob/0c9807ee4180419cc351a2ae563953091b272ffc/Figures/MDP.png)

### 3. A general, robot-agnostic behaviour generation framework for expressive body motion and locomotion
Behaviour Generation Module:
![image](https://github.com/Jellyfishall/AROM/blob/2f73e69dc21a5841555670c55d5ff9c64707a1aa/Figures/Behaviour%20Generation%20structure.png)
![image](https://github.com/Jellyfishall/AROM/blob/0c9807ee4180419cc351a2ae563953091b272ffc/Figures/Screenshot%20from%202026-02-06%2014-31-44.png)

## Key Contributions

* Unified affective control architecture: A single emotion model modulates both decision making and behaviour generation, ensuring consistency and interpretability.

* Biomimetic emotion dynamics: Emotion fluctuations are grounded in physiological principles (dopamine, serotonin, noradrenaline) rather than ad-hoc heuristics.

* Emotion-intervened decision making: Emotions alter incentive salience, action values, and uncertainty handling in an MDP framework.

* Continuous affective behaviour generation: Robot motions (posture, velocity, amplitude, frequency, and trajectory) change smoothly with emotional state.

* Human-centred interpretability: User studies show that affective modulation improves perceived emotional clarity and intention understanding.

## Intended Use

This work is intended for:

* Affective and social robotics research

* Human–robot interaction (HRI)

* Cognitive and biomimetic robot control architectures

* Emotion-aware decision-making systems

## Reference

If you use this work, please cite:
Zhang, J., Herrmann, J.M. A Robotic Mind Model for Affective Decision Making and Behaviour Generation. Int J of Soc Robotics 18, 23 (2026). https://doi.org/10.1007/s12369-025-01345-z


https://github.com/user-attachments/assets/044840b4-36a2-49ef-966a-c9ddc2869baa





