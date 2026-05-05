import pygame
import math


class Value:
    def __init__(self,value,startx,targetx,starty,targety,size,speed,duration):
        self.value = value
        self.x = startx
        self.targetx = targetx
        self.targety = targety
        self.y = starty
        self.size = size
        self.speed = speed
        self.font = pygame.font.Font("Roboto.ttf", self.size)
        self.text = self.font.render(f"{self.value}",True,(200,0,0))
        self.hitbox = self.text.get_rect(center=(self.x, self.y))
        self.duration = duration
        self.increment = 0

    def move(self):
        self.y += (self.targety - self.y)/self.speed
        self.x += (self.targetx - self.x)/self.speed
        self.increment += 1
        self.hitbox = self.text.get_rect(center=(self.x, self.y))
        if self.increment >= self.duration:
            return True

    def draw(self,canvas):
        canvas.blit(self.text,self.hitbox)