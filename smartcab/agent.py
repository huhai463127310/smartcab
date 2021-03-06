import random
import math
import numpy as np
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import time

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5,
                 epsilon_decay_func="const_power", epsilon_decay_const=0.99):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        print("init epsilon={}".format(epsilon))

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        self.t = 1
        if epsilon_decay_func not in ["const_power", "exp_power", "t_square_reciprocal", "cos"]:
            raise ValueError("invalid epsilon_decay_func: ".format(epsilon_decay_func))
        self.epsilon_decay_func = epsilon_decay_func
        self.epsilon_decay_const = epsilon_decay_const
        self.random_action = 0
        self.total_action = 0
        self.start_time = time.time()

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0

        if testing:
            self.epsilon = 0
            self.alpha = 0
        else:
            if self.epsilon_decay_func == "const_power":
                self.epsilon = pow(self.epsilon_decay_const, self.t)
            elif self.epsilon_decay_func == "exp_power":
                self.epsilon = np.exp(-self.epsilon_decay_const * self.t)
            elif self.epsilon_decay_func == "t_square_reciprocal":
                self.epsilon = 1.0/(self.t ** 2)
            elif self.epsilon_decay_func == "cos":
                self.epsilon = math.cos(self.epsilon_decay_const * self.t)

            time_elapse = time.time() - self.start_time
            print("epsilon_decay_func={} t={} epsilon={:.8f} total_action={} random_action={} "
                  "random_ration={:.4f} time_elapse={} min {} s".format(
                    self.epsilon_decay_func,
                    self.t, self.epsilon,
                    self.total_action,
                    self.random_action,
                    0 if self.total_action == 0 else self.random_action * 1.0 / self.total_action,
                    time_elapse // 60, int(time_elapse % 60)))
            self.t += 1
            # import sys
            # sys.exit()
        self.random_action = 0
        self.total_action = 0
        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        # Set 'state' as a tuple of relevant data for the agent        
        state = (waypoint, inputs["light"], inputs["left"], inputs["right"], inputs["oncoming"])

        return state

    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state

        items = sorted(self.Q[state].items(), key=lambda _: _[1], reverse=True)
        end_index = 0

        for i in range(1, len(items)):
            if items[i][1] == items[0][1]:
                end_index = i
            else:
                break

        max_index = random.randint(0, end_index)
        maxQ = items[max_index]
        # maxQ = max(self.Q[state].values())

        # print("state action count: {} {} {}".format(state, len(items), maxQ))
        return maxQ

    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0

        if state not in self.Q:
            self.Q.setdefault(state, {action: 0.0 for action in self.valid_actions})
        return


    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        # When learning, choose a random action with 'epsilon' probability
        #   Otherwise, choose an action with the highest Q-value for the current state
        self.total_action += 1
        if self.learning:
            if random.random() < self.epsilon:
                self.random_action += 1
                action = random.choice(self.valid_actions)
            else:
                action = self.get_maxQ(state)[0]
        else:
            action = random.choice(self.valid_actions)
        return action

    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        if self.learning:
            # gamma = 0
            # new_state = self.build_state()
            # self.createQ(new_state)
            self.Q[state][action] = (1 - self.alpha) * self.Q[state][action]
            # + self.alpha * (reward + gamma * self.get_maxQ(new_state)[1])
        return

    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return
        

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment(verbose=False, num_dummies=100, grid_size=(8, 6))
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    # ############  add by me  ############
    #    * epsilon_decay_func - epsilon decay function, default is const_power
    #    * epsilon_decay_const - constant number a in epsilon decay function, default is 0.99
    agent = env.create_agent(LearningAgent, learning=True, alpha=0.5, epsilon=1,
                             epsilon_decay_func="cos", epsilon_decay_const=0.0015)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, update_delay=0.01, display=False, log_metrics=True, optimized=True)
    
    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(tolerance=0.1, n_test=10)


if __name__ == '__main__':
    start_time = time.time()
    run()
    total_time = math.floor(time.time() - start_time)
    print("total_time is {} min {} s".format(total_time//60, total_time % 60))

