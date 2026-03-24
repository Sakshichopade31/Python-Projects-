"""
Fruit Ninja Game - Fixed Version
Python 3 + Pygame
"""

import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
PINK = (255, 192, 203)

class Fruit:
    """Simple Fruit Class"""
    def __init__(self, x, y, fruit_type="apple"):
        self.x = x
        self.y = y
        self.fruit_type = fruit_type
        
        # Physics
        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-12, -8)
        self.gravity = 0.4
        
        # Set properties based on fruit type
        if fruit_type == "apple":
            self.color = RED
            self.points = 10
            self.radius = 20
            self.emoji = "🍎"
        elif fruit_type == "banana":
            self.color = YELLOW
            self.points = 15
            self.radius = 18
            self.emoji = "🍌"
        elif fruit_type == "orange":
            self.color = ORANGE
            self.points = 12
            self.radius = 20
            self.emoji = "🍊"
        elif fruit_type == "strawberry":
            self.color = RED
            self.points = 20
            self.radius = 15
            self.emoji = "🍓"
        elif fruit_type == "bomb":
            self.color = BLACK
            self.points = -50
            self.radius = 22
            self.emoji = "💣"
            
        self.slashed = False
        self.active = True
        
    def update(self):
        """Update fruit position"""
        if not self.active:
            return
            
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += self.gravity
        
        # Screen boundary check
        if self.y > SCREEN_HEIGHT + 50 or self.y < -50:
            self.active = False
            
    def draw(self, screen):
        """Draw fruit"""
        if not self.active:
            return
            
        # Draw fruit circle
        if self.fruit_type == "bomb":
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)
            # Draw fuse
            pygame.draw.line(screen, BROWN, 
                           (self.x + 10, self.y - 10), 
                           (self.x + 20, self.y - 20), 3)
            # Draw spark
            spark_x = self.x + 20
            spark_y = self.y - 20
            pygame.draw.circle(screen, ORANGE, (int(spark_x), int(spark_y)), 4)
        else:
            # Normal fruit
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            # Highlight
            pygame.draw.circle(screen, WHITE, (int(self.x - 5), int(self.y - 5)), 5)
            # Leaf
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y - self.radius - 2)), 5)
            
        # Draw emoji
        try:
            font = pygame.font.SysFont('segoeuiemojifont', 30)
            text = font.render(self.emoji, True, BLACK)
            screen.blit(text, (self.x - 15, self.y - 15))
        except:
            pass
            
    def check_collision(self, x1, y1, x2, y2):
        """Check if line intersects with fruit"""
        if not self.active or self.slashed:
            return False
            
        # Distance from point to line
        line_len = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if line_len == 0:
            return False
            
        # Calculate distance from fruit to line
        t = ((self.x - x1)*(x2 - x1) + (self.y - y1)*(y2 - y1)) / (line_len**2)
        t = max(0, min(1, t))
        
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        dist = math.sqrt((self.x - proj_x)**2 + (self.y - proj_y)**2)
        
        return dist <= self.radius

class Blade:
    """Slash Trail"""
    def __init__(self):
        self.positions = []
        self.max_positions = 15
        self.active = False
        
    def add_position(self, x, y):
        """Add new position to trail"""
        self.positions.append((x, y))
        if len(self.positions) > self.max_positions:
            self.positions.pop(0)
        self.active = True
        
    def clear(self):
        """Clear trail"""
        self.positions = []
        self.active = False
        
    def draw(self, screen):
        """Draw blade trail"""
        if len(self.positions) < 2:
            return
            
        for i in range(len(self.positions) - 1):
            alpha = int(255 * (i / len(self.positions)))
            width = max(1, i // 2)
            
            start = self.positions[i]
            end = self.positions[i + 1]
            
            pygame.draw.line(screen, WHITE, start, end, width)

class FruitNinja:
    """Main Game Class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Fruit Ninja")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Game variables
        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.game_state = "menu"  # menu, playing, gameover
        
        # Objects
        self.fruits = []
        self.blade = Blade()
        
        # Timing
        self.spawn_timer = 0
        self.spawn_delay = 45  # Frames between spawns
        
        # Mouse tracking
        self.mouse_down = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        # Load high score
        self.load_high_score()
        
    def load_high_score(self):
        """Load high score from file"""
        try:
            with open("fruitninja_high.txt", "r") as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0
            
    def save_high_score(self):
        """Save high score to file"""
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open("fruitninja_high.txt", "w") as f:
                    f.write(str(self.high_score))
            except:
                pass
                
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "menu":
                        self.game_state = "playing"
                        self.reset_game()
                    elif self.game_state == "gameover":
                        self.game_state = "menu"
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_down = True
                    self.blade.clear()
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False
                    self.blade.clear()
                    
        return True
        
    def reset_game(self):
        """Reset game for new round"""
        self.score = 0
        self.lives = 20
        self.fruits = []
        self.spawn_timer = 0
        
    def spawn_fruit(self):
        """Spawn new fruit"""
        x = random.randint(200, SCREEN_WIDTH - 200)
        y = SCREEN_HEIGHT - 50
        
        # Decide fruit type
        if random.random() < 0.2:  # 20% chance of bomb
            fruit_type = "bomb"
        else:
            fruit_type = random.choice(["apple", "banana", "orange", "strawberry"])
            
        self.fruits.append(Fruit(x, y, fruit_type))
        
    def update(self):
        """Update game logic"""
        if self.game_state != "playing":
            return
            
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Handle blade
        if self.mouse_down:
            self.blade.add_position(mouse_x, mouse_y)
            
            # Check for fruit collision
            if self.last_mouse_x != 0 and self.last_mouse_y != 0:
                for fruit in self.fruits[:]:
                    if fruit.check_collision(self.last_mouse_x, self.last_mouse_y, 
                                           mouse_x, mouse_y):
                        self.slash_fruit(fruit)
        else:
            self.blade.clear()
            
        # Update fruits
        for fruit in self.fruits[:]:
            fruit.update()
            
            # Remove inactive fruits
            if not fruit.active:
                if fruit.fruit_type != "bomb" and not fruit.slashed:
                    self.lives -= 1  # Missed fruit costs life
                self.fruits.remove(fruit)
                
        # Spawn new fruits
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_fruit()
            self.spawn_timer = 0
            
        # Check game over
        if self.lives <= 0:
            self.game_state = "gameover"
            self.save_high_score()
            
        # Store last mouse position
        self.last_mouse_x, self.last_mouse_y = mouse_x, mouse_y
        
    def slash_fruit(self, fruit):
        """Handle fruit slash"""
        if fruit.slashed:
            return
            
        fruit.slashed = True
        fruit.active = False
        
        if fruit.fruit_type == "bomb":
            self.lives = 0  # Bomb = instant game over
        else:
            self.score += fruit.points
            
    def draw_background(self):
        """Draw gradient background"""
        for y in range(SCREEN_HEIGHT):
            color_val = 50 + int((y / SCREEN_HEIGHT) * 100)
            color = (color_val // 2, color_val // 3, color_val)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
            
    def draw(self):
        """Draw everything"""
        # Draw background
        self.draw_background()
        
        # Draw fruits
        for fruit in self.fruits:
            fruit.draw(self.screen)
            
        # Draw blade
        self.blade.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw menus
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "gameover":
            self.draw_gameover()
            
        pygame.display.flip()
        
    def draw_ui(self):
        """Draw user interface"""
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # High Score
        high_text = self.font_small.render(f"High: {self.high_score}", True, YELLOW)
        self.screen.blit(high_text, (20, 70))
        
        # Lives
        lives_text = self.font_small.render(f"Lives: {'❤️' * self.lives}", True, RED)
        self.screen.blit(lives_text, (20, 110))
        
    def draw_menu(self):
        """Draw main menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("FRUIT NINJA", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "Drag mouse to slash fruits!",
            "Avoid bombs!",
            "",
            "Press SPACE to start",
            "Press ESC to quit"
        ]
        
        y = 300
        for instruction in instructions:
            text = self.font_medium.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y))
            self.screen.blit(text, text_rect)
            y += 50
            
        # Fruit examples
        fruits = ["🍎", "🍌", "🍊", "🍓", "💣"]
        x = SCREEN_WIDTH//2 - 150
        for fruit in fruits:
            try:
                font = pygame.font.SysFont('segoeuiemojifont', 50)
                text = font.render(fruit, True, WHITE)
                self.screen.blit(text, (x, 500))
                x += 80
            except:
                pass
                
    def draw_gameover(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        gameover = self.font_large.render("GAME OVER", True, RED)
        go_rect = gameover.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(gameover, go_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 350))
        self.screen.blit(score_text, score_rect)
        
        # High score message
        if self.score >= self.high_score:
            new_text = self.font_medium.render("NEW HIGH SCORE!", True, YELLOW)
            new_rect = new_text.get_rect(center=(SCREEN_WIDTH//2, 400))
            self.screen.blit(new_text, new_rect)
            
        # Restart instruction
        restart = self.font_small.render("Press SPACE for Menu", True, WHITE)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH//2, 500))
        self.screen.blit(restart, restart_rect)
        
    def run(self):
        """Main game loop"""
        running = True
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update game
            self.update()
            
            # Draw everything
            self.draw()
            
            # Control frame rate
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = FruitNinja()
    game.run()