import random
import math
from pygame import Rect

# Game constants
WIDTH = 800
HEIGHT = 600
TILE_SIZE = 64
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

class Character:
    def __init__(self, x, y, speed, animations):
        self.x = x
        self.y = y
        self.speed = speed
        self.animations = animations
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.direction = 'right'
        self.target_x = x
        self.target_y = y
        self.moving = False
        
    def update(self):
        # Update animation frame
        self.animation_frame += self.animation_speed
        if self.animation_frame >= len(self.animations[self.current_animation]):
            self.animation_frame = 0
            
        # Move towards target
        if self.moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < self.speed:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
                self.current_animation = 'idle'
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                
                # Determine direction for animation
                if abs(dx) > abs(dy):
                    self.direction = 'right' if dx > 0 else 'left'
                else:
                    self.direction = 'down' if dy > 0 else 'up'
    
    def draw(self):
        frame = int(self.animation_frame)
        img = self.animations[self.current_animation][frame]
        
        if self.direction == 'left':
            img = img.copy()  # Create a copy to avoid modifying the original
            img.xscale = -1  # Flip horizontally
            
        screen.blit(img, (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2))
        
    def move_to(self, x, y):
        self.target_x = x
        self.target_y = y
        self.moving = True
        self.current_animation = 'walk'

class Hero(Character):
    def __init__(self, x, y):
        # Create simple animations using built-in PGZero images
        animations = {
            'idle': [
                'player_stand',
                'player_stand',  # Just one frame for idle
            ],
            'walk': [
                'player_walk1',
                'player_walk2',
                'player_walk3',
                'player_walk4',
            ]
        }
        super().__init__(x, y, 2, animations)
        
class Enemy(Character):
    def __init__(self, x, y):
        animations = {
            'idle': [
                'enemy_stand',
                'enemy_stand',  # Just one frame for idle
            ],
            'walk': [
                'enemy_walk1',
                'enemy_walk2',
                'enemy_walk3',
                'enemy_walk4',
            ]
        }
        super().__init__(x, y, 1, animations)
        self.patrol_points = [
            (x, y),
            (x + random.randint(2, 5) * TILE_SIZE, y),
            (x + random.randint(2, 5) * TILE_SIZE, y + random.randint(2, 5) * TILE_SIZE),
            (x, y + random.randint(2, 5) * TILE_SIZE)
        ]
        self.current_patrol_point = 0
        
    def update(self):
        super().update()
        
        # Patrol behavior
        if not self.moving and random.random() < 0.01:  # 1% chance to move each frame
            self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
            target = self.patrol_points[self.current_patrol_point]
            self.move_to(target[0], target[1])

class Game:
    def __init__(self):
        self.state = MENU
        self.hero = None
        self.enemies = []
        self.music_on = True
        self.sounds_on = True
        self.game_over = False
        self.background = 'dungeon'
        
    def start_game(self):
        self.state = PLAYING
        self.hero = Hero(WIDTH//2, HEIGHT//2)
        self.enemies = []
        
        # Create some enemies
        for _ in range(5):
            x = random.randint(1, GRID_WIDTH-2) * TILE_SIZE
            y = random.randint(1, GRID_HEIGHT-2) * TILE_SIZE
            self.enemies.append(Enemy(x, y))
            
        if self.music_on:
            music.play('theme')
    
    def update(self):
        if self.state == PLAYING:
            self.hero.update()
            
            for enemy in self.enemies:
                enemy.update()
                
                # Check for collision with hero
                if (abs(enemy.x - self.hero.x) < TILE_SIZE and 
                    abs(enemy.y - self.hero.y) < TILE_SIZE):
                    self.state = GAME_OVER
                    if self.sounds_on:
                        sounds.lose.play()
    
    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game()
            screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (0, 0, 0, 128))
            screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=60)
            screen.draw.text("Click to return to menu", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=30)
    
    def draw_menu(self):
        screen.blit('menu_bg', (0, 0))
        screen.draw.text("ROGUELIKE ADVENTURE", center=(WIDTH//2, 100), fontsize=50)
        
        # Draw buttons
        self.start_button = Rect(WIDTH//2 - 100, 200, 200, 50)
        self.sound_button = Rect(WIDTH//2 - 100, 270, 200, 50)
        self.quit_button = Rect(WIDTH//2 - 100, 340, 200, 50)
        
        screen.draw.filled_rect(self.start_button, (50, 150, 50))
        screen.draw.text("START GAME", center=self.start_button.center, fontsize=30)
        
        sound_text = "SOUND: ON" if self.sounds_on else "SOUND: OFF"
        screen.draw.filled_rect(self.sound_button, (150, 50, 50))
        screen.draw.text(sound_text, center=self.sound_button.center, fontsize=30)
        
        screen.draw.filled_rect(self.quit_button, (150, 50, 150))
        screen.draw.text("QUIT", center=self.quit_button.center, fontsize=30)
    
    def draw_game(self):
        screen.blit(self.background, (0, 0))
        
        # Draw grid (optional, for debugging)
        # for x in range(0, WIDTH, TILE_SIZE):
        #     screen.draw.line((x, 0), (x, HEIGHT), (100, 100, 100))
        # for y in range(0, HEIGHT, TILE_SIZE):
        #     screen.draw.line((0, y), (WIDTH, y), (100, 100, 100))
        
        self.hero.draw()
        for enemy in self.enemies:
            enemy.draw()
    
    def on_mouse_down(self, pos):
        if self.state == MENU:
            if self.start_button.collidepoint(pos):
                self.start_game()
            elif self.sound_button.collidepoint(pos):
                self.sounds_on = not self.sounds_on
                self.music_on = not self.music_on
                if self.music_on:
                    music.play('theme')
                else:
                    music.stop()
            elif self.quit_button.collidepoint(pos):
                exit()
        elif self.state == GAME_OVER:
            self.state = MENU
            music.stop()
    
    def on_mouse_move(self, pos):
        pass
    
    def on_key_down(self, key):
        if self.state == PLAYING:
            # Convert mouse position to grid coordinates
            grid_x = (pos[0] // TILE_SIZE) * TILE_SIZE + TILE_SIZE//2
            grid_y = (pos[1] // TILE_SIZE) * TILE_SIZE + TILE_SIZE//2
            self.hero.move_to(grid_x, grid_y)
            if self.sounds_on:
                sounds.step.play()

# Create game instance
game = Game()

def update():
    game.update()

def draw():
    game.draw()

def on_mouse_down(pos):
    game.on_mouse_down(pos)

def on_mouse_move(pos):
    game.on_mouse_move(pos)

def on_key_down(key):
    game.on_key_down(key)
