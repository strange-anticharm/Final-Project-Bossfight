import pygame
import math


class Number:
    def __init__(self,value,angle,startx,starty,speed):
        self.value = value
        self.angle = angle
        self.x = startx
        self.y = starty
        self.speed = speed
        self.font = pygame.font.Font(pygame.font.get_default_font(), 30)
        self.text = self.font.render(f"-{self.value}",True,(150,0,0))
        self.display = pygame.transform.rotate(self.text,-self.angle)
        self.rect = self.display.get_rect(center=(self.x,self.y))
        self.hitbox = self.text.get_rect(center=(self.x, self.y))

    def move(self):
        self.x += self.speed*math.cos(math.radians(self.angle))
        self.y += self.speed*math.sin(math.radians(self.angle))
        self.rect = self.display.get_rect(center=(self.x,self.y))
        self.hitbox = self.text.get_rect(center=(self.x, self.y))

    def draw(self,canvas):
        canvas.blit(self.display,self.rect)