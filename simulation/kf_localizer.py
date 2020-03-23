import numpy as np


class KFLocalizer:
    def __init__(self, state_mu, state_std, motion_model, motion_noise):
        self.state_mu = np.array(state_mu)

        self.state_std = np.array(state_std)
        self.motion_noise = np.array(motion_noise)

        self.motion_model = motion_model

    def predict(self, action, delta_time):
        # Note the real formula is A * state_mu + B * action
        # We assume A is an identity-matrix and B * action is represented by the motion model
        self.state_mu = self.motion_model(self.state_mu, action, delta_time)
        # Note the real formula is A * state_std * A^T + motion_noise
        self.state_std += self.motion_noise

    def update_z(self, z):
        self.z = z #Note: z can be None
