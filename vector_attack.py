import random
from summon_axis import Axis
import math
import pygame

#new class to make the vectr attack better

class VectorAttack:
    def __init__(self,player_pos):
        self.vc_index = 0
        self.axis = Axis(player_pos[0],player_pos[1],200,10,5)
        self.list_of_vectors = [[random.randint(-5,5),random.randint(-5,5)] for i in range(5)]
        self.list_of_positions = [[self.axis.x,self.axis.y] for i in range(5)]
        self.vector_text = ""
        self.done = False

    def update(self,screen,vector_surface,player_surface,player_pos,
               player_in_dash,player_in_iframe,player_iframe_duration,
               player_hp,bigger_font,current_phase,damage_sfx):
        vector_surface.fill((0,0,0,0))

        elapsed = self.vc_index - 60
        num_lines = min(elapsed // 30 + 1, 5)
        if self.vc_index > 60:
            self.vector_text = f"v = {self.list_of_vectors[num_lines - 1][0]}i + {-self.list_of_vectors[num_lines - 1][1]}j"
        else:
            self.vector_text = ""

        current_vector_text = bigger_font.render(self.vector_text,True,(0,0,0),(255,255,255))
        label_y = self.axis.y - self.axis.size - 10
        if label_y - 5 <= 0:
            label_y = self.axis.y + self.axis.size + 10
        current_vector_text_rect = current_vector_text.get_rect(center=(self.axis.x,label_y))

        if self.vc_index != 0:
            self.axis.draw(screen)
            vector_surface.blit(current_vector_text,current_vector_text_rect)

        if 0 < self.vc_index < 60:
            self.axis.extend()

        if 60 < self.vc_index < 30*5 + 60:
            for i in range(min(num_lines,5)):
                vx,vy = self.list_of_vectors[i]
                scale = self.axis.size // 5
                end_x = self.axis.x + vx * scale
                end_y = self.axis.y + vy * scale
                self.list_of_positions[i][0] += (end_x - self.list_of_positions[i][0])/10
                self.list_of_positions[i][1] += (end_y - self.list_of_positions[i][1])/10
                pygame.draw.line(vector_surface,(200,0,0,255),
                                 (self.axis.x,self.axis.y),
                                 tuple(self.list_of_positions[i]),3)

        if self.vc_index > 30*5 + 60:
            self.axis.retract()



        player_hitbox = pygame.mask.from_surface(player_surface)
        vector_hitbox = pygame.mask.from_threshold(vector_surface,(200,0,0,255),(1,1,1,1))
        if player_hitbox.overlap(vector_hitbox,(0,0)):
            if not player_in_dash and not player_in_iframe:
                player_hp -= 15
                if current_phase != -1 and isinstance(current_phase,int):
                    damage_sfx.play()
                player_iframe_duration = 180
                player_in_iframe = True

        if self.vc_index > 30*5 + 60*2:
            self.done = True

        self.vc_index += 1

        return player_hp,player_in_iframe,player_iframe_duration #this will make it so that we can update the different things better