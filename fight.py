import sys, pygame
import random
import os
import math
from bullet import Bullet
from number_attack import Number
os.environ['SDL_AUDIODRIVER'] = 'dsp'

pygame.init()
size = width, height = 500,500

al = "qwertyuiopasdfghjklzxcvbnm"

angle = 0
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Desmos Bossfight!")
pygame.font.init()
font = pygame.font.Font(pygame.font.get_default_font(), 12)
bigger_font = pygame.font.Font(pygame.font.get_default_font(),18)
super_font = pygame.font.Font(pygame.font.get_default_font(),24)
hyper_font = pygame.font.Font("times.ttf", 75)
player_pos = [250,250]
player_rad = 20
player_hp = 100
player_hp_text = bigger_font.render(f"Your HP: {player_hp}",False,(255,255,255),(0,0,0))
player_hp_text_rect = player_hp_text.get_rect(bottomleft = (0,height))
player_col = (240, 216, 144)

boss_image = pygame.image.load("desmoslogo.png").convert_alpha()
boss_image = pygame.transform.scale(boss_image , (75,75))
pygame.display.set_icon(boss_image)
boss_pos = [250,125]
boss_hitbox = boss_image.get_rect(center = tuple(boss_pos))
boss_hp = 2500
boss_hp_text = font.render(f"HP: {boss_hp}",False,(0,0,0),(255,255,255))
boss_hp_text_rect = boss_hp_text.get_rect(center = (boss_pos[0],boss_pos[1] - 10-75/2))

clock = pygame.time.Clock()

gun_w, gun_h = 4,20
all_bullets = []

dash_cooldown = 0        
dash_duration = 0          
DASH_TOTAL_FRAMES = 3
DASH_POWER = 150
dash_dx = 0
dash_dy = 0
dash_cooldown_dx = 0
dash_cooldown_dx_target = 0
dash_cooldown_text = bigger_font.render(f"Dash (Q): {dash_cooldown//60}",True,(255,255,255),(0,0,0))
dash_cooldown_text_rect = dash_cooldown_text.get_rect(bottomright=(width,height + dash_cooldown_dx))
player_direction = 0
#the player should nt be able to take damage while dashing, so this condition will help
player_in_dash = False


list_of_function = ["5sin(5x)","1/sin(2x)","1/tan(1.2x)","(abs(x)/x)tan(x)^2","-2xtan(2x)","1/x","2sin(2x)","sin(1/(0.01x))/(0.05x)","(abs(cos(x))/cos(x))tan(2x)^2","xsin(x)","xcos(x^2)","2x^3 - 0.5x^2 + x - 2","x/cos(abs(x)^abs(x)) + x","e^-x^2","2xcos(e^abs(2x-2))/cos(x-1)","4xsin(xe^x)"]
random.shuffle(list_of_function)
function = ""
graph_surface = pygame.Surface(size, pygame.SRCALPHA)
graph_surface.fill((0, 0, 0, 0))



def evalfunc(func_str, x_value):
    #creates a dictionary with EVERY math function(except for most of the logs i thing) 
    allowed_names = {k: v for k, v in math.__dict__.items()}
    #assigns x to the current value
    allowed_names["x"] = x_value
    allowed_names["max"] = max
    allowed_names["abs"] = abs
    #evaluates everything(with every function)
    return eval(func_str, allowed_names)



def axis(x,y):
    pygame.draw.line(screen,(0,0,0),(0,y),(width,y),5)
    pygame.draw.line(screen,(0,0,0),(x,y - height//2),(x,y + height//2),5)



currently_graphing = False
graph_index = 0
def graph(func):
    global currently_graphing
    global graph_index
    if currently_graphing: 
        if graph_index == 0:
            graph_surface.fill((0, 0, 0, 0))
        func = func.replace("^","**").replace("ln","log")
        for i in range(len(func)):
            try:
                if func[i] in "0123456789x)" and (func[i+1].lower() in al or func[i+1] in "("):
                    func = func[:i] + func[i] + "*" + func[i+1:]
            except:
                pass
        y_scale = 25
        x_scale = 25
        origin = [width//2,height//2]


        try:
            Xo = (graph_index - origin[0])/x_scale
            Xn = ((graph_index+1) - origin[0])/x_scale
            Yo = (-evalfunc(func,Xo)*y_scale + origin[1])
            Yn = -evalfunc(func,Xn)*y_scale + origin[1]

            if abs(Yn - Yo) < 900:
                pygame.draw.line(graph_surface,(150,0,0),(graph_index,Yo),(graph_index+1,Yn),2)
        except:
            pass
        graph_index += 1
        if currently_graphing and graph_index > width:
            currently_graphing = False
            graph_index = 0



def generate_random_number_attacks(amount,list):
    for i in range(amount):
        edge = random.randint(0, 3)
        if edge == 0: 
            temp_x, temp_y = random.randint(0, width), 0
        elif edge == 1: 
            temp_x, temp_y = random.randint(0, width), height
        elif edge == 2: 
            temp_x, temp_y = 0, random.randint(0, height)
        else:           
            temp_x, temp_y = width, random.randint(0, height)
        temporary_angle_deg = math.degrees(math.atan2(player_pos[1] - temp_y, player_pos[0] - temp_x))
        temporary_value = random.randint(1,6)
        temporary_speed = 4
        list.append(Number(temporary_value,temporary_angle_deg,temp_x,temp_y,temporary_speed))



def draw_player(x,y,color):
    pygame.draw.circle(screen,color,(x,y),player_rad)
    pygame.draw.circle(screen,(0,0,0),(x,y),player_rad,3)



def draw_hands(x,y,angle,color):
    pygame.draw.circle(screen,color,(int(23*math.cos(angle) + x), int(23*math.sin(angle) + y)) , 5)
    pygame.draw.circle(screen,(0,0,0),(int(23*math.cos(angle) + x), int(23*math.sin(angle) + y)) , 5,2)
    pygame.draw.circle(screen,color,(int(23*math.cos(angle+math.pi) + x), int(23*math.sin(angle+math.pi) + y)) , 5)
    pygame.draw.circle(screen,(0,0,0),(int(23*math.cos(angle+math.pi) + x), int(23*math.sin(angle+math.pi) + y)) , 5,2)
def draw_gun(x,y,angle):
    gun_surf = pygame.Surface((gun_w, gun_h), pygame.SRCALPHA)
    gun_surf.fill((40, 40, 40)) 
    rotation_deg = -math.degrees(angle)
    rotated_gun = pygame.transform.rotate(gun_surf, rotation_deg)
    offset_vec = pygame.math.Vector2(0, 0)
    offset_vec.from_polar((gun_h / 2, math.degrees(angle - math.pi/2)))
    gun_center = (int(23* math.cos(angle) + x) + offset_vec.x, int(23* math.sin(angle) + y) + offset_vec.y)
    gun_rect = rotated_gun.get_rect(center=gun_center)
    screen.blit(rotated_gun, gun_rect)











def circle_rect_collide(circle_position, circle_radius, rect):
    cx,cy = circle_position
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top,  min(cy, rect.bottom))
    #math.hypot uses pythagorean theorem to find the radius
    return math.hypot(cx - closest_x, cy - closest_y) < circle_radius
number_attack_list_storage = []
number_attack_list = []
timer_number_attacks = 0
generate_random_number_attacks(30,number_attack_list_storage)
attack_1_start = True











def attack1(amount):
    global timer_number_attacks
    global attack_1_start
    if attack_1_start:
        timer_number_attacks += 1
        if timer_number_attacks % 30 == 0:
                generate_random_number_attacks(1,number_attack_list)
        if timer_number_attacks == amount*30:
            attack_1_start = False
            timer_number_attacks = 0









current_attack = 1
chosen_functions = random.sample(list_of_function,5)
attack2_start = False
axis_animation_tick = 0
target_y = -height//2 - 10
target_x = 0
now_graphing_text = bigger_font.render(f"Currently Graphing: " , True,(255,255,255),(0,0,0))
now_graphing_text_rect = now_graphing_text.get_rect(topright=(target_x,45))
current_graph_text = super_font.render(f"{function}",True,(255,255,255),(0,0,0))
current_graph_text_rect = current_graph_text.get_rect(topleft=now_graphing_text_rect.bottomleft)

in_cutscene = False
current_phase = 0.5










cutscene_frame = 0
def init_cutscene():
    global cutscene_frame
    global current_phase
    global dialouge1
    dialouge1 = bigger_font.render(f"",True,(0,0,0))
    dialouge1_rect = dialouge1.get_rect(topleft = boss_hitbox.topright)
    if max(0,min(cutscene_frame,30)) == cutscene_frame:
        dialouge1 = bigger_font.render(f"",True,(0,0,0))
        dialouge1_rect = dialouge1.get_rect(topleft = boss_hitbox.topright)
    elif max(30,min(cutscene_frame,90)) == cutscene_frame:
        dialouge1 = bigger_font.render(f"<(yo bro)",True,(0,0,0))
        dialouge1_rect = dialouge1.get_rect(topleft = boss_hitbox.topright) 
    elif max(90,min(cutscene_frame,210)) == cutscene_frame:
        dialouge1 = bigger_font.render(f"<(i heard you were \n using geogebra)",True,(0,0,0))
        dialouge1_rect = dialouge1.get_rect(topleft = boss_hitbox.topright)
    elif max(210,min(cutscene_frame,270)) == cutscene_frame:
        dialouge1 = bigger_font.render(f"<(i swear i wasnt bro)",True,(0,0,0))
        dialouge1_rect = dialouge1.get_rect(topleft = (player_pos[0] + player_rad , player_pos[1] - player_rad))
    elif max(270,min(cutscene_frame,330)) == cutscene_frame:
        dialouge1 = bigger_font.render(f"<(whatever you say bro)",True,(0,0,0))
        dialouge1_rect = dialouge1.get_rect(topleft = boss_hitbox.topright)




    cutscene_frame += 1
    screen.blit(dialouge1,dialouge1_rect)
    if cutscene_frame == 330:
        current_phase = 1







def attack2():
    global currently_graphing
    global graph_index
    global chosen_functions
    global function
    global attack2_start
    global player_hp
    global axis_animation_tick
    global target_y
    global target_x
    axis(width//2,target_y)
    if not currently_graphing and attack2_start:
        if axis_animation_tick < 200:
            axis_animation_tick += 1
            target_y += (height//2 - target_y)/10
            target_x += (200 - target_x)/10
        else:
            try:
                function = chosen_functions.pop()
                currently_graphing = True
            except:
                axis_animation_tick = 0
                attack2_start = False
    elif attack2_start and currently_graphing:
        graph(function)
        graph_hitbox = pygame.mask.from_threshold(graph_surface,(150,0,0),(10,10,10,255))
        player_surface = pygame.Surface((player_rad*2,player_rad*2),pygame.SRCALPHA)
        pygame.draw.circle(player_surface, (240,216,144), (player_rad,player_rad), player_rad)
        circle_mask = pygame.mask.from_surface(player_surface)
        offset = (player_pos[0] - player_rad , player_pos[1] - player_rad)
        if graph_hitbox.overlap(circle_mask,offset):
                player_hp -= 1

death_text_opacity = 0
death_text_frame = 0
def death():
    global current_phase , death_text_opacity , death_text_frame , angle
    current_phase = -1



    screen.fill((0,0,0))    
    death_text = hyper_font.render(f"You Died!" , True , (255,255,255))

    death_text.set_alpha(death_text_opacity)

    draw_player(player_pos[0],player_pos[1],(255,255,255))
    draw_hands(player_pos[0],player_pos[1],angle,(255,255,255))

    if min(60,death_text_frame) == 60:
        pygame.draw.circle(screen,(0,0,0),tuple(player_pos),death_text_frame-60)


    death_text_rect = death_text.get_rect(center = (250,63))
    death_text_frame += 1
    screen.blit(death_text,death_text_rect)



    if min(90,death_text_frame) == 90:
        death_text_opacity += (1 if death_text_opacity < 255 else 0)
    if min(90 + 255 +120 , death_text_frame) == 90 + 255 + 120:
            pygame.quit()
            sys.exit()  



attack3_circle_rad = 450
attack3_circle_rad_target = 450
attack3_frame = 0
def attack3():
    global attack3_circle_rad , attack3_circle_rad_target, attack3_frame , target_x
    attack3_circle_rad_target = 250








running = True

while running:
    clock.tick(60)
    if current_phase >= 0 : screen.fill((255,255,255))
    pygame.draw.circle(screen,(0,0,0),(width//2,height//2),attack3_circle_rad,10)













    if dash_cooldown < 300:
        dash_cooldown += 1
        dash_cooldown_dx_target = 0
    else: dash_cooldown_dx_target = 1






    dash_cooldown_dx += (25*dash_cooldown_dx_target - dash_cooldown_dx)/5




    attack3_circle_rad += (attack3_circle_rad_target - attack3_circle_rad)/15


    if current_attack == 1 and current_phase == 1:
        boss_pos[0] += int((250 - boss_pos[0])/15)
        boss_pos[1] += int((125 - boss_pos[1])/15)

        function = ""
        target_y += ((-height//2 - 10) - target_y)/4
        target_x += (-target_x)/4
        attack1(10)
        if not attack_1_start:
            attack2_start = True
            current_attack = 2

    elif current_attack == 2 and current_phase == 1:
        boss_pos[0] += int((425 - boss_pos[0])/15)
        boss_pos[1] += int((75 - boss_pos[1])/15)
        attack2()
        if not attack2_start:
            attack_1_start = True
            graph_surface.fill((0, 0, 0, 0))
            timer_number_attacks = 0
            chosen_functions = random.sample(list_of_function, 5)
            current_attack = 1









    boss_hitbox = boss_image.get_rect(center = tuple(boss_pos))

    boss_hp_text = bigger_font.render(f"HP: {boss_hp}",False,(0,0,0),(255,255,255))
    boss_hp_text_rect = boss_hp_text.get_rect(center = (boss_pos[0],boss_pos[1] - 10-75/2))

    player_hp_text = bigger_font.render(f"Your HP: {player_hp}",False,(255,255,255),(0,0,0))
    player_hp_text_rect = player_hp_text.get_rect(bottomleft = (0,height))

    dash_cooldown_text = bigger_font.render(f"Dash (Q): {5 - dash_cooldown//60}",True,(255,255,255),(0,0,0))
    dash_cooldown_text_rect = dash_cooldown_text.get_rect(bottomright=(width,height + dash_cooldown_dx))

    now_graphing_text = bigger_font.render(f"Currently Graphing: " , True,(255,255,255),(0,0,0))
    now_graphing_text_rect = now_graphing_text.get_rect(topright=(target_x,45))

    current_graph_text = super_font.render(f"{function}",True,(255,255,255),(0,0,0))
    current_graph_text_rect = current_graph_text.get_rect(topleft=now_graphing_text_rect.bottomleft)   












    mousex,mousey = pygame.mouse.get_pos()
    dx = mousex - player_pos[0]
    dy = mousey - player_pos[1]

    if current_phase >= 1: angle = (math.atan2(dy, dx) + math.pi/2)


    offset_vec = pygame.math.Vector2(0, 0)
    offset_vec.from_polar((gun_h / 2, math.degrees(angle - math.pi/2)))
    bulletx,bullety = (int(23* math.cos(angle) + player_pos[0]) + offset_vec.x, int(23* math.sin(angle) + player_pos[1]) + offset_vec.y)
    axis(width//2,target_y)
    screen.blit(graph_surface, (0, 0))















    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and current_phase >= 1:
            all_bullets.append(Bullet(angle,bulletx,bullety,10,2,10))
        if event.type == pygame.KEYDOWN and current_phase >= 1:
            if event.key == pygame.K_SPACE:
                all_bullets.append(Bullet(angle,bulletx,bullety,10,2,10))
            if event.key == pygame.K_q:
                if dash_cooldown >= 300 and dash_duration <= 0:
                    dash_cooldown = 0
                    dash_duration = DASH_TOTAL_FRAMES
                    dash_dx = math.cos(player_direction)
                    dash_dy = math.sin(player_direction)















    if dash_duration > 0:
        player_in_dash = True
        dash_duration -= 1
        dash_step = DASH_POWER / DASH_TOTAL_FRAMES
        new_x = player_pos[0] + dash_step * dash_dx
        new_y = player_pos[1] + dash_step * dash_dy
        player_pos[0] = max(player_rad, min(width - player_rad, new_x))
        player_pos[1] = max(player_rad, min(height - player_rad, new_y))
    else:
        if current_phase == 1:
            player_in_dash = False
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_w]:
                if player_pos[1] - player_rad > 0:
                    player_pos[1] -= 3
            if pressed[pygame.K_s]:
                if player_pos[1] + player_rad < height:
                    player_pos[1] += 3
            if pressed[pygame.K_a]:
                if player_pos[0] - player_rad > 0:
                    player_pos[0] -= 3
            if pressed[pygame.K_d]:
                if player_pos[0] + player_rad < width:
                    player_pos[0] += 3
            #apperantly pressed[pygame.K_a] returns 1 0 or -1
            movement_dx = pressed[pygame.K_d] - pressed[pygame.K_a]
            movement_dy = pressed[pygame.K_s] - pressed[pygame.K_w]
            player_direction = math.radians(270) if (movement_dx == 0 and movement_dy == 0) else math.atan2(movement_dy,movement_dx)
            














    for item in all_bullets:
        item.draw(screen)
        if item.move(0,0,width,height):
            all_bullets.remove(item)
        if item.bullet_rect.colliderect(boss_hitbox):
            boss_hp -= 10
            all_bullets.remove(item)













    screen.blit(boss_image,boss_hitbox)
    screen.blit(boss_hp_text,boss_hp_text_rect)
    screen.blit(player_hp_text,player_hp_text_rect)
    screen.blit(dash_cooldown_text,dash_cooldown_text_rect)
    screen.blit(now_graphing_text,now_graphing_text_rect)
    screen.blit(current_graph_text,current_graph_text_rect)











    draw_player(player_pos[0],player_pos[1],player_col)
    draw_hands(player_pos[0],player_pos[1],angle,player_col)
    draw_gun(player_pos[0],player_pos[1],angle)










    for item in number_attack_list:
        item.move()
        item.draw(screen)
        if circle_rect_collide(tuple(player_pos),player_rad,item.hitbox):
            if not player_in_dash:
                number_attack_list.remove(item)
                player_hp -= item.value












    if current_phase == 0.5:
        init_cutscene()
    if player_hp <= 0:
        death()









    pygame.display.flip()











pygame.quit()
sys.exit()