import pygame 
import math
import sys

from pherogrid import *
from player import *
from food import Food
from globals import *

class Simulation:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("ANT COLONY SIMULATION")

        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) #sets the window size
        self.clock = pygame.time.Clock() #to stabilize the framerate

        self.cur_w, self.cur_h = self.screen.get_size() #probably gets the screen size, idk why id does because screensize is alread set in globals
        self.screen_size = (self.cur_w, self.cur_h)
        self.nest_position = (self.cur_w /2, self.cur_h / 2)
        self.phero_layer = PheroGrid(self.screen_size)

        # self.cave = pygame.sprite.Group()
        # self.cave.add(CaveSprite(self.screen, 10, PRATIO))
        
        self.workers = pygame.sprite.Group()
        for _ in range(ANTS):
            self.workers.add(Ant(self.screen, self.nest_position, self.phero_layer))
        
        #list of food sprites
        self.food_list = []  
        self.foods = pygame.sprite.Group() # foods is a group
        

        self.dt = 0  # Define dt as an instance variable
        self.fps_checker = 0  # Define fps_checker as an instance variable

    def run(self):
        self.running = True
        while self.running:
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:
                    food_bits = 200
                    self.f_radius = 50
                    for i in range(food_bits):
                        dist = pow(i / (food_bits - 1.0), 0.5) * self.f_radius
                        angle = 2 * math.pi * 0.618033 * i
                        fx = mouse_pos[0] + dist * math.cos(angle)
                        fy = mouse_pos[1] + dist * math.sin(angle)
                        self.foods.add(Food((fx, fy))) #adds Foods sprite and its position to the sprite group
                    self.food_list.extend(self.foods.sprites()) 
                    
                if event.button == 3:
                    for bit in self.food_list:
                        if pygame.Vector2(mouse_pos).distance_to(bit.rect.center) < self.f_radius + 5:
                            bit.pickup()
                    self.food_list = self.foods.sprites()

    def update(self):
        self.handle_events()
        self.dt = self.clock.tick(FPS) / 100  # Update dt here
        self.workers.update(self.dt)
        # self.cave.update(self.dt)

    def draw(self):
        phero_img = self.phero_layer.update(self.dt)  # Use self.dt here
        rescaled_img = pygame.transform.scale(phero_img, (self.cur_w, self.cur_h))
        pygame.Surface.blit(self.screen, rescaled_img, (0, 0))

        self.foods.draw(self.screen)
        pygame.draw.circle(self.screen, [100, 0, 0], (self.nest_position[0], self.nest_position[1] + 6), 25, 0)

        # pg.draw.rect(self.screen, (50,50,50), [1000, 550, 400, 60]) # test wall
        # pg.draw.rect(self.screen, (50,50,50), [900, 300, 60, 400])
        # pg.draw.rect(self.screen, (50,50,50), [1200, -25, 60, 300])
        # pg.draw.rect(self.screen, (50,50,50), [400, 275, 60, 300])
        # pg.draw.rect(self.screen, (50,50,50), [0, 100, 400, 60])
        # # pg.draw.rect(self.screen, (50,50,50), [200, 300, 50, 500])

        self.workers.draw(self.screen)

        pygame.display.update()

        # Outputs framerate once per second
        self.fps_checker += 1
        if self.fps_checker >= FPS:
            print(round(self.clock.get_fps(), 2))
            self.fps_checker = 0

    def close(self):
        pygame.quit()
        sys.quit()

if __name__ == '__main__':
    simulation = Simulation()
    simulation.run()
