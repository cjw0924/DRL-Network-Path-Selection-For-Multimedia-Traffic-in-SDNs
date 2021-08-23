import sys
sys.path.insert(0, '/home/dmg/Desktop/DRLResearch/thesis_env/lib/python3.8/site-packages')   
sys.path.insert(0, '/home/dmg/Desktop/DRLResearch/thesis_env/lib/python3.8/site-packages/ryu/app')   

import numpy as np
from gym import Env, spaces
from time import sleep

import proactive_mininet_api

NUMBER_HOSTS = 8
NUMBER_PATHS = 5
REWARD_SCALE = NUMBER_HOSTS*NUMBER_HOSTS*NUMBER_PATHS


class MininetEnv(Env):
    def __init__(self):
        self.number_of_requests = 0
        self.max_requests = 8
        self.done = False
        
        self.mininet_engine = proactive_mininet_api.MininetAPI(NUMBER_HOSTS, NUMBER_PATHS)
        
        self.observation_space = spaces.Box( \
            low=np.zeros((NUMBER_HOSTS,NUMBER_HOSTS,NUMBER_PATHS,1), dtype=np.float32), \
            high=np.full((NUMBER_HOSTS,NUMBER_HOSTS,NUMBER_PATHS,1), 100, dtype=np.float32), dtype=np.float32)
        
        self.state = np.full((NUMBER_HOSTS,NUMBER_HOSTS,NUMBER_PATHS,1), 100, dtype=np.float32)
                
        self.action_space = spaces.Discrete(NUMBER_PATHS)
    
    def step(self, action):
        self.mininet_engine.start_iperf(action)
        self.number_of_requests += 1
        
        print("ACTION:", action)
        print("REQUEST NUMBER:", self.number_of_requests)
            
        reward = 0
        self.done = False
        info = {}
        
        sleep(3)
                
        # state: read link stats
        self.state = self.mininet_engine.build_state()
    
        # reward: evaluate state
        for src in range(NUMBER_HOSTS):
            for dst in range(NUMBER_HOSTS):
                for path_number in range(NUMBER_PATHS):
                    metric = self.state[src, dst, path_number]
                    if metric != None:
                        metric_percentage = metric
                        if metric_percentage > 75:
                            reward += 20
                        elif metric_percentage > 50: 
                            reward += 10
                        elif metric_percentage > 25: 
                            pass
                        elif metric_percentage > 0: 
                            reward -= 10
                        else:
                            reward -= 20
                            
        print("REWARD:", reward/REWARD_SCALE)
                        
        if self.number_of_requests == self.max_requests:
            sleep(31)
            self.done = True
            
        return self.state, reward/REWARD_SCALE, self.done, info
    
    def render():
        pass
    
    def get_state(self):
        return self.state
    
    def reset(self):  
        self.done = False
        self.state = np.full((NUMBER_HOSTS,NUMBER_HOSTS,NUMBER_PATHS,1), 100, dtype=np.float32)
        self.number_of_requests = 0
        self.mininet_engine.reset_measures()
        
        return self.state
