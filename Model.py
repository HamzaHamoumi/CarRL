from Car import Car
import numpy as np
from math import cos, sin, tan, radians, sqrt
import os


class Model:
    map_dir = os.path.join(".\\Maps")
    collision_mallus = 1000
    time_mallus = 50
    checkpoint_crossed_bonus = 100
    distance_bonus = 0.5
    detectors_orientation = [-90, -45, 0, 45, 90]
    detection_search_step = 1

    def __init__(self, width, height, mode, map_name):
        # Load map file
        self.create_map_dir()
        # Load map model
        self.map_name = map_name
        if(os.path.exists(os.path.join(Model.map_dir, self.map_name + ".npz"))):
            model_file = np.load(os.path.join(Model.map_dir, self.map_name + ".npz"))
            if("map_model" in model_file.files):
                self.map_model = model_file["map_model"]
            else:
                print("Corrupted Map file")

            if("car_pos" in model_file.files):
                self.car = Car(int(25 * 2.17), 25, model_file["car_pos"])
            else:
                print("Corrupted Map file")
            
            if("checkpoints" in model_file.files):
                self.checkpoints = model_file["checkpoints"]
            model_file.close()
        else:
            self.map_model = np.zeros((width, height), dtype="int")
            self.car = Car(int(25 * 2.17), 25, self.get_center())
            self.car.set_wall_detection(0, self.detect_wall(self.car.get_orientation()))
            self.checkpoints = np.array([], dtype="float")

        self.collision = False
        self.score = 0
        for detector_orientation in Model.detectors_orientation:
            self.car.set_wall_detection(detector_orientation, self.detect_wall(self.car.get_orientation() + detector_orientation))

    def get_map_model(self):
        return self.map_model.copy()

    def get_map_model_size(self):
        return self.map_model.shape

    def get_car_orientation(self):
        return self.car.get_orientation()

    def get_collision(self):
        return self.collision
    
    def get_score(self):
        return self.score

    def get_center(self):
        return np.array(self.get_map_model_size(), dtype="float") / 2

    def get_checkpoints(self):
        return self.checkpoints.copy()

    def add_checkpoint(self, checkpoint):
        if(self.checkpoints.size > 0):
            self.checkpoints = np.append(self.checkpoints, checkpoint, axis=0)
        else:
            self.checkpoints = checkpoint.astype("float")
    
    def get_wall_detections(self):
        wall_detections = []
        for detector_orientation in Model.detectors_orientation:
            wall_detections.append(self.car.get_wall_detection(detector_orientation))
        return np.array(wall_detections)

    def remove_checkpoint(self, pos, margin):
        if(self.checkpoints.size > 0):
            for i in range(self.checkpoints.shape[0]):
                checkpoint = self.checkpoints[i]
                m = (checkpoint[1][1] - checkpoint[0][1]) / (checkpoint[1][0] - checkpoint[0][0])
                p = checkpoint[0][1] - m * checkpoint[0][0]
                min_x = min(checkpoint[0][0], checkpoint[1][0]) - margin
                max_x = max(checkpoint[0][0], checkpoint[1][0]) + margin
                distance_point_to_checkpoint = abs(-m * pos[0] + pos[1] - p) / sqrt(m**2 + 1)
                if( distance_point_to_checkpoint < margin and pos[0] > min_x and pos[0] < max_x):
                    self.checkpoints = np.delete(self.checkpoints, i, 0)
                    break

    def check_checkpoints_crossed(self, prev_car_pos, next_car_pos):
        nb_checkpoint_crossed = 0
        if(self.checkpoints.size > 0):
            orientation = radians(90)
            rot_matrix = np.array([[cos(orientation), sin(orientation)],[-sin(orientation), cos(orientation)]])
            for checkpoint in self.checkpoints:
                vect_checkpoint = checkpoint[1] - checkpoint[0]
                vect_perpendicular_checkpoint = vect_checkpoint.dot(rot_matrix)
                center_point = (checkpoint[0] + checkpoint[1]) / 2
                vect_center_to_prev_pos = prev_car_pos - center_point
                vect_center_to_next_pos = next_car_pos - center_point
                if vect_center_to_prev_pos.dot(vect_perpendicular_checkpoint) <= 0 and vect_center_to_next_pos.dot(vect_perpendicular_checkpoint) > 0:
                    nb_checkpoint_crossed += 1
        return nb_checkpoint_crossed

    def update(self, action, timestep):
        prev_car_pos = self.car.get_position()
        self.car.move(action, timestep)
        next_car_pos = self.car.get_position()
        self.check_collision()
        if(not self.collision):
            self.score += Model.distance_bonus * np.linalg.norm(next_car_pos - prev_car_pos)
            self.score -= Model.time_mallus * timestep
            self.score += Model.checkpoint_crossed_bonus * self.check_checkpoints_crossed(prev_car_pos, next_car_pos)
            for detector_orientation in Model.detectors_orientation:
                self.car.set_wall_detection(detector_orientation, self.detect_wall(self.car.get_orientation() + detector_orientation))
        else:
            self.score -= Model.collision_mallus

    def detect_wall(self, direction):
        car_pos = self.car.get_position()
        if not direction%360 in [90, 270]:
            m = tan(radians(direction))
            p = car_pos[1] - m * car_pos[0]
            delta_x_direction = cos(radians(direction)) / abs(cos(radians(direction)))
            delta_x = delta_x_direction * sqrt(1 / (1 + m**2)) * Model.detection_search_step
            cursor = car_pos.copy()
            wall_found = False
            while self.is_point_inside(np.around(cursor)) and not wall_found:
                if self.map_model[round(cursor[0]), round(cursor[1])] == 1:
                    wall_found = True
                else:
                    cursor[0] += delta_x
                    cursor[1] = m * cursor[0] + p
        else:
            cursor = car_pos.copy()
            delta_y_direction = sin(radians(direction)) / abs(sin(radians(direction)))
            delta_y = delta_y_direction * Model.detection_search_step
            wall_found = False
            while self.is_point_inside(np.around(cursor)) and not wall_found:
                if self.map_model[round(cursor[0]), round(cursor[1])] == 1:
                    wall_found = True
                else:
                    cursor[1] += delta_y

        return cursor

    def is_point_inside(self, point):
        model_size = self.get_map_model_size()
        return point[0] >= 0 and point[0] < model_size[0] and point[1] >= 0 and point[1] < model_size[1]
    
    def remove_outside_points(self, points):
        if(points.size > 0 and points.ndim == 2):
            filter = []
            for i in range(points.shape[0]):
                filter.append(self.is_point_inside(points[i]))
            return points[filter]

    def updateOnEdit(self, action):
        if(action["car_pos"].size > 0):
            if(self.is_point_inside(action["car_pos"])):
                self.car.set_position(action["car_pos"][0], action["car_pos"][1])

        if(action["points_selected"].size > 0 and action["points_selected"].ndim == 2):
            action["points_selected"] = self.remove_outside_points(action["points_selected"])
            self.map_model[action["points_selected"][:,0], action["points_selected"][:,1]] = 1

        if(action["points_unselected"].size > 0 and action["points_unselected"].ndim == 2):
            action["points_unselected"] = self.remove_outside_points(action["points_unselected"])
            self.map_model[action["points_unselected"][:,0], action["points_unselected"][:,1]] = 0

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

    def save_model(self):
        self.create_map_dir()
        np.savez(os.path.join(Model.map_dir, self.map_name), map_model=self.get_map_model(), car_pos=self.car.get_position(), checkpoints=self.get_checkpoints())
        print("Map saved")
    
    def create_map_dir(self):
        if not os.path.exists(Model.map_dir) or not os.path.isdir(Model.map_dir):
            os.mkdir(Model.map_dir)