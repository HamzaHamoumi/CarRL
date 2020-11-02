from Car import Car
import numpy as np
from math import cos, sin, radians


class Model:
    def __init__(self, width, height, mode):
        #self.map_model = np.random.randint(0, high=2, size=(width, height), dtype=int)
        if(mode == "run"):
            self.map_model = np.zeros((width, height), dtype="int")
            for x in range(self.map_model.shape[0]):
                for y in range(self.map_model.shape[1]):
                    if (x-width/2)**2 + (y-height/2)**2 > 200**2 and (x-width/2)**2 + (y-height/2)**2 < 250**2:
                        self.map_model[x][y] = 1

            for x in range(self.map_model.shape[0]):
                for y in range(self.map_model.shape[1]):
                    if (x-width/2)**2 + (y-height/2)**2 > 450**2 and (x-width/2)**2 + (y-height/2)**2 < 500**2:
                        self.map_model[x][y] = 1


            self.car = Car(int(50 * 2.17), 50, np.array([960, 200], dtype="float"))
            self.collision = False
            self.score = 0
        
        else:
            self.map_model = np.zeros((width, height), dtype="int")

    def get_map_model(self):
        return self.map_model.copy()

    def get_car_orientation(self):
        return self.car.get_orientation()

    def get_collision(self):
        return self.collision
    
    def get_score(self):
        return self.score

    def update(self, action, timestep):
        self.car.move(action, timestep)
        self.check_collision()

    def check_collision(self):
        orientation = radians(self.car.get_orientation())
        rot_matrix = np.array([[cos(orientation), sin(orientation)],[-sin(orientation), cos(orientation)]])

        d_w = self.car.get_size()[0] / 2
        d_h = self.car.get_size()[1] / 2
        topLeftCorner = np.array([d_w, d_h])
        topRightCorner = np.array([d_w, -d_h])
        bottomLeftCorner = np.array([-d_w, d_h])
        bottomRightCorner = np.array([-d_w, -d_h])

        topLeftCorner = (self.car.get_position() + topLeftCorner.dot(rot_matrix)).astype("int")
        topRightCorner = (self.car.get_position() + topRightCorner.dot(rot_matrix)).astype("int")
        bottomLeftCorner = (self.car.get_position() + bottomLeftCorner.dot(rot_matrix)).astype("int")
        bottomRightCorner = (self.car.get_position() + bottomRightCorner.dot(rot_matrix)).astype("int")

        print("Car position: ", self.car.get_position())
        print("topLeftCorner: ", topLeftCorner)

        if(self.map_model[topLeftCorner[0], topLeftCorner[1]] == 1):
            print("Collision: ", True)
            self.collision = True
        elif(self.map_model[topRightCorner[0], topRightCorner[1]] == 1):
            print("Collision: ", True)
            self.collision = True
        elif(self.map_model[bottomLeftCorner[0], bottomLeftCorner[1]] == 1):
            print("Collision: ", True)
            self.collision = True
        elif(self.map_model[bottomRightCorner[0], bottomRightCorner[1]] == 1):
            print("Collision: ", True)
            self.collision = True
        else:
            print("Collision: ", False)
            self.collision = False
