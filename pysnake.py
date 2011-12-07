'''
PySnake

@author: Freddie Pettersson
'''

#!/usr/bin/env python 

import pygame, random
from sys import exit

# common constants
screen_size = (800, 600)
tile_size = (20, 20)
background_color = (50,50,50)
        
class Segment(pygame.sprite.Sprite):
    def __init__(self, x, y, segment_groups, color = (0,255,0)):
        # init this sprite
        pygame.sprite.Sprite.__init__(self)
        # create the sprite image (background surface) and fill it
        self.image = pygame.Surface(tile_size).convert()
        self.image.fill(background_color)
        # draw a square upon the image
        self.color = color
        pygame.draw.rect(self.image, self.color, pygame.Rect(0,0,tile_size[0]-1,
                                                             tile_size[1]-1))
        # set the position of this segment
        self.x = x
        self.y = y
        # the bounds of this sprite
        self.rect = self.image.get_rect()
        # put this sprite on the specified position
        self.rect.topleft = (self.x * tile_size[0], self.y * tile_size[1])
        # add this segment to all segment groups
        self.segment_groups = segment_groups
        for group in segment_groups:
            group.add(self)
        # set no subsequent segment
        self.subsequent = None
        # set starting direction to left
        self.direction = (-1,0)
        # boolen used to determine if this segment is alive or not
        self.is_alive = True
    
    def extend(self):
        segment = self
        while segment.subsequent != None:
            segment = segment.subsequent
        x = segment.x - segment.direction[0]
        y = segment.y - segment.direction[1]
        segment.subsequent = Segment(x, y, segment.segment_groups)
        segment.subsequent.direction = segment.direction
    
    def explode(self):
        if self.is_alive:
            self.is_alive = False
            pygame.draw.rect(self.image, (255,0,0), pygame.Rect(0,0,tile_size[0]-1,
                                                                 tile_size[1]-1))
            if self.subsequent != None:
                self.subsequent.explode()
    
    def move(self):
        if self.is_alive:
            self.x += self.direction[0]
            self.y += self.direction[1]
            self.rect.move_ip((self.direction[0]*tile_size[0], 
                           self.direction[1]*tile_size[1]))
            if self.subsequent != None:
                self.subsequent.move()
                self.subsequent.direction = self.direction

class Bonus(pygame.sprite.Sprite):
    def __init__(self, occupied_group):
        # init this sprite
        pygame.sprite.Sprite.__init__(self)
        # create the sprite image (background surface) and fill it
        self.image = pygame.Surface(tile_size).convert()
        self.image.fill(background_color)
        # draw a (red) circle upon the image
        self.color = (255,0,0)
        pygame.draw.circle(self.image, self.color, 
                           pygame.Rect(0, 0, tile_size[0], tile_size[1]).center,
                           tile_size[0]/2-1)
        # the bounds of this sprite
        self.rect = self.image.get_rect()
        # put this sprite on a valid random position (where it doesn't collide)
        valid_pos = False
        while not valid_pos:
            valid_pos = True
            # pick and move to a random position
            self.rect.topleft = (random.choice(range(tile_size[0], 
                                                     screen_size[0]-
                                                     tile_size[0],
                                                     tile_size[0])), 
                                 random.choice(range(tile_size[1], 
                                                     screen_size[1]-
                                                     tile_size[1],
                                                     tile_size[1])))
            # check for collisions
            for sprite in occupied_group:
                # continue loop if the sprite collides
                if self.rect.colliderect(sprite):
                    valid_pos = False

class Wall(pygame.sprite.Sprite):
    def __init__(self, occupied_group, x = None, y = None):
        # init this sprite
        pygame.sprite.Sprite.__init__(self)
        # create the sprite image (background surface) and fill it
        self.image = pygame.Surface(tile_size).convert()
        self.image.fill(background_color)
        # draw a (grey) square upon the image
        self.color = (150,150,150)
        pygame.draw.rect(self.image, self.color,
                         pygame.Rect(0,0,tile_size[0]-1,tile_size[1]-1))
        # the bounds of this sprite
        self.rect = self.image.get_rect()
        # no position has been specified
        if x == None or y == None:
            # put this sprite on a valid random position
            valid_pos = False
            while not valid_pos:
                valid_pos = True
                # pick and move to a random position
                self.rect.topleft = (random.choice(range(tile_size[0],
                                                         screen_size[0]-
                                                         tile_size[0],
                                                         tile_size[0])), 
                                     random.choice(range(tile_size[1],
                                                         screen_size[1]-
                                                         tile_size[1],
                                                         tile_size[1])))
                # check for collisions
                for sprite in occupied_group:
                    # continue loop if the sprite collides
                    if self.rect.colliderect(sprite):
                        valid_pos = False
        # move the sprite to the specified position
        else:
            self.rect.topleft = (x, y)

class PySnake(object):
    def __init__(self):
        # init pygame module
        pygame.init()
        # create the screen (display)
        self.screen = pygame.display.set_mode(screen_size)
        # print name and version to console and screen caption
        self.name = "PySnake"
        self.version = "0.10"
        print self.name, "v"+self.version
        pygame.display.set_caption(self.name+" v"+self.version)
        # create and fill the background surface and put it on the screen
        self.background = pygame.Surface(screen_size).convert()
        self.background.fill(background_color)
        self.screen.blit(self.background, (0, 0))
        # create sprite groups
        self.body_group = pygame.sprite.Group()
        self.head_group = pygame.sprite.Group()
        self.bonus_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        self.all_group = pygame.sprite.RenderUpdates()
        # create surrounding wall-blocks
        y = 0
        for x in range(0, screen_size[0]-1, tile_size[0]):
            wall = Wall(self.all_group, x, y)
            self.wall_group.add(wall)
            self.all_group.add(wall)
        y = screen_size[1]-tile_size[1]
        for x in range(tile_size[0], screen_size[0], tile_size[0]):
            wall = Wall(self.all_group, x, y)
            self.wall_group.add(wall)
            self.all_group.add(wall)
        x = 0
        for y in range(0, screen_size[1]-1, tile_size[1]):
                wall = Wall(self.all_group, x, y)
                self.wall_group.add(wall)
                self.all_group.add(wall)
        x = screen_size[0]-tile_size[0]
        for y in range(tile_size[1], screen_size[1]-tile_size[1], tile_size[1]):
                wall = Wall(self.all_group, x, y)
                self.wall_group.add(wall)
                self.all_group.add(wall)
        # create the 4 disturbing wall-blocks in each corner
        wall = Wall(self.all_group, 6*tile_size[0], 6*tile_size[1])
        wall.add(self.all_group)
        self.wall_group.add(wall)
        wall = Wall(self.all_group, screen_size[0]-7*tile_size[0], 
                    screen_size[1]-7*tile_size[1])
        wall.add(self.all_group)
        self.wall_group.add(wall)
        wall = Wall(self.all_group, 6*tile_size[0],
                    screen_size[1]-7*tile_size[1])
        wall.add(self.all_group)
        self.wall_group.add(wall)
        wall = Wall(self.all_group, screen_size[0]-7*tile_size[0], 
                    6*tile_size[1])
        wall.add(self.all_group)
        self.wall_group.add(wall)
        # create the player with initially 8 segments (head + 7)
        self.player = Segment(screen_size[0]/tile_size[0]/2, 
                             screen_size[1]/tile_size[1]/2,
                             [self.body_group, self.all_group],
                             (255,255,0))
        self.head_group.add(self.player)
        self.all_group.add(self.player)
        for i in range(7):
            self.player.extend()
        # init game variables
        self.is_paused = False
        self.game_over = False
        self.next_direction = (-1,0)
        self.score = 0
        self.bonus = None
        self.time_passed = 0
        self.wait_time = 5
        # init clock
        self.clock = pygame.time.Clock()
        # flip the display to update the full display surface to the screen
        pygame.display.flip()
    
    def update(self):
        '''
        Updates every sprite.
        Handles player movement and bonus spawning.
        '''
        if self.bonus == None:
            self.bonus = Bonus(self.all_group)
            self.bonus_group.add(self.bonus)
            self.all_group.add(self.bonus)
        # move the player if enough time has passed
        self.time_passed += 2
        if not self.is_paused and self.time_passed > self.wait_time:
            self.player.direction = self.next_direction
            self.player.move()
            self.time_passed = 0
        
    def collisions(self):
        '''
        Checks if any sprite collides with another.
        Use this method to give bonus score or to determine if the game is over.
        '''
        # check if head collides with any bonus
        bonus_collisions = pygame.sprite.groupcollide(self.head_group,
                                                      self.bonus_group, 
                                                      False, True)
        for group in bonus_collisions:
            # bonus collision detected; extend player and increase score
            for sprite in bonus_collisions[group]:
                self.player.extend()
                self.bonus = None
                self.score += 1
                # increase speed
        # check if head collides with any part of the body
        suicide_collisions = pygame.sprite.groupcollide(self.head_group,
                                                        self.body_group,
                                                        False, False)
        for group in suicide_collisions:
            for sprite in suicide_collisions[group]:
                # critical head to body collision detected; game over
                if not sprite is self.player:
                    self.game_over = True
                    self.player.explode()
        # check if head collides with any walls
        wall_collisions = pygame.sprite.groupcollide(self.head_group,
                                                     self.wall_group,
                                                     False, False)
        for group in wall_collisions:
            # critical wall collision detected; game over 
            for sprite in wall_collisions[group]:
                self.game_over = True
                self.player.explode()
    
    def draw(self):
        '''
        Draws every sprite onto the screen and updates the display.
        '''
        # clear the screen
        self.all_group.clear(self.screen, self.background)
        # draw every sprite
        dirty = self.all_group.draw(self.screen)
        # print the score
        font = pygame.font.Font(None, 20)
        score_text = font.render("Score: "+str(self.score), True, (0,255,0))
        score = self.screen.blit(score_text, (4*tile_size[0]/2,0))
        dirty.append(score)
        # pint game instructions
        font = pygame.font.Font(None, 20)
        instructions_text = font.render("Arrows controls, "+
                                        "'PAUSE' or 'P' pauses, "+
                                        "'F2' or 'R' restarts, "+
                                        "'ESC' quits", True, (0,0,0))
        instructions = self.screen.blit(instructions_text, (4*tile_size[0],screen_size[1]-tile_size[1]))
        dirty.append(instructions)
        # print game over text if game is over
        if self.game_over:
            game_over_text = font.render("Game over!", True, (255,0,0))
            game_over = self.screen.blit(game_over_text, (screen_size[0]/2,0))
            dirty.append(game_over)
        # print pause text if game is paused
        if self.is_paused:
            paused_text = font.render("Paused", True, (0,0,255))
            paused = self.screen.blit(paused_text, (screen_size[0]/2,0))
            dirty.append(paused)
        # update
        pygame.display.update(dirty)

    def run(self):
        '''
        Starts and runs the main-loop of the game.
        '''
        while True:
            # handle events
            for event in pygame.event.get():
                # quit the game
                if event.type == pygame.QUIT:
                    print "quit"
                    exit()
                # handle keystroke
                elif event.type == pygame.KEYDOWN:
                    # only handle direction changes if not paused
                    if not self.is_paused and not self.game_over:
                        # change player direction to up
                        if (event.key == pygame.K_UP and 
                            self.player.direction != (0,1)):
                            self.next_direction = (0,-1)
                        # change player direction to down
                        elif (event. key == pygame.K_DOWN and
                              self.player.direction != (0,-1)):
                            self.next_direction = (0,1)
                        # change player direction to left
                        elif (event.key == pygame.K_LEFT and
                              self.player.direction != (1,0)):
                            self.next_direction = (-1,0)
                        # change player direction to right
                        elif (event.key == pygame.K_RIGHT and
                              self.player.direction != (-1,0)):
                            self.next_direction = (1,0)
                    # toggle pause (pause or unpause the game)
                    if not self.game_over and (event.key == pygame.K_PAUSE or 
                                               event.key == pygame.K_p):
                        print "pause"
                        self.is_paused = not self.is_paused
                    # restart the game
                    elif event.key == pygame.K_F2 or event.key == pygame.K_r:
                        print "restart"
                        PySnake().run()
                    # quit the game
                    elif event.key == pygame.K_ESCAPE:
                        print "quit"
                        exit()
            if not self.game_over:
                # update game components
                self.update()
                # handle sprite collisions
                self.collisions()
            # draw graphics
            self.draw()
            # wait a while
            self.clock.tick(30)

# Start it up!
if __name__ == '__main__':
    game = PySnake()
    game.run()
