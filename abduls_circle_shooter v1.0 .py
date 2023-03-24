# Game by Abdul
# V 1.3
# Copyright - Public Domain
# Feel free to modify, copy and distribute

# Special Thanks to Al Sweigart for his wonderful pygame tutorial, https://inventwithpython.com/pygame/ 
# Without it I would have never learned to use the pygame library

# Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygameAl 

#Royalty-Free sound effects & music from pixabay.com

#Boilerplate statements that must always be called
import pygame, sys, random
import os
from pygame.locals import *
from time import sleep
#sys and os must be imported for us to compile the game into a exe
#no idea what the below statement does but it is necessary for compilation
def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


pygame.init()

FPS = 60.0
fpsClock = pygame.time.Clock()

# Variable Declarations
window_height = 720
window_width = 1280
centre_x = window_width / 2
centre_y = window_height / 2
circle_radius = 20.0
player_speed = 5
render_mouse_line = True
mouse_line_x = 0.0
mouse_line_y = 0.0
frame_count = 0
past_player_counter = 0
player_damage = 10
player_health = 100
player_is_alive = True
circle_diameter = circle_radius * 2
player_respawn_counter = 0
after_burner = False
after_burner_timer = 0
play_waiting_sound = False #Should we play 'waiting_for_a_respawn'?

kills = 0
player_color = (  0,   0, (255 * player_health / 100))


player_orbit_box_x = circle_radius + circle_diameter * 2
player_orbit_box_y = circle_radius + circle_diameter * 2
past_player_location_x = centre_x
past_player_location_y = centre_y

# color               R    G    B
black            = (  0,   0,   0)
grey             = (136, 136, 136)
dark_grey        = ( 50,  50,  50)
very_dark_grey   = ( 25,  25,  25)
white            = (255, 255, 255)
red              = (255,   0,   0)
orange           = (255, 100,   0)
green            = (  0, 255,   0)
blue             = (  0,   0, 255)
yellow           = ( 255, 255,  0)
cyan             = (  0, 255, 255)

#sound and backround
backround_image = pygame.image.load("backround.jpg")
background_music = pygame.mixer.music.load("backround.mp3") # royalty free music files from pixabay
ship_fire = pygame.mixer.Sound("ship_fire.mp3")
enemy_fire = pygame.mixer.Sound("enemy_fire.mp3")
waiting_for_a_respawn = pygame.mixer.Sound("waiting_for_a_respawn.mp3")

#motion
up = 'up'
up_left = 'up_left'
up_right = 'up_right'
down = 'down'
down_left = 'down_left'
down_right = 'down_right'
left = 'left'
right = 'right'
static = 'static'
angular_motion = (up_left, up_right, down_left, down_right)

list_of_enemies = []

class enemy(): #Enemy class
    def __init__(self, spawn_trigger, enemy_x = None, enemy_y = None, enemy_speed = None, enemy_in_range = None, enemy_fire_count = None, enemy_health = None, enemy_damage = None, enemy_color = None, enemy_is_alive = None, enemy_motion = None, enemy_respawn_counter = None):
        if enemy_x is None:
            enemy_x = random.randint(circle_diameter, window_width - circle_diameter)
        if enemy_y is None:
            enemy_y = random.randint(circle_diameter, window_height - circle_diameter)
        if enemy_speed is None:
            enemy_speed = random.randint(1, 6)
        if enemy_in_range is None:
            enemy_in_range = False
        if enemy_fire_count is None:
            enemy_fire_count = 0
        if enemy_health is None:
            enemy_health = 0
        if enemy_damage is None:
            enemy_damage = 25
        if enemy_color is None:
            enemy_color = ((255 * enemy_health / 100),   0,  0)
        if enemy_is_alive is None:
            enemy_is_alive = False
        if enemy_motion is None:
            enemy_motion = left
        if enemy_respawn_counter is None:
            enemy_respawn_counter = 0

        self.enemy_x = enemy_x
        self.enemy_y = enemy_y
        self.enemy_speed = enemy_speed
        self.enemy_in_range = enemy_in_range
        self.enemy_fire_count = enemy_fire_count
        self.enemy_health = enemy_health
        self.enemy_damage = enemy_damage
        self.enemy_color = enemy_color
        self.enemy_is_alive = enemy_is_alive
        self.enemy_motion = enemy_motion
        self.enemy_respawn_counter = enemy_respawn_counter
        self.spawn_trigger = spawn_trigger
        
        list_of_enemies.append(self)

#enemy generation

enemy1 = enemy(-1)
enemy2 = enemy(5)
enemy3 = enemy(10)
enemy4 = enemy(15)
enemy5 = enemy(20)
enemy6 = enemy(25)
enemy7 = enemy(30)
enemy8 = enemy(35)
enemy9 = enemy(40)
enemy10 = enemy(45)
enemy11 = enemy(50)
enemy12 = enemy(55)

default_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Abdul's Circle Shooter")
pygame.mixer.music.play(-1, 0.0) # play the music
fps_clock = pygame.time.Clock()
trail_surface = pygame.Surface((320, 240)) #size of the trail surface is not important
#this surface is used to rotate the trail as Rect objects cannot be rotated.
motion = static #motion of the ball is static
enemy1.enemy_is_alive = True
enemy1.enemy_health = 100
enemy1.enemy_speed = 5
#font processing
font_object = pygame.font.Font('freesansbold.ttf', 32)
textSurfaceObj = font_object.render('You died. Respawning soon', True, blue, black)
textRectObj = textSurfaceObj.get_rect()

textRectObj.centerx = window_width / 2
textRectObj.centery = window_height / 2

def terminateGame():
    pygame.quit()
    sys.exit()

def topDeflectMotion(motion):
# deflects angular motion and only angular motion
    if motion == up_left:
        motion = down_left
    elif motion == up_right:
        motion = down_right
    elif motion == down_left:
        motion = up_left
    elif motion == down_right:
        motion = up_right

    return motion

def sideDeflectMotion(motion):
# deflects angular motion and only angular motion
    if motion == up_left:
        motion = up_right
    elif motion == up_right:
        motion = up_left
    elif motion == down_left:
        motion = down_right
    elif motion == down_right:
        motion = down_left

    return motion   

def checkForCollision(centre_y, centre_x, motion): 
    #change the direction of the ball once hitting the wall
    if centre_x > window_width - circle_radius:
        if motion in angular_motion:
            motion = sideDeflectMotion(motion)
        else:
            motion = left
    if centre_x < circle_radius:
        if motion in angular_motion:
            motion = sideDeflectMotion(motion)
        else:
            motion = right
    if centre_y > window_height - circle_radius:
        if motion in angular_motion:
            motion = topDeflectMotion(motion)
        else:
            motion = up
    if centre_y < circle_radius:
        if motion in angular_motion:
            motion = topDeflectMotion(motion)
        else:
            motion = down

    return motion

def moveBall(centre_y, centre_x, motion, motion_increment):
    #update the position of the ball based on which direction it should move
    if motion == static:
        return centre_y, centre_x
    if motion == up:
        centre_y -= motion_increment
    if motion == down:
        centre_y += motion_increment       
    if motion == left:
        centre_x -= motion_increment
    if motion == right:
        centre_x += motion_increment
    if motion == up_left:
        centre_y -= motion_increment
        centre_x -= motion_increment
    if motion == up_right:
        centre_y -= motion_increment
        centre_x += motion_increment
    if motion == down_left:
        centre_y += motion_increment
        centre_x -= motion_increment
    if motion == down_right:
        centre_y += motion_increment
        centre_x += motion_increment

    return centre_y, centre_x

def calculateTrail(circle_x, circle_y, circle_diameter, motion, color):
    #return a Rect with the position of the trail for drawing later
    if motion == static:
        circle_trail = None
    if motion == up:
        circle_trail = pygame.Rect(circle_x, circle_y, circle_diameter, circle_diameter * 2)
    if motion == down:
        circle_trail = pygame.Rect(circle_x, circle_y - circle_diameter, circle_diameter, circle_diameter * 2)
    if motion == left:
        circle_trail = pygame.Rect(circle_x, circle_y, circle_diameter * 2, circle_diameter)
    if motion == right:
        circle_trail = pygame.Rect(circle_x - circle_diameter, circle_y, circle_diameter * 2, circle_diameter)
    #This is a bit complex. Create a surface, draw the trail to it, rotate the surface and then blit it to the default_surface
    if motion == up_left:
        circle_trail = pygame.Rect(circle_x + circle_radius, circle_y, circle_diameter, circle_diameter * 2)
        trail_surface = pygame.Surface(circle_trail.size, pygame.SRCALPHA)
        pygame.draw.ellipse(trail_surface, color, (0, 0, *circle_trail.size), int(circle_radius))
        rotated_trail_surface = pygame.transform.rotate(trail_surface, 45)
        default_surface.blit(rotated_trail_surface, rotated_trail_surface.get_rect(center = circle_trail.center))
        circle_trail = None #Do not return a trail if we have blitted one already.
    if motion == up_right:
        circle_trail = pygame.Rect(circle_x - circle_radius, circle_y, circle_diameter, circle_diameter * 2)
        trail_surface = pygame.Surface(circle_trail.size, pygame.SRCALPHA)
        pygame.draw.ellipse(trail_surface, color, (0, 0, *circle_trail.size), int(circle_radius))
        rotated_trail_surface = pygame.transform.rotate(trail_surface, -45)
        default_surface.blit(rotated_trail_surface, rotated_trail_surface.get_rect(center = circle_trail.center))
        circle_trail = None
    if motion == down_left:
        circle_trail = pygame.Rect(circle_x + circle_radius, circle_y - circle_diameter, circle_diameter, circle_diameter * 2)
        trail_surface = pygame.Surface(circle_trail.size, pygame.SRCALPHA)
        pygame.draw.ellipse(trail_surface, color, (0, 0, *circle_trail.size), int(circle_radius))
        rotated_trail_surface = pygame.transform.rotate(trail_surface, -45)
        default_surface.blit(rotated_trail_surface, rotated_trail_surface.get_rect(center = circle_trail.center))
        circle_trail = None
    if motion == down_right:
        circle_trail = pygame.Rect(circle_x - circle_radius, circle_y - circle_diameter, circle_diameter, circle_diameter * 2)
        trail_surface = pygame.Surface(circle_trail.size, pygame.SRCALPHA)
        pygame.draw.ellipse(trail_surface, color, (0, 0, *circle_trail.size), int(circle_radius))
        rotated_trail_surface = pygame.transform.rotate(trail_surface, 45)
        default_surface.blit(rotated_trail_surface, rotated_trail_surface.get_rect(center = circle_trail.center))
        circle_trail = None

    return circle_trail

def enemyAI(centre_x, centre_y, enemy1_x, enemy1_y, current_player_x, current_player_y):
    if enemy1_x > centre_x + player_orbit_box_x:
        in_x_orbit_box = False
    elif enemy1_x < centre_x - player_orbit_box_x:
        in_x_orbit_box = False
    else:
        in_x_orbit_box = True

    if enemy1_y > centre_y + player_orbit_box_y:
        in_y_orbit_box = False
    elif enemy1_y < centre_y - player_orbit_box_y:
        in_y_orbit_box = False
    else:
        in_y_orbit_box = True

    if in_x_orbit_box == True and in_y_orbit_box == True:
        motion = orbit_player(current_player_x, current_player_y, enemy1_x, enemy1_y)
        enemy1_in_range = True
    else:
        motion = huntPlayer(centre_x, centre_y, enemy1_x, enemy1_y)
        enemy1_in_range = False

    return motion, enemy1_in_range

def orbit_player(current_player_x, current_player_y, enemy1_x, enemy1_y):
    #clockwise orbiting of the player ball
    #create a grid with positions that the enemy could be in and move to the next region on the grid
    if enemy1_x > centre_x + circle_radius: # Enemy is left of the player
        if enemy1_y > centre_y + circle_radius: # bottom left
            motion = down_left
        elif enemy1_y < centre_y - circle_radius: #top left
            motion = down_right
        else: #midleft
            motion = down
    elif enemy1_x < centre_x - circle_radius: # Enemy is right of the player
        if enemy1_y > centre_y + circle_radius: # bottom right
            motion = up_left
        elif enemy1_y < centre_y - circle_radius: #top right
            motion = up_right
        else: #midright
            motion = up
    else: # directly above or below
        if enemy1_y > centre_y: #below
            motion = left
        else:
            motion = right
    return motion

def shootPlayer(centre_x, centre_y, enemy1_x, enemy1_y, motion, player_health, player_is_alive, enemy_damage, shoot_player_count = 0, fire = False, recalculate = True):    
    if player_is_alive == True:
        shoot_player_count += 1
        if motion != static:
            shooting_box = circle_radius + circle_diameter
        else:
            shooting_box = circle_radius + circle_radius
        if shoot_player_count > 5:
            recalculate = True
        shoot_player_count = 0

        if recalculate == True:
            firepoint_x = random.randint((centre_x - shooting_box), (centre_x + shooting_box))
            firepoint_y = random.randint((centre_y - shooting_box), (centre_y + shooting_box))
            enemy1_coordinates = (float(enemy1_x), float(enemy1_y))
            firepoint_coordinates = (float(firepoint_x), float(firepoint_y))
            recalculate = False

        pygame.draw.line(default_surface, yellow, enemy1_coordinates, firepoint_coordinates, 4)
        enemy_fire.play(3, 1000)
        player_health = takeDamage(firepoint_x, firepoint_y, centre_y, centre_x, player_health, yellow, enemy_damage)
    return player_health
        
def takeDamage(mouse_line_x, mouse_line_y, centre_y, centre_x, health, flash_color, player_damage):
    target_coordinates = (float(centre_x), float(centre_y))
    if mouse_line_x < centre_x + circle_radius and mouse_line_x > centre_x - circle_radius and mouse_line_y > centre_y - circle_radius and mouse_line_y < centre_y + circle_radius:
        if health >= player_damage:
            health -= player_damage
            flashBall(target_coordinates, flash_color)
    

    return health

def flashBall(target_coordinates, flash_color):
    pygame.draw.circle(default_surface, flash_color, target_coordinates, circle_radius)
    
def isAlive(health, is_alive):
    if health <= 0:
        is_alive = False
    else:
        is_alive = True
    
    return is_alive

def updateEnemyColor(color, health):
    value = (255 * health) / 100
    value = int(value)
    color = (value, 0, 0)
    return color

def updatePlayerColor(color, health):
    value = (255 * health) / 100
    value = int(value)
    color = (0, 0, 255)
    return color

def huntPlayer(centre_x, centre_y, enemy1_x, enemy1_y):
    if enemy1_x > centre_x: # The player is to the left of the enemy
        x_go_to = left 
    elif enemy1_x < centre_x: # The player is to the right of the enemy
        x_go_to = right
    else:
        x_go_to = None

    if enemy1_y > centre_y: # The player is above the enemy
        y_go_to = up
    elif enemy1_y < centre_y: # The player is below the enemy
        y_go_to = down
    else:
        y_go_to = None

    if x_go_to == left and y_go_to == up:
        enemy_motion = up_left
    elif x_go_to == left and y_go_to == down:
        enemy_motion = down_left
    elif x_go_to == right and y_go_to == up:
        enemy_motion = up_right
    elif x_go_to == right and y_go_to == down:
        enemy_motion = down_right
    elif x_go_to == None and y_go_to == None:
        enemy_motion = static
    elif x_go_to == left and y_go_to == None:
        enemy_motion = left
    elif x_go_to == right and y_go_to == None:
        enemy_motion = right
    elif x_go_to == None and y_go_to == up:
        enemy_motion = up
    elif x_go_to == None and y_go_to == down:
        enemy_motion = down    

    return enemy_motion

def revive(player_is_alive, player_health):
    player_health = 100
    player_is_alive = True

    return player_is_alive, player_health

while True: #The main game loop
    default_surface.fill(black)
    default_surface.blit(backround_image, (0, 0))
    frame_count += 1
    enemy1.enemy_fire_count += 1
    past_player_counter += 1
    if after_burner == True:
        player_speed = 10
        if after_burner_timer <= FPS / 2: 
            after_burner_timer += 1
    else:
        player_speed = 5
        if after_burner_timer > 0:
            after_burner_timer -= 0.1

    if player_is_alive == False:
        if player_respawn_counter == 0:
            waiting_for_a_respawn.play(0, 3000)
        player_respawn_counter += 1
        default_surface.blit(textSurfaceObj, textRectObj)
        
    if player_respawn_counter > FPS * 3:
        kills = -1
        player_is_alive, player_health = revive(player_is_alive, player_health)
        player_respawn_counter = 0
        for i in list_of_enemies:
            i.enemy_is_alive = False
            i.enemy_health = 0
            i.enemy_is_alive = isAlive(i.enemy_health, i.enemy_is_alive)
    

    if frame_count >= FPS: # a second
        frame_count = 0
    
    kill_surface = font_object.render(f'Kills : {kills}', True, blue, black)
    kill_rect_object = kill_surface.get_rect()
    kill_rect_object.centerx = 80
    kill_rect_object.centery = 20
    default_surface.blit(kill_surface, kill_rect_object)
    pressed = pygame.key.get_pressed()
    mouse_pressed = pygame.mouse.get_pressed()
    #check to see if everyone is alive
    player_is_alive = isAlive(player_health, player_is_alive)
    #add the player.
    if player_is_alive == True:
        player_color = updatePlayerColor(player_color, player_health)
        motion = checkForCollision(centre_y, centre_x, motion)
        centre_y, centre_x = moveBall(centre_y, centre_x, motion, player_speed) #Update coordinates of the ball
        circle_coordinates = (float(centre_x), float(centre_y))
        circle_x = centre_x - circle_radius
        circle_y = centre_y - circle_radius
        circle_trail = calculateTrail(circle_x, circle_y, circle_diameter, motion, cyan)
        if circle_trail != None:
            pygame.draw.ellipse(default_surface, cyan, circle_trail) #Draw trail if we need one
        pygame.draw.circle(default_surface, player_color, circle_coordinates, circle_radius)
        if past_player_counter > 30:
            past_player_location_x = centre_x
            past_player_location_y = centre_y
            past_player_counter = 0
        mouse_line_coordinates = (float(mouse_line_x), float(mouse_line_y))

    #enemy processing 
    for i in list_of_enemies:
        i.enemy_is_alive = isAlive(i.enemy_health, i.enemy_is_alive)
    for i in list_of_enemies:
        if i.enemy_is_alive == False and kills >= i.spawn_trigger:
            i.enemy_respawn_counter += 1
        if i.enemy_respawn_counter == 1:
            kills += 1
        if i.enemy_respawn_counter > FPS * 3:
            i.enemy_respawn_counter = 0
            i.enemy_is_alive, i.enemy_health = revive(i.enemy_is_alive, i.enemy_health)
            i.enemy_x = random.randint(window_width - 200, window_width + circle_diameter)
            i.enemy_y = random.randint(0 - window_height, window_height * 2)
            i.enemy_motion = left
        if i.enemy_is_alive == True:
            i.enemy_color = updateEnemyColor(i.enemy_color, i.enemy_health)
            i.enemy_coordinates = (float(i.enemy_x), float(i.enemy_y))
            i.enemy_motion, i.enemy_in_range = enemyAI(past_player_location_x, past_player_location_y, i.enemy_x, i.enemy_y, centre_x, centre_y)
            i.enemy_y, i.enemy_x = moveBall(i.enemy_y, i.enemy_x, i.enemy_motion, i.enemy_speed)
            i.enemy_motion = checkForCollision(i.enemy_y, i.enemy_x, i.enemy_motion)
        #Drawing. The order they are drawn determines what is on top of what
            enemy_circle_trail = calculateTrail((i.enemy_x - circle_radius), (i.enemy_y - circle_radius), circle_diameter, i.enemy_motion, yellow)
            if enemy_circle_trail != None:
                pygame.draw.ellipse(default_surface, yellow, enemy_circle_trail)
            pygame.draw.circle(default_surface, i.enemy_color, i.enemy_coordinates, circle_radius)

    if player_is_alive == True:
        if frame_count > 5:
            render_mouse_line = False
            frame_count = 0
        if render_mouse_line == True:
            #Draw a line from the centre of the circle, but for no more than 3 frames.
            pygame.draw.line(default_surface, green, circle_coordinates, mouse_line_coordinates, 4)
            ship_fire.play(0, 500)
            for i in list_of_enemies: 
                i.enemy_health = takeDamage(mouse_line_x, mouse_line_y, i.enemy_y, i.enemy_x, i.enemy_health, green, player_damage)
            #update the dynamic color
        pygame.draw.circle(default_surface, player_color, circle_coordinates, circle_radius) #cover part of the line with an identical circle

    for i in list_of_enemies:
        if i.enemy_is_alive == True: # this is in a seperate block to ensure that the enemy fire is always drawn on top
            if i.enemy_in_range == True and i.enemy_fire_count > 5:
                player_health = shootPlayer(centre_x, centre_y, i.enemy_x, i.enemy_y, motion, player_health, player_is_alive, i.enemy_damage)
                i.enemy_fire_count = 0

    #user input processing
    #afterburner
    if pressed[pygame.K_e] and after_burner_timer < FPS / 2:
        after_burner = True
    else:
        after_burner = False
    #check if a key is held down, and give motion if it is
    if pressed[pygame.K_p] or pressed[pygame.K_ESCAPE]:
        motion = static
        circle_trail = None
    if pressed[pygame.K_w]:
        motion = up
    elif pressed[pygame.K_s]:
        motion = down
    if pressed[pygame.K_a]:
        motion = left
    elif pressed[pygame.K_d]:
        motion = right

    if pressed[pygame.K_w] and pressed[pygame.K_a]:
        motion = up_left
    if pressed[pygame.K_w] and pressed[pygame.K_d]:
        motion = up_right
    if pressed[pygame.K_s] and pressed[pygame.K_a]:
        motion = down_left
    if pressed[pygame.K_s] and pressed[pygame.K_d]:
        motion = down_right

    if mouse_pressed[0] == True: #while the mouse is held, continously flash a line
        if frame_count > 1:
            render_mouse_line = False
        else:
            render_mouse_line = True
        
    pygame.display.update()
    fps_clock.tick(FPS) 
    
    for event in pygame.event.get(): #event_handling_loop
        if event.type == QUIT:
            terminateGame()
        elif event.type == MOUSEBUTTONDOWN:
            if render_mouse_line == False:
                render_mouse_line = True
                frame_count = 0
            elif render_mouse_line == True:
                render_mouse_line = False
        elif event.type == MOUSEMOTION:
            mouse_line_x, mouse_line_y = event.pos
        elif event.type == KEYDOWN:
            if event.key == K_q:
                for i in list_of_enemies:
                    if kills >= i.spawn_trigger:
                        i.enemy_respawn_counter = FPS * 3
                player_respawn_counter = FPS * 2
            if event.key == K_0:
                kills = 89 # 100 after the enemies begin their respawn countdowns.