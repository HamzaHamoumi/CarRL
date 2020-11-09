import pygame
import numpy as np
import os
import time
from math import cos, sin, radians


class View():
    car_filename = "carTopView.png"
    asset_path = "./Assets"
    checkpoint_size = 3
    checkpoint_arrow_length = 20

    def __init__(self, model_data):
        pygame.init()
        pygame.display.set_caption("Car Racing Reinforcement Learning")
        
        self.surface = pygame.display.set_mode((model_data["map_model"].shape[0], model_data["map_model"].shape[1]))
        map_model = np.absolute(model_data["map_model"] - 1) * 255
        self.surface.blit(pygame.surfarray.make_surface(map_model), pygame.Rect(0,0,0,0))
        pygame.display.flip()

        self.car_surface = pygame.image.load(os.path.join(View.asset_path, View.car_filename))
        car_coordinates = model_data["car"]["carPosition"].astype("int") - model_data["car"]["carSize"].astype("int") / 2
        self.previous_car_rect = pygame.Rect((car_coordinates), car_coordinates + model_data["car"]["carSize"].astype("int") / 2)
        self.textRect = None
        
        self.mouseLeftClicked = False
        self.mouseRightClicked = False

        self.checkpoint1_pos = np.array([], dtype="int")

    def update(self, model_data, results_prev):
        # Current Car Surface
        car_surface_transformed = pygame.transform.scale(self.car_surface, model_data["car"]["carSize"].astype("int"))
        car_surface_transformed = pygame.transform.rotate(car_surface_transformed, model_data["car"]["carOrientation"])
        car_surface_size = np.array(car_surface_transformed.get_size(), dtype="int")
        car_coordinates = model_data["car"]["carPosition"].astype("int") - car_surface_size / 2
        car_rect = pygame.Rect(car_coordinates, car_surface_size)

        # Previous Car surface to clean
        x = max(self.previous_car_rect.x, 0)
        y = max(self.previous_car_rect.y, 0)
        w = min(self.previous_car_rect.x + self.previous_car_rect.w, model_data["map_model"].shape[0]) - x
        h = min(self.previous_car_rect.y + self.previous_car_rect.h, model_data["map_model"].shape[1]) - y
        map_rect_to_update = pygame.Rect(x,y,w,h)

        map_model = model_data["map_model"][x: x + w, y: y + h]
        map_model = np.absolute(map_model - 1) * 255
        map_model_surface = pygame.surfarray.make_surface(map_model)
        self.surface.blit(map_model_surface, map_rect_to_update)

        # Clean Text rect
        if(self.textRect != None):
            map_model_text = model_data["map_model"][self.textRect.x: self.textRect.x + self.textRect.w, self.textRect.y: self.textRect.y + self.textRect.h]
            map_model_text = np.absolute(map_model_text - 1) * 255
            map_model_text_surface = pygame.surfarray.make_surface(map_model_text)
            self.surface.blit(map_model_text_surface, self.textRect)

        # Render Car
        self.surface.blit(car_surface_transformed, car_coordinates)

        # Display Text information
        font = pygame.font.SysFont("Calibri", 30, True, False)
        textStr = "Collision: " + ("True" if model_data["collision"] else "False")
        textStr += "  Score: " + str(int(model_data["score"]))
        text = font.render(textStr, True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.move(20, 20)
        self.surface.blit(text, textRect)
        self.textRect = textRect

        # draw checkpoints
        checkpoints = model_data["checkpoints"]
        for checkpoint in checkpoints:
            pygame.draw.line(self.surface, (0,255,0), checkpoint[0], checkpoint[1], View.checkpoint_size)

        # Update the screen surface
        pygame.display.update([map_rect_to_update, car_rect, textRect])
        self.previous_car_rect = car_rect

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

        return results

    def updateOnEdit(self, model_data):
        # Current Car Surface
        car_surface_transformed = pygame.transform.scale(self.car_surface, model_data["car"]["carSize"].astype("int"))
        car_surface_transformed = pygame.transform.rotate(car_surface_transformed, model_data["car"]["carOrientation"])
        car_surface_transformed.set_alpha(185)
        car_surface_size = np.array(car_surface_transformed.get_size(), dtype="int")
        car_coordinates = model_data["car"]["carPosition"].astype("int") - car_surface_size / 2
        car_rect = pygame.Rect(car_coordinates, car_surface_size)

        # Render the map
        map_model = np.absolute(model_data["map_model"] - 1)
        map_rgb = np.zeros((map_model.shape[0], map_model.shape[1], 3))
        map_rgb[:, :, 0] = map_model * 255
        map_rgb[:, :, 1] = map_model * 255
        map_rgb[:, :, 2] = map_model * 255
        pygame.surfarray.blit_array(self.surface, map_rgb)

        # Render Car
        self.surface.blit(car_surface_transformed, car_coordinates)

        # draw checkpoints
        orientation = radians(90)
        rot_matrix = np.array([[cos(orientation), -sin(orientation)],[sin(orientation), cos(orientation)]])

        checkpoints = model_data["checkpoints"]
        for checkpoint in checkpoints:
            pygame.draw.line(self.surface, (0,255,0), checkpoint[0], checkpoint[1], View.checkpoint_size)
            vect = (checkpoint[1] - checkpoint[0])
            vect /= np.linalg.norm(vect)
            vect_perpendicular = vect.dot(rot_matrix)
            vect_perpendicular /= np.linalg.norm(vect_perpendicular)
            center_point = (checkpoint[0] + checkpoint[1]) / 2
            point_start_arrow1 = center_point - View.checkpoint_arrow_length / 2 * vect
            point_start_arrow2 = center_point + View.checkpoint_arrow_length / 2 * vect
            pygame.draw.line(self.surface, (0,255,0), point_start_arrow1, center_point + View.checkpoint_arrow_length * vect_perpendicular , View.checkpoint_size)
            pygame.draw.line(self.surface, (0,255,0), point_start_arrow2, center_point + View.checkpoint_arrow_length * vect_perpendicular , View.checkpoint_size)
        if(self.checkpoint1_pos.size > 0):
            pygame.draw.line(self.surface, (255,0,0), self.checkpoint1_pos, pygame.mouse.get_pos(), View.checkpoint_size)

        # Update the screen surface
        pygame.display.flip()

        # Check user inputs
        results = {
            "run": True,
            "points_selected": [],
            "points_unselected": [],
            "car_pos": np.array([], dtype="int"),
            "checkpoint": np.array([], dtype="int")
        }
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                results["run"] = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Leaving the game")
                    results["run"] = False
                if event.key == pygame.K_SPACE:
                    print("Space Bar pressed")
                    results["car_pos"] = np.array(pygame.mouse.get_pos(), dtype="int")
                if event.key == pygame.K_c:
                    print("C button pressed")
                    self.checkpoint1_pos = np.array(pygame.mouse.get_pos(), dtype="int")
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_c:
                    print("C button released")
                    if(self.checkpoint1_pos.size > 0):
                        mouse_x = pygame.mouse.get_pos()[0]
                        mouse_y = pygame.mouse.get_pos()[1]
                        if(self.checkpoint1_pos[0] != mouse_x or self.checkpoint1_pos[1] != mouse_y):
                            results["checkpoint"] = np.array([self.checkpoint1_pos,pygame.mouse.get_pos()], dtype="int")
                        self.checkpoint1_pos = np.array([], dtype="int")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print("Mouse clicked !")
                if event.button == 1:
                    self.mouseLeftClicked = True
                    if(self.check_inside_screen(event.pos)):
                        results["points_selected"].append([event.pos[0], event.pos[1]])
                elif event.button == 3:
                    self.mouseRightClicked = True
                    if(self.check_inside_screen(event.pos)):
                        results["points_unselected"].append([event.pos[0], event.pos[1]])
            elif event.type == pygame.MOUSEBUTTONUP:
                print("Mouse click released !")
                if event.button == 1:
                    self.mouseLeftClicked = False
                elif event.button == 3:
                    self.mouseRightClicked = False
            elif event.type == pygame.MOUSEMOTION:
                print("Mouse moved !")
                if(event.buttons[0] == 1):
                    self.mouseLeftClicked = True
                    if(self.check_inside_screen(event.pos)):
                        results["points_selected"].append([event.pos[0], event.pos[1]])
                elif event.buttons[2] == 1:
                    self.mouseRightClicked = True
                    if(self.check_inside_screen(event.pos)):
                        results["points_unselected"].append([event.pos[0], event.pos[1]])
        return results

    def check_inside_screen(self, point):
        return point[0] >= 0 and point[0] < self.surface.get_width() and point[1] >= 0 and point[1] < self.surface.get_height()
