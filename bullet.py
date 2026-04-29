import pygame
import math

class Bullet:
    def __init__(self,slope,startx,starty,speed,width,length):
        self.angle = slope
        self.x = startx
        self.y = starty
        self.speed = speed
        self.dx = width
        self.dy = length
        self.surface = pygame.Surface((self.dx,self.dy), pygame.SRCALPHA)
        self.surface.fill((100, 100, 0)) 
        self.rotated_bullet = pygame.transform.rotate(self.surface, -math.degrees(self.angle))
        self.bullet_rect = self.rotated_bullet.get_rect(center=(self.x,self.y))

    def move(self,minx,miny,maxx,maxy):
        self.x += self.speed*math.cos(self.angle-math.pi/2)
        self.y += self.speed*math.sin(self.angle-math.pi/2)
        if minx > self.x or maxx < self.x or miny > self.y or maxy < self.y:
            return False

    def draw(self,canvas):
        self.rotated_bullet = pygame.transform.rotate(self.surface, -math.degrees(self.angle))
        self.bullet_rect = self.rotated_bullet.get_rect(center=(self.x,self.y))
        canvas.blit(self.rotated_bullet, self.bullet_rect)
        