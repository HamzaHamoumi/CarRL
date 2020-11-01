import pygame
import numpy as np
import os
import time


class View():
    car_filename = "carTopView.png"
    asset_path = "./Assets"

    def __init__(self, model_data):
        pygame.init()
        pygame.display.set_caption("Car Racing Reinforcement Learning")
        self.surface = pygame.display.set_mode((model_data["map_model"].shape[0], model_data["map_model"].shape[1]))
        
        map_model = np.absolute(model_data["map_model"] - 1)
        map_rgb = np.zeros((map_model.shape[0], map_model.shape[1], 3))
        map_rgb[:, :, 0] = map_model * 255
        map_rgb[:, :, 1] = map_model * 255
        map_rgb[:, :, 2] = map_model * 255
        pygame.surfarray.blit_array(self.surface, map_rgb)
        pygame.display.flip()

        self.car_surface = pygame.image.load(os.path.join(View.asset_path, View.car_filename))
        self.previous_car_coordinates = self.transformCoordinates(np.zeros(2)) - model_data["car"]["carSize"].astype("int") / 2

    def update(self, model_data, results_prev):
        start = time.time()
        car_surface_transformed = pygame.transform.scale(self.car_surface, model_data["car"]["carSize"].astype("int"))
        car_surface_transformed = pygame.transform.rotate(car_surface_transformed, model_data["car"]["carOrientation"])
        car_surface_size = np.array(car_surface_transformed.get_size(), dtype="int")
        car_coordinates = self.transformCoordinates(model_data["car"]["carPosition"]).astype("int") - car_surface_size / 2
        car_rect = pygame.Rect(car_coordinates, car_surface_size)

        x = max(self.previous_car_coordinates[0], 0)
        y = max(self.previous_car_coordinates[1], 0)
        w = min(self.previous_car_coordinates[0] + 2 * car_surface_size[0], model_data["map_model"].shape[0]) - x
        h = min(self.previous_car_coordinates[1] + 2 * car_surface_size[1], model_data["map_model"].shape[1]) - y
        map_rect_to_update = pygame.Rect(x, y, w, h)

        map_model = model_data["map_model"][map_rect_to_update.x: map_rect_to_update.x + map_rect_to_update.w, map_rect_to_update.y: map_rect_to_update.y + map_rect_to_update.h]
        map_model = np.absolute(map_model - 1)
        map_rgb = np.zeros((map_model.shape[0], map_model.shape[1], 3))
        map_rgb[:, :, 0] = map_model * 255
        map_rgb[:, :, 1] = map_model * 255
        map_rgb[:, :, 2] = map_model * 255
        end = time.time()
        print(f"Runtime of the program is {end - start}")
        map_model_surface = pygame.surfarray.make_surface(map_rgb)
        self.surface.blit(map_model_surface, map_rect_to_update)

        #self.surface.fill(pygame.Color(255, 255, 255))

        self.surface.blit(car_surface_transformed, car_coordinates)

        # Check user inputs
        results = {
            "run": True,
            "moveInput": results_prev["moveInput"].copy()
        }
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                results["run"] = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    print("you pressed the down key")
                    results["moveInput"][0] = 1
                elif event.key == pygame.K_DOWN:
                    print("you pressed the up key")
                    results["moveInput"][1] = 1
                elif event.key == pygame.K_LEFT:
                    print("you pressed the left key")
                    results["moveInput"][2] = 1
                elif event.key == pygame.K_RIGHT:
                    print("you pressed the right key")
                    results["moveInput"][3] = 1
                elif event.key == pygame.K_ESCAPE:
                    print("Leaving the game")
                    results["run"] = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    print("you released the down key")
                    results["moveInput"][0] = 0
                elif event.key == pygame.K_DOWN:
                    print("you released the up key")
                    results["moveInput"][1] = 0
                elif event.key == pygame.K_LEFT:
                    print("you released the left key")
                    results["moveInput"][2] = 0
                elif event.key == pygame.K_RIGHT:
                    print("you released the right key")
                    results["moveInput"][3] = 0

        pygame.display.update([map_rect_to_update, car_rect])
        self.previous_car_coordinates = car_coordinates

        return results

    def transformCoordinates(self, coords):
        x = coords[0]
        y = - coords[1] + self.surface.get_height()
        return np.array([x, y])
