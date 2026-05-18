import sys, pygame
import random
import os
import math
from bullet import Bullet
from number_attack import Number
from attack_damage_number import Value
from summon_axis import Axis
#os.environ['SDL_AUDIODRIVER'] = 'dsp'

pygame.init()
size = width, height = 500,500

pygame.mixer.init()
PHASE_1_MUSIC = "animation_warrior_theme.mp3"
PHASE_2_MUSIC = "il-vento-d'oro.mp3"
phase_music = PHASE_1_MUSIC
pygame.mixer.music.load(phase_music)
music_started = False

death_sfx = pygame.mixer.Sound("death_sfx.mp3")
damage_sfx = pygame.mixer.Sound("damage_sfx.mp3")
boss_hit_sfx = pygame.mixer.Sound("boss_hit_sfx.mp3")
ping_sfx = pygame.mixer.Sound("ding.mp3")

al = "qwertyuiopasdfghjklzxcvbnm"


player_in_iframe = False
player_iframe_duration = 0
angle = 0
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Desmos Bossfight!")
pygame.font.init()
font = pygame.font.Font(pygame.font.get_default_font(), 12)
bigger_font = pygame.font.Font(pygame.font.get_default_font(),18)
super_font = pygame.font.Font(pygame.font.get_default_font(),24)
integral_font = pygame.font.Font("times.ttf", 48)
hyper_font = pygame.font.Font("times.ttf", 75)
player_pos = [250,250]
player_rad = 20
player_hp = 1000 #change to 100 later
player_hp_text = bigger_font.render(f"Your HP: {player_hp}",False,(255,255,255),(0,0,0))
player_hp_text_rect = player_hp_text.get_rect(bottomleft = (0,height))
player_col = (240, 216, 144) 
random_damage_value = 0
random_damage_value_xpos = 0
random_damage_value_ypos = 0
all_damage_texts = []

boss_pos = [250,125]
boss_image = pygame.image.load("desmoslogo.png").convert_alpha()
boss_image = pygame.transform.scale(boss_image , (75,75))
boss_impact_frame = pygame.image.load("desmos_impact_frame.png").convert_alpha()
boss_impact_frame = pygame.transform.scale(boss_impact_frame , (75,75))
boss_impact_frame_rect = boss_impact_frame.get_rect(center=boss_pos)
pygame.display.set_icon(boss_image)
boss_hitbox = boss_image.get_rect(center = tuple(boss_pos))
boss_hp = 65
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


list_of_function = ["5sin(5x)","1/sin(2x)","1/tan(1.2x)","(abs(x)/x)tan(x)^2","-2xtan(2x)","1/x","2sin(2x)","sin(1/(0.02x))/(0.05x)","(abs(cos(x))/cos(x))tan(2x)^2","xsin(x)","xcos(x^2)","x^3 - 4x^2 + x - 2","x/cos(abs(x)^abs(x)) + x","e^-x^2","2xcos(e^abs(2x-2))/cos(x-1)","4xsin(xe^x)"]
random.shuffle(list_of_function)
function = ""
graph_surface = pygame.Surface(size, pygame.SRCALPHA)
graph_surface.fill((0,0,0,0))
polar_surface = pygame.Surface(size, pygame.SRCALPHA)
polar_surface.fill((0,0,0,0))



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
def graph(func,end_after_done,origin):
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

        print(graph_index)

        try:
            Xo = (graph_index - origin[0])/x_scale
            Xn = ((graph_index+1) - origin[0])/x_scale
            Yo = (-evalfunc(func,Xo)*y_scale + origin[1])
            Yn = -evalfunc(func,Xn)*y_scale + origin[1]

            if abs(Yn - Yo) < 900:
                pygame.draw.line(graph_surface,(150,0,0),(graph_index,Yo),(graph_index+1,Yn),2)
        except Exception as e: 
                print(e)
        graph_index += (1 if graph_index <= width else 0)
        if currently_graphing and graph_index > width and end_after_done:
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

player_surface = pygame.Surface(size, pygame.SRCALPHA)

def draw_player(x,y,color):
    pygame.draw.circle(player_surface,color,(x,y),player_rad)
    pygame.draw.circle(player_surface,(0,0,0),(x,y),player_rad,3)
def draw_hands(x,y,angle,color):
    pygame.draw.circle(player_surface,color,(int(23*math.cos(angle) + x), int(23*math.sin(angle) + y)) , 5)
    pygame.draw.circle(player_surface,(0,0,0),(int(23*math.cos(angle) + x), int(23*math.sin(angle) + y)) , 5,2)
    pygame.draw.circle(player_surface,color,(int(23*math.cos(angle+math.pi) + x), int(23*math.sin(angle+math.pi) + y)) , 5)
    pygame.draw.circle(player_surface,(0,0,0),(int(23*math.cos(angle+math.pi) + x), int(23*math.sin(angle+math.pi) + y)) , 5,2)
def draw_gun(x,y,angle):
    gun_surf = pygame.Surface((gun_w, gun_h), pygame.SRCALPHA)
    gun_surf.fill((40, 40, 40)) 
    rotation_deg = -math.degrees(angle)
    rotated_gun = pygame.transform.rotate(gun_surf, rotation_deg)
    offset_vec = pygame.math.Vector2(0, 0)
    offset_vec.from_polar((gun_h / 2, math.degrees(angle - math.pi/2)))
    gun_center = (int(23* math.cos(angle) + x) + offset_vec.x, int(23* math.sin(angle) + y) + offset_vec.y)
    gun_rect = rotated_gun.get_rect(center=gun_center)
    player_surface.blit(rotated_gun, gun_rect)


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
    global phase_1_music
    global music_started
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
        if not music_started:
            pygame.mixer.music.play(loops=-1)
            music_started = True
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
    global player_col
    global current_phase
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
        graph(function,True,[width//2,height//2])
        graph_hitbox = pygame.mask.from_threshold(graph_surface,(150,0,0),(10,10,10,255))
        circle_mask = pygame.mask.from_threshold(player_surface,player_col,(10,10,10,255))
        offset = (0,0)
        if graph_hitbox.overlap(circle_mask,offset):
                if current_phase != -1: damage_sfx.play()
                player_hp -= 1


death_text_opacity = 0
death_text_frame = 0
def death():
    global current_phase , death_text_opacity , death_text_frame , angle , death_sfx
    pygame.mixer.music.stop()
    current_phase = -1



    screen.fill((0,0,0))
    player_surface.fill((0,0,0,0))    
    death_text = hyper_font.render(f"You Died!" , True , (255,255,255))

    death_text.set_alpha(death_text_opacity)

    draw_player(player_pos[0],player_pos[1],(255,255,255))
    draw_hands(player_pos[0],player_pos[1],angle,(255,255,255))
    screen.blit(player_surface,(0,0))

    if min(60,death_text_frame) == 60:

        if death_text_frame == 60:
            death_sfx.play()
        pygame.draw.circle(screen,(0,0,0),tuple(player_pos),death_text_frame/2-60)


    death_text_rect = death_text.get_rect(center = (250,63))
    death_text_frame += 1
    screen.blit(death_text,death_text_rect)



    if min(90,death_text_frame) == 90:
        death_text_opacity += (1 if death_text_opacity < 255 else 0)
    if min(90 + 255 +120 , death_text_frame) == 90 + 255 + 120:
            pygame.quit()
            sys.exit()  





polar_index = 0
currently_polaring = False
current_angle = 0
current_radius = 0
def draw_line(r,angle,start_delay,end_delay):
    global polar_index,currently_polaring,width,height,current_angle,current_radius
    polar_surface.fill((0, 0, 0, 0))
    POLAR_SPEED = 0.05
    POLAR_DURATION = max(1, int(abs(angle) / POLAR_SPEED))
    EXTRA_ANIMATION_TIME = 45
    if currently_polaring:
        
        if polar_index == 0: current_radius = 0

        total_time = start_delay + POLAR_DURATION + end_delay + EXTRA_ANIMATION_TIME
        if polar_index < start_delay:
            current_radius += (r - current_radius)/20
            current_angle = 0

        if start_delay <= polar_index and polar_index < (start_delay + POLAR_DURATION):
            current_angle = ((polar_index - start_delay))*angle/POLAR_DURATION


        elif polar_index >= POLAR_DURATION + start_delay:
            current_angle = angle

        if polar_index > total_time - EXTRA_ANIMATION_TIME and polar_index < total_time:
            current_radius += (-current_radius)/12
        

        real_part = (current_radius-5)*math.cos(current_angle) + width//2 
        imaginary_part = (current_radius-5)*math.sin(current_angle) + height//2 
        if current_radius > 4 : pygame.draw.line(polar_surface,(170,0,0),(width//2,height//2),(real_part,imaginary_part),5)

        if min(polar_index,total_time) >= total_time:
            polar_index = 0
            currently_polaring = False

        polar_index += 1


attack3_start = True
attack3_circle_rad = math.sqrt(250**2 + 250**2) + 10
attack3_circle_rad_target = math.sqrt(250**2 + 250**2) + 10
attack3_frame = 0
random_angles_generation = [(math.radians(random.randint(-360,-60)) if random.randint(0,1) == 0 else math.radians(random.randint(60,360))) for i in range(5)]
polar_graph_index = 0
temp_angle = 0
progress = 500
def attack3():
    global attack3_circle_rad , attack3_circle_rad_target, attack3_frame , target_x,currently_polaring,random_angles_generation , polar_graph_index , attack3_start , temp_angle , player_in_iframe , player_hp , player_iframe_duration , width, height, progress
    global current_phase
    if attack3_start and not currently_polaring:
        attack3_frame += 1
        if attack3_frame < 180:
           pass
        else:
            try:
                temp_angle = random_angles_generation.pop()
                currently_polaring = True
            except:
                attack3_frame = 0
                attack3_start = False
    elif attack3_start and currently_polaring:
        draw_line(attack3_circle_rad , temp_angle , 90 ,  60)
        line_hitbox = pygame.mask.from_threshold(polar_surface,(170,0,0),(10,10,10,255))
        player_mask = pygame.mask.from_surface(player_surface)
        offset = (0,0)
        if line_hitbox.overlap(player_mask,offset):
            if not player_in_dash:
                if not player_in_iframe:
                    player_hp -= 15
                    if current_phase != -1 and isinstance(current_phase,int): damage_sfx.play()
                    player_iframe_duration = 180
                player_in_iframe = True

def reset_phase1():
    global attack_1_start,attack2_start,attack3_start,attack3_circle_rad_target,target_y,number_attack_list
    attack3_start = False
    attack2_start = False
    attack_1_start = False
    graph_surface.fill((0,0,0,0))
    polar_surface.fill((0,0,0,0))
    number_attack_list = []
    attack3_circle_rad_target = math.sqrt(250**2 + 250**2) + 10
    target_y += ((-height//2 - 10) - target_y)/4

last_value_attack = ""
last_attack = ""
boss_impact_frame_opacity = 255 
surface_opacity_p2 = 255
cutscene_frame_phase2 = 0
boss_hp_text_alpha = 0
shield_surface = pygame.Surface(size,pygame.SRCALPHA)
shield_target_size = math.dist(tuple(boss_pos),boss_hitbox.topleft) + 10
SHIELD_INIT = math.dist(tuple(boss_pos),tuple((a + b) / 2 for a, b in zip(boss_hitbox.topleft, boss_hitbox.bottomleft)))
shield_current_size = SHIELD_INIT
shield_hp = 5000
def cutscene_phase2():
    global cutscene_frame , in_cutscene
    global current_phase
    global dialouge1 , dialouge1_rect
    global phase_music
    global music_started
    global boss_hp
    global all_damage_texts
    global all_bullets
    global last_value_attack
    global boss_pos , player_pos
    global PHASE_2_MUSIC
    global boss_impact_frame_rect
    global boss_impact_frame
    global last_attack
    global boss_hit_sfx
    global boss_impact_frame_opacity
    global size
    global surface_opacity_p2
    global cutscene_frame_phase2
    global boss_hp_text_alpha
    global angle
    global dialouge1
    global shield_target_size
    global shield_current_size
    global ping_sfx
    global current_attack , attack_4_start

    if cutscene_frame_phase2 == 0:
        dialouge1 = bigger_font.render(f"",True,(0,0,0))
        dialouge1_rect = dialouge1.get_rect(topleft = boss_hitbox.topright)

    new_surface = pygame.Surface(size,pygame.SRCALPHA)

    boss_hp_text = bigger_font.render(f"HP: ε",True,(255,255,255))
    boss_hp_text.set_alpha(boss_hp_text_alpha)
    boss_hp_text_rect = boss_hp_text.get_rect(center = (boss_pos[0],boss_pos[1] - 10-75/2))

    try:
        last_value_attack = all_damage_texts[-1].value
        last_attack = Value(last_value_attack + boss_hp,boss_pos[0],boss_pos[0],boss_pos[1],boss_pos[1] + 40,48,80,180,(200,0,0))
        boss_hit_sfx.play()
        pygame.mixer.music.stop()
        phase_music = PHASE_2_MUSIC
    except:
        pass

    reset_phase1()

    current_phase = 1.5
    reset_phase1()
    all_damage_texts.clear()
    all_bullets.clear()
    new_surface.fill((0,0,0,surface_opacity_p2))
    screen.blit(new_surface,(0,0))



    screen.blit(boss_impact_frame,boss_impact_frame_rect)
    screen.blit(boss_hp_text,boss_hp_text_rect)
    boss_impact_frame.set_alpha(boss_impact_frame_opacity)
    boss_hp_text.set_alpha(boss_hp_text_alpha)

    try:
        last_attack.draw(screen)
        if last_attack.move():
            del last_attack
    except:
        cutscene_frame_phase2 += 1


    if cutscene_frame_phase2 > 0 and 255 > cutscene_frame_phase2:
        boss_impact_frame_opacity -= 1
    if cutscene_frame_phase2 == 265:
            pygame.mixer.music.load(phase_music)
            pygame.mixer.music.play(-1)
    if cutscene_frame_phase2 >= 255 + 40 and cutscene_frame_phase2 < 255 + 40 + 120:
        player_pos = [250,250]
        boss_pos = [250,125]
        angle = 0
        boss_impact_frame_opacity = 255
        boss_hp_text_alpha = 255

    if cutscene_frame_phase2 >= 255 + 40 + 120 and  surface_opacity_p2 > 0 and boss_hp_text_alpha > 0 and boss_impact_frame_opacity > 0:
        screen.blit(boss_hp_text,boss_hp_text_rect)
        if surface_opacity_p2 > 0:
            surface_opacity_p2 -= 5 
        if boss_hp_text_alpha > 0:
            boss_hp_text_alpha -= 5
        if boss_impact_frame_opacity > 0:
            boss_impact_frame_opacity -= 5

    if surface_opacity_p2 == 0 and boss_hp_text_alpha == 0 and boss_impact_frame_opacity == 0:
        screen.blit(dialouge1,dialouge1_rect)
        if cutscene_frame_phase2 >= 255 + 40 + 120 + 40 + 255//5 and cutscene_frame_phase2 < 255 + 255//5 + 40 + 120 + 40+ 60:
            dialouge1 = bigger_font.render(f"<(bro what)",True,(0,0,0))
            dialouge1_rect = dialouge1.get_rect(topleft = (player_pos[0] + player_rad , player_pos[1] - player_rad))
        if cutscene_frame_phase2 >= 255 + 40 + 255//5+ 120 + 40 + 60 and cutscene_frame_phase2 < 255 + 40+ 255//5 + 120 + 40+ 180:
            dialouge1 = bigger_font.render(f"<(how are you\neven alive)",True,(0,0,0))
            dialouge1_rect = dialouge1.get_rect(topleft = (player_pos[0] + player_rad , player_pos[1] - player_rad))
        if cutscene_frame_phase2 >= 255 + 40+ 255//5 + 120 + 40 + 180 and cutscene_frame_phase2 < 255 + 40+ 255//5 + 120 + 40+ 300:
            dialouge1 = bigger_font.render(f"<(im locked)",True,(0,0,0))
            dialouge1_rect = dialouge1.get_rect(topleft = boss_hitbox.topright)
        if cutscene_frame_phase2 >= 255 + 40+ 255//5 + 120 + 40 + 300 and cutscene_frame_phase2 < 255 + 40+ 255//5 + 120 + 40+ 420:
            if cutscene_frame_phase2 == 255 + 40+ 255//5 + 120 + 40 + 300:
                ping_sfx.play()
            dialouge1 = bigger_font.render(f"",True,(0,0,0))
            dialouge1_rect = dialouge1.get_rect(topleft = boss_hitbox.topright)
            shield_current_size += (shield_target_size - shield_current_size)/20
        if cutscene_frame_phase2 >= 255 + 40+ 255//5 + 120 + 40+ 420 + 175:
            in_cutscene = False
            current_phase = 2
            current_attack = 4
            attack_4_start = True
            boss_hp = 1




def generate_random_axis(minx,maxx,miny,maxy):
    axisx = random.randint(minx,maxx)
    axisy = random.randint(miny,maxy)
    size = 200
    return Axis(axisx,axisy,size,5,5)

vc_index = 0
current_vector = 0
axis_test = Axis(250,250,100,20,5)
list_of_vectors = [[0,0],[0,0],[0,0],[0,0],[0,0]]
list_of_positions = [[0,0],[0,0],[0,0],[0,0],[0,0]]
vector_surface = pygame.Surface(size,pygame.SRCALPHA)
vector_text = ""
def vector_attack():
    global vc_index
    global axis_test
    global width,height
    global list_of_vectors , list_of_positions
    global vector_surface , player_surface
    global current_vector
    global bigger_font
    global vector_text
    global player_in_iframe , player_in_dash , player_iframe_duration , player_hp , player_pos
    vector_surface.fill((0,0,0,0))
    current_vector_text = bigger_font.render(vector_text,True,(0,0,0),(255,255,255))
    current_vector_text_rect = current_vector_text.get_rect(center = (axis_test.x,(axis_test.y - axis_test.size - 10) if (axis_test.y - axis_test.size - 10 - 5) > 0 else (axis_test.y + axis_test.size + 10)))
    elapsed = vc_index - 60
    num_lines = elapsed // 60 + 1
    if num_lines < 5:
        vector_text = f"v = {list_of_vectors[num_lines][0]}i + {-list_of_vectors[num_lines][1]}j"
    else:
        vector_text = ""
    if vc_index == 0:
        axis_test = Axis(player_pos[0],player_pos[1],200,10,5)
        for i in range(5):
            list_of_vectors[i] = [random.randint(-5,5),random.randint(-5,5)]
            list_of_positions[i] = [axis_test.x,axis_test.y]

    if vc_index != 0:
        axis_test.draw(screen)
        vector_surface.blit(current_vector_text,current_vector_text_rect)

    if vc_index < 60 and vc_index != 0:
        axis_test.extend()
    if vc_index > 60 and vc_index < 60*6:
        
        for i in range(min(num_lines, 5)):
            vx, vy = list_of_vectors[i]
            scale = axis_test.size//5
            end_x = axis_test.x + vx * scale
            end_y = axis_test.y + vy * scale
            list_of_positions[i][0] += (end_x - list_of_positions[i][0])/30
            list_of_positions[i][1] += (end_y - list_of_positions[i][1])/30
            pygame.draw.line(vector_surface, (200, 0, 0,255),
                             (axis_test.x, axis_test.y),
                             tuple(list_of_positions[i]), 3)
    if vc_index > 60*6:
        axis_test.retract()

    player_hitbox = pygame.mask.from_surface(player_surface)
    vector_hitbox = pygame.mask.from_threshold(vector_surface,(200,0,0,255),(1,1,1,1))
    if player_hitbox.overlap(vector_hitbox,(0,0)):
            if not player_in_dash:
                if not player_in_iframe:
                    player_hp -= 15
                    if current_phase != -1 and isinstance(current_phase,int): damage_sfx.play()
                    player_iframe_duration = 180
                player_in_iframe = True
    
    vc_index += 1


attack_4_index = 0
attack_4_start = False
def attack4():
    global attack_4_index
    global attack_4_start
    global vc_index
    if attack_4_index < 5 and attack_4_start:
        vector_attack()
        if vc_index > 60*7:
            vc_index = -1
            attack_4_index += 1
    else:
        attack_4_start = False
        attack_4_index = 0


def shade_integral(surface, func, minx, maxx, origin):
    func = func.replace("^","**").replace("ln","log")
    for i in range(len(func)):
            try:
                if func[i] in "0123456789x)" and (func[i+1].lower() in al or func[i+1] in "("):
                    func = func[:i] + func[i] + "*" + func[i+1:]
            except:
                pass
    points = []
    x_scale, y_scale = 25,25

    x = minx
    while x <= maxx:
        try:
            screen_x = origin[0] + x * x_scale
            screen_y = origin[1] - evalfunc(func, x) * y_scale
            points.append((screen_x, screen_y))
        except:
            pass
        x += 0.05

    if len(points) < 2: #checks if a polygon can actually be made
        return

    baseline_y = origin[1]  # y position of x-axis on screen
    points.append((points[-1][0], baseline_y))  # bottom-right
    points.append((points[0][0],  baseline_y))  # bottom-left

    pygame.draw.polygon(surface, (175,0,0), points)


attack5_start = False
attack5_index = 0
attack5_axis = None
animation_max_y = -player_pos[1]+50
list_of_new_functions = ["sin(x) + 8","17 - (x/3)^2","xsin(x) + 9","sqrt(100-x^2)","5erf(x)+6"]
new_chosen_functions = random.sample(list_of_new_functions,3)
new_function = ""
attack5_attack_tick = 0
attack5_a = 0
attack5_b = 0
attack5_attack_wave = 0
attack5_closing_tick = 0
integral_surface = pygame.Surface(size,pygame.SRCALPHA)
def attack5():
    integral_surface.fill((0,0,0,0))
    global attack5_start , attack5_index , attack5_axis
    global player_pos , animation_max_y , player_hp
    global width,height
    global ping_sfx , bigger_font , warning_text_alpha , font
    global currently_graphing , new_chosen_functions , new_function , graph_index
    global attack5_attack_tick,attack5_a,attack5_b , attack5_attack_wave
    global attack5_closing_tick
    global super_font , integral_font , font , bigger_font
    warning_text = bigger_font.render("Your movement is limited\nto the x-axis!",True,(0,0,0))
    warning_text_rect = warning_text.get_rect(topleft = (0,0))
    if attack5_start:
        if attack5_index == 0:
            attack5_axis = Axis(width//2,height//2,250,5,5)
            ping_sfx.play()
            attack5_closing_tick = 0
            attack5_a = 0
            attack5_b = 0
            new_function = ""
            warning_text_alpha = 255
            attack5_axis.y = player_pos[1]
        if attack5_index < 240:
            if attack5_index < 90:
                attack5_axis.extend()
            elif attack5_index >= 90:
                if warning_text_alpha > 0: warning_text_alpha -= 5
                attack5_axis.y = animation_max_y * abs((0.65)**((attack5_index - 90)/10)*math.cos((attack5_index - 90)/10)) + 450
                player_pos[1] = attack5_axis.y
        elif attack5_index >= 240:
            if not currently_graphing:
                try:
                    new_function = new_chosen_functions.pop()
                    currently_graphing = True
                except:
                    if attack5_closing_tick == 0:
                        graph_surface.fill((0,0,0,0))
                        integral_surface.fill((0,0,0,0))
                    if attack5_closing_tick < 35:
                        attack5_axis.retract()
                    else:
                        attack5_start = False
                    attack5_closing_tick += 1
            else:
                graph(new_function,False,[250,450])
                if graph_index > width:
                    if attack5_attack_wave < 3:
                        if attack5_attack_tick == 0:
                            ping_sfx.play()
                            attack5_a , attack5_b = random.randint(-10,10),random.randint(-10,10)
                            while abs(attack5_b - attack5_a) < 4 or abs(attack5_a - attack5_b) > 10:
                                attack5_b = random.randint(-10,10)
                        if attack5_attack_tick < 60:
                            integral_sign_text = integral_font.render("\u222B",True,(0,0,0),(255,255,255))
                            integral_sign_text_rect = integral_sign_text.get_rect(topleft = (25,25))
                            upper_bound_text = bigger_font.render(f"{max(attack5_a,attack5_b)}",True,(0,0,0),(255,255,255))
                            upper_bound_text_rect = upper_bound_text.get_rect(topleft=integral_sign_text_rect.topright)
                            lower_bound_text = bigger_font.render(f"{min(attack5_a,attack5_b)}",True,(0,0,0),(255,255,255))
                            lower_bound_text_rect = lower_bound_text.get_rect(bottomleft=integral_sign_text_rect.bottomright)
                            function_text = super_font.render("f(x)dx",True,(0,0,0))
                            function_text_rect = function_text.get_rect(topleft = upper_bound_text_rect.bottomright)
                            screen.blit(integral_sign_text,integral_sign_text_rect)
                            screen.blit(upper_bound_text,upper_bound_text_rect)
                            screen.blit(lower_bound_text,lower_bound_text_rect)
                            screen.blit(function_text,function_text_rect)
                        elif attack5_attack_tick >= 60 and attack5_attack_tick < 120:
                            shade_integral(integral_surface,new_function,min(attack5_a,attack5_b) , max(attack5_a, attack5_b) , [250,450])
                        else:
                            attack5_attack_tick = -1
                            attack5_attack_wave += 1
                        
                        
                        attack5_attack_tick += 1
                    else:
                        currently_graphing = False
                        graph_index = 0
                        attack5_attack_tick = 0
                        attack5_attack_wave = 0


        warning_text.set_alpha(warning_text_alpha)
        screen.blit(warning_text,warning_text_rect)
        if attack5_index >= 10 and attack5_closing_tick <= 0:
            for i in range(width//25):
                pygame.draw.line(screen,(0,0,0),(25 * i , attack5_axis.y + 5),(25 * i , attack5_axis.y - 5),2)
                screen.blit(font.render(f"{i - 10}" , True , (0,0,0)),font.render(f"{i - 10}" , True , (0,0,0)).get_rect(topleft=(25 * i , attack5_axis.y + 5)))
            for i in range(height//25):
                pygame.draw.line(screen,(0,0,0),(245,height - 25*i),(255, height - 25*i),2)
                screen.blit(font.render(f"{i - int(height//25 - attack5_axis.y//25 - (1 if attack5_index > 90 else 0))}" , True , (0,0,0)),font.render(f"{i - int(height//25 - attack5_axis.y//25)}" , True , (0,0,0)).get_rect(topleft=(255, height - 25*i)))
        attack5_axis.draw(screen)

        integral_hitbox = pygame.mask.from_threshold(integral_surface,(175,0,0),(10,10,10,255))
        circle_mask = pygame.mask.from_threshold(player_surface,player_col,(10,10,10,255))
        if integral_hitbox.overlap(circle_mask,(0,0)):
                if current_phase != -1: damage_sfx.play()
                player_hp -= 1


        attack5_index += 1


 















running = True

while running:
    clock.tick(60)
    if current_phase >= 0 : screen.fill((255,255,255))
    player_surface.fill((255,255,255,0))
    shield_surface.fill((255,255,255,0))

    player_iframe_duration -= (1 if player_iframe_duration > 0 else 0)
    if player_iframe_duration == 0: player_in_iframe = False
          

    if current_phase == 2: shield_current_size = ((10)*shield_hp//5000) + shield_target_size - 10


    if dash_cooldown < 300:
        dash_cooldown += 1
        dash_cooldown_dx_target = 0
    else: dash_cooldown_dx_target = 1


    if player_in_iframe:
        flash_alpha = int(77.5* math.cos(math.radians(player_iframe_duration * 8)) + 177.5)
        player_col = (240, 216, 144, flash_alpha)
    else:
        player_col = (240, 216, 144, 255)



    dash_cooldown_dx += (25*dash_cooldown_dx_target - dash_cooldown_dx)/5
    attack3_circle_rad += (attack3_circle_rad_target - attack3_circle_rad)/15


    draw_player(player_pos[0],player_pos[1],player_col)
    draw_hands(player_pos[0],player_pos[1],angle,player_col)
    draw_gun(player_pos[0],player_pos[1],angle)

    if current_attack == 1 and current_phase == 1:
        boss_pos[0] += int((250 - boss_pos[0])/5)
        boss_pos[1] += int((125 - boss_pos[1])/5)
        attack3_circle_rad_target = math.sqrt(250**2 + 250**2) + 10
        target_y += ((-height//2 - 10) - target_y)/4
        target_x += (-target_x)/4
        attack1(120) #change to 30 later
        if not attack_1_start:
            attack2_start = True
            current_attack = 2

    elif current_attack == 2 and current_phase == 1:
        boss_pos[0] += int((425 - boss_pos[0])/15)
        boss_pos[1] += int((75 - boss_pos[1])/15)
        attack2()
        if not attack2_start:
            attack3_start = True
            graph_surface.fill((0, 0, 0, 0))
            timer_number_attacks = 0
            chosen_functions = random.sample(list_of_function, 5)
            current_attack = 3
    
    elif current_attack == 3 and current_phase == 1:
        boss_pos[0] += int((75 - boss_pos[0])/15)
        boss_pos[1] += int((75 - boss_pos[1])/15)
        function = ""
        target_x += (width-target_x)/4
        attack3_circle_rad_target = 250
        attack3()
        if not attack3_start:
            attack_1_start = True
            polar_surface.fill((0,0,0,0))
            random_angles_generation = [(math.radians(random.randint(-360,-60)) if random.randint(0,1) == 0 else math.radians(random.randint(60,360))) for i in range(5)]
            current_attack = 1

    if current_phase == 2 and current_attack == 4:
        attack4()
        if not attack_4_start:
            attack5_start = True
            new_chosen_functions = random.sample(list_of_new_functions,3)
            animation_max_y = player_pos[1]-450
            vector_surface.fill((0,0,0,0))
            current_attack = 5
    
    if current_phase == 2 and current_attack == 5:
        screen.blit(integral_surface,(0,0))
        attack5()
        if not attack5_start:
            current_attack = 4
            attack5_index = 0
            attack_4_start = True
            


    shield_hp_text = bigger_font.render(f"Shield HP: {shield_hp}" , True , (255,255,255) , (0,0,0))
    shield_hp_text_rect = shield_hp_text.get_rect(topright = (500,0))

    boss_impact_frame_rect = boss_impact_frame.get_rect(center=boss_pos)
    boss_hitbox = boss_image.get_rect(center = tuple(boss_pos))

    boss_hp_text = bigger_font.render(f"HP: {boss_hp if current_phase < 1.5 else 'ε'}",False,(0,0,0))
    boss_hp_text_rect = boss_hp_text.get_rect(center = (boss_pos[0],boss_pos[1] - 10-75/2))

    player_hp_text = bigger_font.render(f"Your HP: {player_hp}",False,(255,255,255),(0,0,0))
    player_hp_text_rect = player_hp_text.get_rect(bottomleft = (0,height))

    dash_cooldown_text = bigger_font.render(f"Dash (Q): {5 - dash_cooldown//60}",True,(255,255,255),(0,0,0))
    dash_cooldown_text_rect = dash_cooldown_text.get_rect(bottomright=(width,height + dash_cooldown_dx))

    now_graphing_text = bigger_font.render(f"Currently Graphing: " , True,(255,255,255),(0,0,0))
    now_graphing_text_rect = now_graphing_text.get_rect(topright=(target_x,45))

    if current_attack == 1 and current_phase == 1:
        current_graph_text = super_font.render(f"{function}",True,(255,255,255),(0,0,0))
        current_graph_text_rect = current_graph_text.get_rect(bottomright=(0,0))
    elif current_attack == 2 and current_phase == 1:
        current_graph_text = super_font.render(f"{function}",True,(255,255,255),(0,0,0))
        current_graph_text_rect = current_graph_text.get_rect(topleft=now_graphing_text_rect.bottomleft)
    elif current_attack == 3 and current_phase == 1:
        current_graph_text = super_font.render((f"re^i{-temp_angle}" if attack3_frame >= 180 else ""),True,(255,255,255),(0,0,0))
        current_graph_text_rect = current_graph_text.get_rect(topright=now_graphing_text_rect.bottomright)
    else:
        current_graph_text = super_font.render(f"{function}",True,(255,255,255),(0,0,0))
        current_graph_text_rect = current_graph_text.get_rect(bottomright=(0,0))
        now_graphing_text = bigger_font.render(f"Currently Graphing: " , True,(255,255,255),(0,0,0))
        now_graphing_text_rect = now_graphing_text.get_rect(bottomright=(0,0))


    mousex,mousey = pygame.mouse.get_pos()
    dx = mousex - player_pos[0]
    dy = mousey - player_pos[1]
    if current_phase >= 1 and isinstance(current_phase,int): angle = (math.atan2(dy, dx) + math.pi/2)

    offset_vec = pygame.math.Vector2(0, 0)
    offset_vec.from_polar((gun_h / 2, math.degrees(angle - math.pi/2)))
    bulletx,bullety = (int(23* math.cos(angle) + player_pos[0]) + offset_vec.x, int(23* math.sin(angle) + player_pos[1]) + offset_vec.y)
    

    if current_phase > 1: pygame.draw.aacircle(shield_surface,(0,255,255,255//2),tuple(boss_pos),shield_current_size)


    axis(width//2,target_y)
    screen.blit(graph_surface, (0, 0))
    screen.blit(polar_surface, (0, 0))
    screen.blit(shield_surface,(0,0))
    pygame.draw.circle(screen,(0,0,0),(width//2,height//2),attack3_circle_rad,10)



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and current_phase >= 1 and isinstance(current_phase,int):
            all_bullets.append(Bullet(angle,bulletx,bullety,10,2,10))
        if event.type == pygame.KEYDOWN and current_phase >= 1 and isinstance(current_phase,int):
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
        if current_phase == 1 or current_phase == 2:
            player_in_dash = False
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_w] and not attack5_start:
                if player_pos[1] - player_rad > 0:
                    player_pos[1] -= 3
            if pressed[pygame.K_s] and not attack5_start:
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
            movement_dy = (pressed[pygame.K_s] - pressed[pygame.K_w]) if not attack5_start else 0
            player_direction = (math.radians(270) if not attack5_start else math.radians(0)) if (movement_dx == 0 and movement_dy == 0) else math.atan2(movement_dy,movement_dx)

            if current_attack == 3 and current_phase == 1:
                cx, cy = width // 2, height // 2 #circle center x,y
                dx_fc = player_pos[0] - cx #delta x from circle
                dy_fc = player_pos[1] - cy
                dist = math.hypot(dx_fc, dy_fc)
                max_dist = attack3_circle_rad - player_rad - 5
                if dist > max_dist:
                    player_pos = [cx + dx_fc / dist * max_dist , cy + dy_fc / dist * max_dist]



    for item in all_bullets:
        item.draw(screen)
        if item.move(0,0,width,height):
            all_bullets.remove(item)

        if item.bullet_rect.colliderect(boss_hitbox) and current_phase == 1:
            random_damage_value = random.randint(8,13)
            random_damage_value_xpos = random.randint(10*boss_pos[0] - 375 , 10*boss_pos[0] + 375)//10
            random_damage_value_ypos = random.randint(10*boss_pos[1] - 375 , 10*boss_pos[1] + 375)//10 #since the distance from the edge to the center is 37.5, we multiply everything by 10 to get integers and divide by 10 later
            boss_hp -= random_damage_value
            all_damage_texts.append(Value(random_damage_value , random_damage_value_xpos , random_damage_value_xpos , random_damage_value_ypos , random_damage_value_ypos+20 ,24, 10 , 45 , (200,0,0)))
            all_bullets.remove(item)
        elif current_phase == 2 and circle_rect_collide(tuple(boss_pos),shield_current_size,item.bullet_rect):
            shield_hp -= 50 # change to 10 later
            random_damage_value_xpos = random.randint(10*boss_pos[0] - 375 , 10*boss_pos[0] + 375)//10
            random_damage_value_ypos = random.randint(10*boss_pos[1] - 375 , 10*boss_pos[1] + 375)//10
            all_damage_texts.append(Value(0 , random_damage_value_xpos , random_damage_value_xpos , random_damage_value_ypos , random_damage_value_ypos+20 ,24, 10 , 45 , (0,230,255)))
            all_bullets.remove(item)
    


    screen.blit(boss_image,boss_hitbox)
    screen.blit(boss_hp_text,boss_hp_text_rect)
    screen.blit(player_hp_text,player_hp_text_rect)
    screen.blit(dash_cooldown_text,dash_cooldown_text_rect)
    screen.blit(now_graphing_text,now_graphing_text_rect)
    screen.blit(current_graph_text,current_graph_text_rect)
    if current_phase == 2: screen.blit(shield_hp_text,shield_hp_text_rect)

    screen.blit(vector_surface,(0,0))

    if current_phase == 1: attack5()
    screen.blit(player_surface,(0,0))

    for item in all_damage_texts:
        item.draw(screen)
        if item.move():
            all_damage_texts.remove(item)


    for item in number_attack_list:
        item.move()
        item.draw(screen)
        if circle_rect_collide(tuple(player_pos),player_rad,item.hitbox):
            if not player_in_dash:
                number_attack_list.remove(item)
                if current_phase != -1 and isinstance(current_phase,int): damage_sfx.play()
                player_hp -= item.value



    if current_phase == 0.5:
        init_cutscene()
    if player_hp <= 0:
        death()
    if boss_hp <= 0 and current_phase < 2:
            cutscene_phase2()


    pygame.display.flip()



pygame.quit()
sys.exit()