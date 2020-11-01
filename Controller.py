from Model import Model
from View import View
import numpy as np
import pygame
import time


class Controller:
    def __init__(self):
        self.model = Model(1920, 1080)
        model_data = {
                "map_model": self.model.get_map_model(),
                "car": {
                    "carPosition": self.model.car.get_position(),
                    "carOrientation": self.model.get_car_orientation(),
                    "carSize": self.model.car.get_size()
                }
            }
        self.view = View(model_data)

    def run_game(self):
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
            view_results = self.view.update(model_data, view_results)

            # Update the model
            end_time = time.time()
            print(f"Runtime of the program is {end_time - start_time}")
            self.model.update(view_results["moveInput"], end_time - start_time)
