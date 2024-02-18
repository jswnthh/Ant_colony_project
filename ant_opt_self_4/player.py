#ant.py
import pygame 
import numpy as np
from random import randint
import math
from pherogrid import PheroGrid
from globals import *
 
class Vec2():
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
	def vint(self):
		return (int(self.x), int(self.y))
    

	
class Ant(pygame.sprite.Sprite):
   

    def __init__(self, drawSurface, nest_Position, pheroLayer):
        super().__init__()
        #self.antID = antNum
        self.drawSurface = drawSurface
        self.surfaceWidth, self.surfaceHeight = self.drawSurface.get_size()
        self.pygameSize = (int(self.surfaceWidth/PRATIO), int(self.surfaceHeight/PRATIO)) #tuple
        self.isMyTrail = np.full(self.pygameSize, False)
        self.pheroLayer = pheroLayer
        self.nest_Position = nest_Position
        self.image = pygame.Surface((12, 21)).convert()
        self.image.set_colorkey(0)

        pygame.draw.circle(self.image, [107, 54, 22], [8, 8], 5)

        self.orig_img = pygame.transform.rotate(self.image.copy(), -90)
        self.rect = self.image.get_rect(center=self.nest_Position)
        self.angle = randint(0, 360)
        self.desiredDirection = pygame.Vector2(math.cos(math.radians(self.angle)),math.sin(math.radians(self.angle)))
        self.pos = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2(0,0)
        self.last_sdp = (nest_Position[0]/PRATIO,nest_Position[1]/PRATIO)
        self.mode = 0

    def update(self, dt):  # behavior
        mid_result = left_result = right_result = [0,0,0]
        mid_GA_result = left_GA_result = right_GA_result = [0,0,0]

        randomAngle = randint(0,360)
        accel = pygame.Vector2(0,0)

        foodColor = (2,150,2)  # color of food to look for
        pStrength = 80  # Pheromone strength, evaps slowly
        wandrStr = .10  # how random they walk around
        maxSpeed = 12  # 10-12 seems ok
        steerStr = 3  # 3 or 4, dono
        
        # Update position for pheromone grid
        scaledown_pos = (int(self.pos.x/PRATIO), int(self.pos.y/PRATIO))
        
        # Define sensor offsets and positions
        mid_sensL = Vec2.vint(self.pos + pygame.Vector2(21, -3).rotate(self.angle))
        mid_sensR = Vec2.vint(self.pos + pygame.Vector2(21, 3).rotate(self.angle))
        left_sens1 = Vec2.vint(self.pos + pygame.Vector2(18, -14).rotate(self.angle))
        left_sens2 = Vec2.vint(self.pos + pygame.Vector2(16, -21).rotate(self.angle))
        right_sens1 = Vec2.vint(self.pos + pygame.Vector2(18, 14).rotate(self.angle))
        right_sens2 = Vec2.vint(self.pos + pygame.Vector2(16, 21).rotate(self.angle))
        # May still need to adjust these sensor positions, to improve following.

        

        if self.drawSurface.get_rect().collidepoint(mid_sensL) and self.drawSurface.get_rect().collidepoint(mid_sensR):
            mid_result, mid_isID, mid_GA_result = self.sensCheck(mid_sensL, mid_sensR)
        if self.drawSurface.get_rect().collidepoint(left_sens1) and self.drawSurface.get_rect().collidepoint(left_sens2):
            left_result, left_isID, left_GA_result = self.sensCheck(left_sens1, left_sens2)
        if self.drawSurface.get_rect().collidepoint(right_sens1) and self.drawSurface.get_rect().collidepoint(right_sens2):
            right_result, right_isID, right_GA_result = self.sensCheck(right_sens1, right_sens2)
            
        if self.mode == 0 and self.pos.distance_to(self.nest_Position) > 21:
            self.mode = 1

        elif self.mode == 1:  # Look for food, or trail to food.
            setAcolor = (0, 0, 100)
            # Check if the ant has moved to a new position
            if scaledown_pos != self.last_sdp and scaledown_pos[0] in range(0, self.pygameSize[0]) and scaledown_pos[1] in range(0, self.pygameSize[1]):
                # Add a scent trail
                self.pheroLayer.img_array[scaledown_pos] += setAcolor
                # Mark the position as part of the ant's trail
                self.isMyTrail[scaledown_pos] = True
                # Update the last position
                self.last_sdp = scaledown_pos
        
            # Check the results from sensors to determine movement
            if mid_result[1] > max(left_result[1], right_result[1]):
                self.desiredDirection += pygame.Vector2(1, 0).rotate(self.angle).normalize()
                wandrStr = .02
            elif left_result[1] > right_result[1]:
                self.desiredDirection += pygame.Vector2(1, -2).rotate(self.angle).normalize()
                wandrStr = .02
            elif right_result[1] > left_result[1]:
                self.desiredDirection += pygame.Vector2(1, 2).rotate(self.angle).normalize()
                wandrStr = .02

            # Check if food is detected
            if left_GA_result == foodColor and right_GA_result != foodColor:
                self.desiredDirection += pygame.Vector2(0, -1).rotate(self.angle).normalize()
                wandrStr = .02
            elif right_GA_result == foodColor and left_GA_result != foodColor:
                self.desiredDirection += pygame.Vector2(0, 1).rotate(self.angle).normalize()
                wandrStr = .02
            elif mid_GA_result == foodColor:
                # Head directly towards the food
                self.desiredDirection = pygame.Vector2(-1, 0).rotate(self.angle).normalize()
                maxSpeed = 12
                wandrStr = .05
                steerStr = 0.1
                self.mode = 2


        elif self.mode == 2:  # Once found food, either follow own trail back to nest_Position, or head in nest_Position's general direction.
            setAcolor = (0, 80, 0)
            # Check if the ant has moved to a new position
            if scaledown_pos != self.last_sdp and scaledown_pos[0] in range(0, self.pygameSize[0]) and scaledown_pos[1] in range(0, self.pygameSize[1]):
                # Add a scent trail
                self.pheroLayer.img_array[scaledown_pos] += setAcolor
                # Update the last position
                self.last_sdp = scaledown_pos

            # Check if the ant is close to the nest
            if self.pos.distance_to(self.nest_Position) < 24:
                # Head directly towards the nest
                self.desiredDirection = pygame.Vector2(-1, 0).rotate(self.angle).normalize()
                # Reset trail markers
                self.isMyTrail[:] = False
                maxSpeed = 8
                wandrStr = .02
                steerStr = 0.1
                self.mode = 1
            elif mid_result[2] > max(left_result[2], right_result[2]) and mid_isID:
                # Follow the scent trail in front
                self.desiredDirection += pygame.Vector2(1, 0).rotate(self.angle).normalize()
                wandrStr = .02
            elif left_result[2] > right_result[2] and left_isID:
                # Follow the scent trail on the left
                self.desiredDirection += pygame.Vector2(1, -2).rotate(self.angle).normalize()  # left (0,-1)
                wandrStr = .02
            elif right_result[2] > left_result[2] and right_isID:
                # Follow the scent trail on the right
                self.desiredDirection += pygame.Vector2(1, 2).rotate(self.angle).normalize()  # right (0, 1)
                wandrStr = .02
            else:
                # If no clear trail, head towards the nest's general direction
                self.desiredDirection += pygame.Vector2(self.nest_Position - self.pos).normalize() * .08
                wandrStr = .02
  #pygame.Vector2(self.desiredDirection + (1,0)).rotate(pygame.math.Vector2.as_polar(self.nest_Position - self.pos)[1])

        wallColor = (50,50,50)  # avoid walls of this color
        '''
        collision in pygame

        you always use a rects for collision (and also movement)
        but here we are using color
        
        '''
        if left_GA_result == wallColor:
            self.desiredDirection += pygame.Vector2(0,1).rotate(self.angle) #.normalize()
            wandrStr = .01
            steerStr = 6
        elif right_GA_result == wallColor:
            self.desiredDirection += pygame.Vector2(0,-1).rotate(self.angle) #.normalize()
            wandrStr = .01
            steerStr = 6
        elif mid_GA_result == wallColor:
            self.desiredDirection += pygame.Vector2(-2,0).rotate(self.angle) #.normalize()
            maxSpeed = 8
            wandrStr = .01
            steerStr = 6

        # Avoid edges
        if not self.drawSurface.get_rect().collidepoint(left_sens2) and self.drawSurface.get_rect().collidepoint(right_sens2):
            self.desiredDirection += pygame.Vector2(0,1).rotate(self.angle) #.normalize()
            wandrStr = .01
            steerStr = 5
        elif not self.drawSurface.get_rect().collidepoint(right_sens2) and self.drawSurface.get_rect().collidepoint(left_sens2):
            self.desiredDirection += pygame.Vector2(0,-1).rotate(self.angle) #.normalize()
            wandrStr = .01
            steerStr = 5
        elif not self.drawSurface.get_rect().collidepoint(Vec2.vint(self.pos + pygame.Vector2(21, 0).rotate(self.angle))):
            self.desiredDirection += pygame.Vector2(-1,0).rotate(self.angle) #.normalize()
            maxSpeed = 8
            wandrStr = .01
            steerStr = 5

        randDir = pygame.Vector2(math.cos(math.radians(randomAngle)),math.sin(math.radians(randomAngle)))
        self.desiredDirection = pygame.Vector2(self.desiredDirection + randDir * wandrStr).normalize()
        dzvelocity = self.desiredDirection * maxSpeed
        dzStrFrc = (dzvelocity - self.velocity) * steerStr
        accel = dzStrFrc if pygame.Vector2(dzStrFrc).magnitude() <= steerStr else pygame.Vector2(dzStrFrc.normalize() * steerStr)
        velocityo = self.velocity + accel * dt
        self.velocity = velocityo if pygame.Vector2(velocityo).magnitude() <= maxSpeed else pygame.Vector2(velocityo.normalize() * maxSpeed)
        self.pos += self.velocity * dt
        self.angle = math.degrees(math.atan2(self.velocity[1],self.velocity[0]))
        # adjusts angle of img to match heading
        self.image = pygame.transform.rotate(self.orig_img, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        # actually update position
        self.rect.center = self.pos

    def sensCheck(self, pos1, pos2): # checks given points in Array, IDs, and pixels on screen.
        sdpos1 = (int(pos1[0]/PRATIO),int(pos1[1]/PRATIO))
        sdpos2 = (int(pos2[0]/PRATIO),int(pos2[1]/PRATIO))
        array_r1 = self.pheroLayer.img_array[sdpos1]
        array_r2 = self.pheroLayer.img_array[sdpos2]
        array_result = (max(array_r1[0], array_r2[0]), max(array_r1[1], array_r2[1]), max(array_r1[2], array_r2[2]))

        is1ID = self.isMyTrail[sdpos1]
        is2ID = self.isMyTrail[sdpos2]
        isID = is1ID or is2ID

        ga_r1 = self.drawSurface.get_at(pos1)[:3]
        ga_r2 = self.drawSurface.get_at(pos2)[:3]
        ga_result = (max(ga_r1[0], ga_r2[0]), max(ga_r1[1], ga_r2[1]), max(ga_r1[2], ga_r2[2]))

        return array_result, isID, ga_result    

