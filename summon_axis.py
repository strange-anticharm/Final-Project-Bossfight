import pygame
import math

class Axis:
    def __init__(self,x,y,size,rate,width):
        self.x = x
        self.y = y
        self.size = size
        self.rate = rate
        self.width = width
        self.left = self.x - size
        self.right = self.x + size
        self.top = self.y - size
        self.bottom = self.y + size
        self.c_left = self.x
        self.c_right = self.x
        self.c_top = self.y
        self.c_bottom = self.y

    def extend(self):
        self.c_left += (self.left - self.c_left)/self.rate
        self.c_right += (self.right - self.c_right)/self.rate
        self.c_top += (self.top - self.c_top)/self.rate
        self.c_bottom += (self.bottom - self.c_bottom)/self.rate

    def retract(self):
        self.c_left += (self.x - self.c_left)/self.rate
        self.c_right += (self.x - self.c_right)/self.rate
        self.c_top += (self.y - self.c_top)/self.rate
        self.c_bottom += (self.y - self.c_bottom)/self.rate
        if self.c_left//1 == self.x: self.c_left = self.x
        if self.c_right//1 == self.x: self.c_right = self.x
        if self.c_top//1 == self.y: self.top  = self.y
        if self.c_bottom//1 == self.y: self.bottom  = self.y
    

    def draw(self,canvas):
        pygame.draw.line(canvas,(0,0,0),(self.c_left,self.y),(self.c_right,self.y),self.width)
        pygame.draw.line(canvas,(0,0,0),(self.x,self.c_top),(self.x,self.c_bottom),self.width)