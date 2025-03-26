import pygame
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interactive 2D Aquarium")

# Colors
BACKGROUND_COLOR = (0, 105, 148)
EYE_COLOR = (0, 0, 0)
FIN_COLOR = (255, 140, 0)
FOOD_COLOR = (139, 69, 19)
SEAWEED_COLOR = (34, 139, 34)

FISH_TYPES = [
    {"color": (255, 165, 0), "size": (70, 35)},
    {"color": (0, 255, 127), "size": (60, 30)},
    {"color": (255, 0, 0), "size": (75, 38)},
    {"color": (0, 191, 255), "size": (65, 33)},
    {"color": (255, 255, 0), "size": (68, 34)}
]

class Fish:
    def __init__(self):
        fish_type = random.choice(FISH_TYPES)
        self.color = fish_type["color"]
        self.width, self.height = fish_type["size"]
        self.y = random.randint(50, HEIGHT - 100)
        self.speed = random.uniform(2, 4)
        self.following_food = False
        self.target_food = None

        if random.choice([True, False]):
            self.x = -self.width
            self.direction = 1
        else:
            self.x = WIDTH
            self.direction = -1

        self.angle = 0 if self.direction == 1 else 180
        self.returning_to_normal = False  

    def move(self):
        if not self.following_food and not self.returning_to_normal:
            self.x += self.speed * self.direction

            if self.x > WIDTH and self.direction == 1:
                self.x = -self.width
            elif self.x < -self.width and self.direction == -1:
                self.x = WIDTH

    def follow_food(self):
        if self.target_food:
            dx = self.target_food.x - self.x
            dy = self.target_food.y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 5:
                self.angle = math.degrees(math.atan2(dy, dx))
                self.x += math.cos(math.radians(self.angle)) * self.speed * 2  
                self.y += math.sin(math.radians(self.angle)) * self.speed * 2  
            else:
                self.following_food = False
                self.target_food = None  
                self.returning_to_normal = True  

    def return_to_normal(self):
        if self.returning_to_normal:
            target_angle = 0 if self.direction == 1 else 180
            if abs(self.angle - target_angle) > 2:
                self.angle += (target_angle - self.angle) * 0.1
            else:
                self.angle = target_angle
                self.returning_to_normal = False  

    def draw(self):
        fish_body = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        pygame.draw.ellipse(fish_body, self.color, (10, 5, self.width - 20, self.height - 10))

        tail_points = [(5, self.height // 2), (0, self.height - 10), (0, 10)]
        pygame.draw.polygon(fish_body, self.color, tail_points)

        pygame.draw.polygon(fish_body, FIN_COLOR, [(self.width // 3, 2), (self.width // 2, -5), (self.width // 1.8, 10)])
        pygame.draw.polygon(fish_body, FIN_COLOR, [(self.width // 3, self.height - 2), (self.width // 2, self.height + 5), (self.width // 1.8, self.height - 10)])

        eye_x = self.width - 15 if self.direction == 1 else 15
        eye_y = int(self.height * 0.3)
        pygame.draw.circle(fish_body, EYE_COLOR, (eye_x, eye_y), 3)

        rotated_fish = pygame.transform.rotate(fish_body, -self.angle)
        screen.blit(rotated_fish, (self.x, self.y))

class FishFood:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 5
        self.sink_speed = 2  
        self.lifetime = 500  

    def move(self):
        if self.y < HEIGHT - 10:
            self.y += self.sink_speed
        self.lifetime -= 1  

    def draw(self):
        pygame.draw.circle(screen, FOOD_COLOR, (self.x, self.y), self.size)

class Seaweed:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(40, 100)
        self.waving_offset = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.02, 0.05)

    def draw(self):
        for i in range(7):
            offset = math.sin(pygame.time.get_ticks() * self.speed + self.waving_offset) * 5
            pygame.draw.line(screen, SEAWEED_COLOR, 
                             (self.x + offset, HEIGHT - 10 - i * 12), 
                             (self.x + offset + random.randint(-5, 5), HEIGHT - i * 12 - 20), 5)

# Create fish, food, and seaweed
fishes = [Fish() for _ in range(15)]
fish_food = []
seaweed_plants = [Seaweed(random.randint(20, WIDTH - 20)) for _ in range(15)]

# Game loop
running = True
while running:
    screen.fill(BACKGROUND_COLOR)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right-click to drop food
                food = FishFood(event.pos[0], event.pos[1])
                fish_food.append(food)

                for fish in fishes:
                    if not fish.following_food:
                        fish.target_food = food
                        fish.following_food = True

    # Draw seaweed
    for seaweed in seaweed_plants:
        seaweed.draw()

    # Move and draw fish
    for fish in fishes:
        if fish.following_food:
            fish.follow_food()
        elif fish.returning_to_normal:
            fish.return_to_normal()
        else:
            fish.move()
        fish.draw()

    # Move and draw fish food
    for food in fish_food[:]:
        food.move()
        food.draw()

        if food.lifetime <= 0:
            fish_food.remove(food)

        for fish in fishes:
            if fish.target_food == food and abs(fish.x - food.x) < 10 and abs(fish.y - food.y) < 10:
                fish_food.remove(food)
                fish.target_food = None
                fish.following_food = False
                fish.returning_to_normal = True  
                break  

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
