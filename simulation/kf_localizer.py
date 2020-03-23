import numpy as np


class KFLocalizer:
    def __init__(self, state_mu, state_std, motion_model, motion_noise, sensor_noise):
        self.state_mu = np.array(state_mu)
        self.state_std = np.array(state_std)
        self.motion_noise = np.array(motion_noise)
        self.sensor_noise = np.array(sensor_noise)

        self.motion_model = motion_model

    def predict(self, action, delta_time):
        # Add the noise to the state_mu only if the action is not nothing
        # No need to add noise if we know we are standing still
        #if action[0] != 0:
            #self.state_mu += np.dot(self.state_mu, np.random.normal(0, self.motion_noise)) * (delta_time * 1000)

        # Note the real formula is A * state_mu + B * action
        # We assume A is an identity-matrix and B * action is represented by the motion model
        self.state_mu = self.motion_model(self.state_mu, action, delta_time)
        # Note the real formula is A * state_std * A^T + motion_noise
        self.state_std += self.motion_noise
        
    def correct(self, z):
        z = np.array(z)
        # C is identity in all calculations
        K = np.matmul(self.state_std, np.linalg.inv(self.state_std + self.sensor_noise))
        self.state_mu = self.state_mu + np.matmul(K, z - self.state_mu)
        self.state_std = np.matmul((np.identity(K.shape[0]) - K), self.state_std)