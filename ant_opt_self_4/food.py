#food.py

import pygame as pg

class Food(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pg.Surface((16, 16))
        self.image.fill(0)
        self.image.set_colorkey(0)
        pg.draw.circle(self.image, [2,150,2], [8, 8], 4)
        self.rect = self.image.get_rect(center=pos)
        
    def pickup(self):
        self.kill()