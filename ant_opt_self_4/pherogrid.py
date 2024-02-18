#pherogrid.py

import pygame as pg
from globals import *
import numpy as np

class PheroGrid():
    def __init__(self, bigSize):
        self.surfSize = (int(bigSize[0]/PRATIO), int(bigSize[1]/PRATIO))
        self.image = pg.Surface(self.surfSize).convert()
        self.img_array = np.array(pg.surfarray.array3d(self.image),dtype=float)#.astype(np.float64)

        
    def update(self, dt):
        evaporation_factor = 0.2 * (100/FPS) * (dt/10) * FPS
        self.img_array -= evaporation_factor
        self.img_array = np.clip(self.img_array, 0, 255)
        pg.surfarray.blit_array(self.image, self.img_array)
        return self.image