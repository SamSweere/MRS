import numpy as np

def exponential_decay(x, start=100, end_factor=0.0, factor=1):
    """
        exponential decay function
    """
    x = np.array(x)
    return start + (start * end_factor - start) * (1 - np.exp(-x/factor))

def get_action(robot, ann, feedback):
    # inp = exponential_decay([dist for hit, dist in robot.sensor_data])
    # return ann.predict(inp.reshape(-1, 1), feedback, norm=100).reshape(-1)
    inp = np.array([dist for hit, dist in robot.sensor_data])
    return ann.predict(inp.reshape(-1, 1), feedback, norm=100).reshape(-1)

def apply_action(robot, ann, feedback):
    action = get_action(robot, ann, feedback)
    
    # without sigmoids
    # robot.set_vr(action[1])
    # robot.set_vl(action[2])

    # The network outputs values between 0 and 1 for each motor
    # We treat those outputs as normalized velocities
    robot.vl = (action[1]-0.5) * 2 * robot.max_v
    robot.vr = (action[2]-0.5) * 2 * robot.max_v

class ANNController:
    def __init__(self, robot, ann, feedback=True):
        self.robot = robot
        self.ann = ann
        self.feedback = feedback
        # self.step_size = step_size_ms / 1000
        self.passed_time = 0.0
        
    def update(self, delta_time):
        # self.passed_time += delta_time
        # if self.passed_time > self.step_size:
        apply_action(self.robot, self.ann, self.feedback)
        # self.passed_time = 0
                    
    def handle_events(self, events):
        pass