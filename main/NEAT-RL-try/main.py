import neat
import gym
import numpy as np
import visualize

Game = 'CartPole-v1'
env = gym.make(Game).unwrapped

CONFIG = './config'
