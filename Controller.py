from Model import Model
from View import View
import numpy as np
import pygame
import time


class Controller:
    def __init__(self, mode = "run"):
        print("Mode: ", mode)
        self.mode = mode
        self.model = Model(1200, 720, self.mode)
        model_data = {
                "map_model": self.get_map_model_for_view(),
                "car": {
                    "carPosition": self.model.car.get_position(),
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
                    "carPosition": self.model.car.get_position(),
                    "carOrientation": self.model.get_car_orientation(),
                    "carSize": self.model.car.get_size()
                },
                "collision": self.model.get_collision(),
                "score": self.model.get_score()
            }
            view_results = self.view.update(model_data, view_results)

            # Update the model
            end_time = time.time()
            print(f"Runtime of the program is {end_time - start_time}")
            #if(not(self.model.get_collision())):
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
                "map_model": self.model.get_map_model(),
                "car": {
                    "carPosition": self.model.car.get_position(),
                    "carOrientation": self.model.get_car_orientation(),
                    "carSize": self.model.car.get_size()
                }
            }
            view_results = self.view.updateOnEdit(model_data)

            print(view_results)

            # Update the model
            end_time = time.time()
            print(f"Runtime of the program is {end_time - start_time}")
            #if(not(self.model.get_collision())):
            self.model.updateOnEdit()

    def get_map_model_for_view(self):
        return np.flip(self.model.get_map_model(), 1)
