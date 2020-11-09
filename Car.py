import numpy as np
from math import cos, sin, radians, pow, sqrt, exp

class Car:
    def __init__(self, width, length, position):
        self.size = np.array([width, length], dtype="float")
        self.position = np.array(position, dtype="float")
        self.orientation = 0
        self.angle_per_sec = 90
        self.angle_coeff1 = 1000#50
        self.angle_coeff2 = 0.001
        self.angle_coeff3 = 15000
        self.v = 0
        self.v_treshold = 0.1
        self.a = 0
        self.mu_fr = 0.5
        self.mu_brake_fr = 3.0
        self.couple = 190
        self.course = 0.0946
        self.nb_cylindre = 3
        self.masse = 1300

    def get_position(self):
        return self.position.copy()
    
    def set_position(self, x, y):
        self.position = np.array([x,y])

    def get_size(self):
        return self.size

    def get_motricity_force(self, action):
        if(action[0] - action[1]) > 0:
            return self.couple / (self.nb_cylindre * self.course)
        elif (action[0] - action[1]) <= 0:
            return 0.0

    def move(self, action, timestep):
        # change orientation
        if(self.v != 0):
            self.orientation += (action[2] - action[3]) * self.angle_per_sec * timestep * exp(-self.v / self.angle_coeff1)
            self.orientation %= 360
        #self.orientation += self.angle_coeff1 * pow(self.v, 2)/( self.angle_coeff2 * pow(self.v,3) + self.angle_coeff3) \
        #                    * (action[2] - action[3]) * timestep
        #self.orientation += self.angle_coeff1 * sqrt(self.v) / (pow(self.v, 3) + self.angle_coeff2) * (
                    #action[2] - action[3]) * timestep

        # estimate next acceleration, speed and position
        mu_tot = self.mu_fr +  self.mu_brake_fr * (1 if (action[1] - action[0]) > 0 else 0)
        self.a = self.get_motricity_force(action) - mu_tot * self.v
        self.v += self.a * timestep

        self.v = self.v if self.v > self.v_treshold else 0.0

        dx = self.v * timestep * cos(radians(self.orientation))
        dy = self.v * timestep * sin(radians(self.orientation))
        self.position += np.array([dx, dy], dtype="float")

    def get_orientation(self):
        return self.orientation
