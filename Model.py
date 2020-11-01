from Car import Car
import numpy as np


class Model:
    def __init__(self, width, height):
        #self.map_model = np.random.randint(0, high=2, size=(width, height), dtype=int)
        self.map_model = np.zeros((width, height), dtype="int")
        for x in range(self.map_model.shape[0]):
            for y in range(self.map_model.shape[1]):
                if (x-width/2)**2 + (y-height/2)**2 > 200**2 and (x-width/2)**2 + (y-height/2)**2 < 250**2:
                    self.map_model[x][y] = 1

        for x in range(self.map_model.shape[0]):
            for y in range(self.map_model.shape[1]):
                if (x-width/2)**2 + (y-height/2)**2 > 450**2 and (x-width/2)**2 + (y-height/2)**2 < 500**2:
                    self.map_model[x][y] = 1


        self.car = Car(int(75 * 2.17), 75, np.array([0, 0], dtype="float"))

    def get_map_model(self):
        return self.map_model.copy()

    def get_car_orientation(self):
        return self.car.get_orientation()

    def update(self, action, timestep):
        self.car.move(action, timestep)
