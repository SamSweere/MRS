import numpy as np


class KFLocalizer:
    def __init__(self, state_mu, state_std, motion_model, motion_noise, sensor_noise):
        self.state_mu = np.array(state_mu)
        # Get it into the right 3x3 dimensions
        self.state_mu = np.identity(self.state_mu.shape[0]) * self.state_mu

        self.state_std = np.array(state_std)
        self.motion_noise = np.array(motion_noise)
        self.sensor_noise = np.array(sensor_noise)

        self.motion_model = motion_model
        # Start with no z
        self.z = state_mu

    def predict(self, action, delta_time):
        # Add the noise to the state_mu
        self.state_mu += np.dot(self.state_mu, np.random.normal(0, self.motion_noise)) * (delta_time * 1000)

        # Note the real formula is A * state_mu + B * action
        # We assume A is an identity-matrix and B * action is represented by the motion model
        self.state_mu = np.identity(self.state_mu.shape[0])*np.array(self.motion_model(
            (self.state_mu[0][0], self.state_mu[1][1], self.state_mu[2][2]), action, delta_time))
        # Note the real formula is A * state_std * A^T + motion_noise
        self.state_std += self.motion_noise

        K = self.state_std*np.linalg.inv(self.state_std + self.sensor_noise)
        self.state_mu = self.state_mu + K*(np.subtract(self.z, self.state_mu))
        self.state_std = (np.identity(K.shape[0]) - K) * self.state_std

    def update_z(self, z, sensor_noise):
        # if z is none increase the sensor noise by allot
        if z is None:
            # Do not update z
            self.sensor_noise = sensor_noise*100000
        else:
            # Update z and reset senor noise
            self.z = z
            self.sensor_noise = sensor_noise