import math
import sympy
import pygame

class Power_rule:
    def __init__(self,x,y,angle,function):
        self.x = x
        self.y = y
        self.a , self.b = function
        #functions will always be of the type "ax^b" where a and b are inputed as a tuple
        self.function = f"{self.a}" + (f"x^{self.b}" if self.b > 1 else "x" if self.b == 1 else f"")
        self.speed = math.log(self.b) + 1
        self.angle = angle
        self.color = (50*abs(self.b) , 0 , 0)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 30)
        self.text = self.font.render(self.function,True,self.color)
        self.hitbox = self.text.get_rect(center=(self.x, self.y))
        self.alpha = 255

    def move(self,angle_update):
        self.angle = angle_update
        self.x += self.speed*math.cos(math.radians(self.angle))
        self.y += self.speed*math.sin(math.radians(self.angle))
        self.hitbox = self.text.get_rect(center=(self.x, self.y))
        if self.a == 0:
            self.alpha = max(self.alpha - 4 , 0)
        self.text.set_alpha(self.alpha)

    def differentiate(self):
        self.a *= self.b
        self.b -= (1 if self.b > 0 else 0)
        self.function = f"{self.a}" + (f"x^{self.b}" if self.b > 1 else "x" if self.b == 1 else f"")
        try:
            self.speed = math.log(self.b) + 1
        except:
            self.speed = 0
        self.color = (min(50*abs(self.b),255) , 0 , 0)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 30)
        self.text = self.font.render(self.function,True,self.color)
        self.hitbox = self.text.get_rect(center=(self.x, self.y))

    def draw(self,canvas):
        canvas.blit(self.text,self.hitbox)



