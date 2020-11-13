from Model import Model
from View import View
import numpy as np
import pygame
import time
import copy


class Controller:
    def __init__(self, mode = "run", map_name = "default"):
        self.mode = mode
        self.cursor_size = 10
        self.checkpoint_removal_margin = 4
        self.model = Model(1200, 720, self.mode, map_name)
        model_data = {
                "map_model": self.get_map_model_for_view(),
                "car": {
                    "carPosition": self.transform_coords_view_and_model(self.model.car.get_position()),
                    "carOrientation": self.model.get_car_orientation(),
                    "carSize": self.model.car.get_size()
                }
            }
        self.view = View(model_data)
    
    def start(self):
        if self.mode == "run":
            self.run_game()
        elif self.mode == "edit":
            self.run_edit()

    def run_game(self):
        view_results = {
            "run": True,
            "moveInput": np.zeros(4, dtype="int")
        }
        while view_results["run"]:
            start_time = time.time()

            # Update the view
            model_data = {
                "map_model": self.get_map_model_for_view(),
                "car": {
                    "carPosition": self.transform_coords_view_and_model(self.model.car.get_position()),
                    "carOrientation": self.model.get_car_orientation(),
                    "carSize": self.model.car.get_size(),
                    "wall_detections": self.transform_array_of_coords_view_and_model(self.model.get_wall_detections())
                },
                "collision": self.model.get_collision(),
                "score": self.model.get_score(),
                "checkpoints": self.transform_checkpoints_coords_view_and_model(self.model.get_checkpoints())
            }
            view_results = self.view.update(model_data, view_results)

            # Update the model
            end_time = time.time()
            print(f"Runtime of the program is {end_time - start_time}")
            if(not(self.model.get_collision())):
                self.model.update(view_results["moveInput"], end_time - start_time)
    
    def run_edit(self):
        view_results = {
            "run": True,
            "moveInput": np.zeros(4, dtype="int")
        }
        while view_results["run"]:
            start_time = time.time()

            # Update the view
            model_data = {
                "map_model": self.get_map_model_for_view(),
                "checkpoints": self.transform_checkpoints_coords_view_and_model(self.model.get_checkpoints()),
                "car": {
                    "carPosition": self.transform_coords_view_and_model(self.model.car.get_position()),
                    "carOrientation": self.model.get_car_orientation(),
                    "carSize": self.model.car.get_size()
                }
            }
            view_results = self.view.updateOnEdit(model_data)
            print(view_results)
            end_time = time.time()

            # remove checkpoint
            if len(view_results["points_unselected"]) > 0:
                for point_unselected in view_results["points_unselected"]:
                    self.model.remove_checkpoint(self.transform_coords_view_and_model(np.array(point_unselected)), self.checkpoint_removal_margin)

            # inflate clicked points to have a circle
            view_results["points_selected"] = self.inflate_points(view_results["points_selected"])
            view_results["points_unselected"] = self.inflate_points(view_results["points_unselected"])
            # convert clicked points to an array
            view_results["points_selected"] = np.array(view_results["points_selected"], dtype="int")
            view_results["points_unselected"] = np.array(view_results["points_unselected"], dtype="int")
            # convert points to model axis
            view_results["points_selected"] = self.transform_array_of_coords_view_and_model(view_results["points_selected"])
            view_results["points_unselected"] = self.transform_array_of_coords_view_and_model(view_results["points_unselected"])
            view_results["car_pos"] = self.transform_coords_view_and_model(view_results["car_pos"])
            # add checkpoint if any
            if view_results["checkpoint"].size > 0:
                checkpoint_to_add = np.array([view_results["checkpoint"]])
                self.model.add_checkpoint(self.transform_checkpoints_coords_view_and_model(checkpoint_to_add)) 

            # Update the model
            print(f"Runtime of the program is {end_time - start_time}")
            #if(not(self.model.get_collision())):
            self.model.updateOnEdit(view_results)
        self.model.save_model()

    def get_map_model_for_view(self):
        return np.flip(self.model.get_map_model(), 1)

    def transform_coords_view_and_model(self, coords):
        if(coords.size > 0):
            x = coords[0]
            y = - coords[1] + self.model.get_map_model_size()[1]
            return np.array([x, y])
        else:
            return coords
    
    def transform_array_of_coords_view_and_model(self, coords):
        if(coords.ndim == 2):
            coords[:,1] = - coords[:,1] + self.model.get_map_model_size()[1]
        return coords

    def transform_checkpoints_coords_view_and_model(self, checkpoints):
        if(checkpoints.size > 0 and checkpoints.ndim == 3):
            checkpoints[:, 0, :] = self.transform_array_of_coords_view_and_model(checkpoints[:, 0, :])
            checkpoints[:, 1, :] = self.transform_array_of_coords_view_and_model(checkpoints[:, 1, :])
        return checkpoints  

    def inflate_points(self, points):
        points_inflated = copy.deepcopy(points)
        map_size = self.model.get_map_model_size()
        square_cursor_size = self.cursor_size**2
        for i in range(len(points)):
            xi = points[i][0]
            yi = points[i][1]
            for x in range(max(xi - self.cursor_size, 0), min(xi + self.cursor_size, map_size[0])):
                for y in range(max(yi - self.cursor_size, 0), min(yi + self.cursor_size, map_size[1])):
                    print(x,y)
                    if((x-xi)**2 + (y-yi)**2 < square_cursor_size):
                        points_inflated.append([x, y])
        return points_inflated