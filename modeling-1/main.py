import pygame
import math
import sys

WIDTH, HEIGHT = 1200, 1000
FPS = 60
MU = 0.4  
MIN_VELOCITY = 2.0  

WHITE = (255, 255, 255)
BLACK = (20, 30, 20) 

COLOR_DATA = [
    (WHITE, "Биток"),
    ((255, 50, 50), "Красный"),
    ((50, 255, 50), "Зеленый"),
    ((50, 50, 255), "Синий"),
    ((255, 255, 50), "Желтый"),
    ((255, 50, 255), "Розовый"),
    ((50, 255, 255), "Голубой"),
    ((255, 128, 0), "Оранж"),
    ((128, 0, 255), "Фиолет"),
    ((150, 75, 0), "Корич"),
    ((180, 180, 180), "Серый")
]

class Ball:
    def __init__(self, x, y, vx, vy, radius, color, name):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.radius = radius
        self.color = color
        self.name = name
        self.path = [(x, y)]
        self.total_distance = 0.0

    def update(self, dt):
        speed = math.hypot(self.vx, self.vy)
        if speed < MIN_VELOCITY:
            self.vx = self.vy = 0
            return
        prev_pos = (self.x, self.y)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.total_distance += math.hypot(self.x - prev_pos[0], self.y - prev_pos[1])
        if math.hypot(self.path[-1][0] - self.x, self.path[-1][1] - self.y) > 5:
            self.path.append((self.x, self.y))
            if len(self.path) > 100: self.path.pop(0)
        decay = math.exp(-MU * dt)
        self.vx *= decay
        self.vy *= decay

    def draw(self, screen):
        if len(self.path) > 1:
            pygame.draw.lines(screen, self.color, False, self.path, 1)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x - 5), int(self.y - 5)), 4)

def handle_collisions(balls):
    for b in balls:
        if b.x - b.radius < 0: b.x, b.vx = b.radius, abs(b.vx)
        if b.x + b.radius > WIDTH: b.x, b.vx = WIDTH - b.radius, -abs(b.vx)
        if b.y - b.radius < 0: b.y, b.vy = b.radius, abs(b.vy)
        if b.y + b.radius > HEIGHT: b.y, b.vy = HEIGHT - b.radius, -abs(b.vy)
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            b1, b2 = balls[i], balls[j]
            dx, dy = b2.x - b1.x, b2.y - b1.y
            dist = math.hypot(dx, dy)
            if dist < b1.radius + b2.radius:
                nx, ny = dx/dist, dy/dist
                overlap = (b1.radius + b2.radius) - dist
                b1.x -= nx * overlap/2
                b1.y -= ny * overlap/2
                b2.x += nx * overlap/2
                b2.y += ny * overlap/2
                v1n = nx * b1.vx + ny * b1.vy
                v1t = -ny * b1.vx + nx * b1.vy
                v2n = nx * b2.vx + ny * b2.vy
                v2t = -ny * b2.vx + nx * b2.vy
                b1.vx, b2.vx = v2n * nx - v1t * ny, v1n * nx - v2t * ny
                b1.vy, b2.vy = v2n * ny + v1t * nx, v1n * ny + v2t * nx

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 13)
    balls = []
    
    # Биток
    balls.append(Ball(200, 300, 0, 0, 15, COLOR_DATA[0][0], COLOR_DATA[0][1]))
    
    # Пирамида из 10 шаров (ряды: 1, 2, 3, 4)
    start_x, start_y = 450, 300
    ball_idx = 1
    for col in range(4):
        for row in range(col + 1):
            bx = start_x + col * 27
            by = start_y + (row - col/2.0) * 31
            balls.append(Ball(bx, by, 0, 0, 15, COLOR_DATA[ball_idx][0], COLOR_DATA[ball_idx][1]))
            ball_idx += 1

    cue_ball = balls[0]
    aiming = False
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if math.hypot(cue_ball.x - mouse_pos[0], cue_ball.y - mouse_pos[1]) < 30: aiming = True
            if event.type == pygame.MOUSEBUTTONUP and aiming:
                aiming = False
                cue_ball.vx = (cue_ball.x - mouse_pos[0]) * 6
                cue_ball.vy = (cue_ball.y - mouse_pos[1]) * 6
                cue_ball.path = [(cue_ball.x, cue_ball.y)]

        for b in balls: b.update(dt)
        handle_collisions(balls)
        screen.fill(BLACK)
        
        for i, b in enumerate(balls):
            s = math.hypot(b.vx, b.vy)
            txt = font.render(f"{b.name.ljust(8)} | P:{int(b.total_distance)} | V:{int(s)}", True, (120, 140, 120))
            screen.blit(txt, (10, 10 + i * 16))

        if aiming:
            pygame.draw.line(screen, (200, 50, 50), (int(cue_ball.x), int(cue_ball.y)), mouse_pos, 2)
        for b in balls: b.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
