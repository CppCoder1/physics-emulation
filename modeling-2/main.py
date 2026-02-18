import pygame
import math
import random

WIDTH, HEIGHT = 1200, 800
FPS = 60

BLACK = (10, 10, 10)
WHITE = (240, 240, 240)
RED = (255, 80, 80)
BLUE = (80, 80, 255)
YELLOW = (255, 255, 0)

K = 10000
CHARGE_VAL = 10
STEP_SIZE = 10
MAX_STEPS = 500

SHOW_VECTORS = True
SHOW_LINES = True
SHOW_PARTICLES = True

class Charge:
    def __init__(self, x, y, q):
        self.x = x
        self.y = y
        self.q = q
        self.radius = 10
        self.color = RED if q > 0 else BLUE

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        font = pygame.font.SysFont("Arial", 20, bold=True)
        text = "+" if self.q > 0 else "-"
        text_surf = font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surf, text_rect)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.life = random.randint(100, 300)

    def update(self, field_func, dt):
        ex, ey = field_func(self.x, self.y)
        self.vx = (self.vx + ex * 0.5) * 0.90
        self.vy = (self.vy + ey * 0.5) * 0.90
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= 1

    def draw(self, surface):
        alpha = min(255, self.life * 2)
        s = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*YELLOW, alpha), (2, 2), 2)
        surface.blit(s, (self.x - 2, self.y - 2))

def calculate_field(x, y, charges):
    Ex, Ey = 0, 0
    for charge in charges:
        dx = x - charge.x
        dy = y - charge.y
        dist_sq = dx*dx + dy*dy
        if dist_sq < 100: 
            dist_sq = 100 
        dist = math.sqrt(dist_sq)
        E = K * charge.q / dist_sq
        Ex += E * (dx / dist)
        Ey += E * (dy / dist)
    return Ex, Ey

def draw_field_vectors(surface, charges):
    spacing = 40
    for y in range(0, HEIGHT, spacing):
        for x in range(0, WIDTH, spacing):
            ex, ey = calculate_field(x, y, charges)
            mag = math.sqrt(ex*ex + ey*ey)
            if mag == 0: continue

            scale = 15
            ex_norm = (ex / mag) * scale
            ey_norm = (ey / mag) * scale
            intensity = min(255, int(mag * 20))
            color = (intensity, intensity, intensity)
            start_pos = (x, y)
            end_pos = (x + ex_norm, y + ey_norm)
            pygame.draw.line(surface, color, start_pos, end_pos, 1)

def draw_field_lines(surface, charges):
    start_points = []
    n_lines = 16
    for charge in charges:
        if charge.q > 0:
            for i in range(n_lines):
                angle = (2 * math.pi / n_lines) * i
                sx = charge.x + math.cos(angle) * 15
                sy = charge.y + math.sin(angle) * 15
                start_points.append((sx, sy, 1))

    for (sx, sy, direction) in start_points:
        points = [(sx, sy)]
        curr_x, curr_y = sx, sy
        for _ in range(MAX_STEPS):
            ex, ey = calculate_field(curr_x, curr_y, charges)
            mag = math.sqrt(ex*ex + ey*ey)
            if mag == 0: break
            
            dx = (ex / mag) * STEP_SIZE * direction
            dy = (ey / mag) * STEP_SIZE * direction
            curr_x += dx
            curr_y += dy
            
            if not (0 <= curr_x <= WIDTH and 0 <= curr_y <= HEIGHT):
                break
                
            hit_charge = False
            for c in charges:
                dist_sq = (curr_x - c.x)**2 + (curr_y - c.y)**2
                if dist_sq < c.radius**2 + 100:
                    hit_charge = True
                    break
            if hit_charge:
                points.append((curr_x, curr_y))
                break
            points.append((curr_x, curr_y))
            
        if len(points) > 1:
            pygame.draw.lines(surface, (100, 200, 100), False, points, 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Electric Field Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)

    charges = [
        Charge(WIDTH/2 - 100, HEIGHT/2, CHARGE_VAL),
        Charge(WIDTH/2 + 100, HEIGHT/2, -CHARGE_VAL)
    ]
    particles = []
    
    global SHOW_VECTORS, SHOW_LINES, SHOW_PARTICLES

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if event.button == 1:
                    charges.append(Charge(mx, my, CHARGE_VAL))
                elif event.button == 3:
                    charges.append(Charge(mx, my, -CHARGE_VAL))
                elif event.button == 2:
                    charges = [c for c in charges if (c.x-mx)**2 + (c.y-my)**2 > 400]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    charges = []
                elif event.key == pygame.K_1:
                    SHOW_VECTORS = not SHOW_VECTORS
                elif event.key == pygame.K_2:
                    SHOW_LINES = not SHOW_LINES
                elif event.key == pygame.K_3:
                    SHOW_PARTICLES = not SHOW_PARTICLES

        if SHOW_PARTICLES and len(charges) > 0 and len(particles) < 100:
            if random.random() < 0.2:
                particles.append(Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        
        for p in particles:
            p.update(lambda x, y: calculate_field(x, y, charges), 1.0)
        particles = [p for p in particles if p.life > 0 and 0 <= p.x <= WIDTH and 0 <= p.y <= HEIGHT]

        screen.fill(BLACK)

        if len(charges) > 0:
            if SHOW_VECTORS:
                draw_field_vectors(screen, charges)
            if SHOW_LINES:
                draw_field_lines(screen, charges)
        
        if SHOW_PARTICLES:
            for p in particles:
                p.draw(screen)

        for charge in charges:
            charge.draw(screen)

        ui_text = [
            f"Charges: {len(charges)}",
            "LMB: + | RMB: - | Wheel: Del",
            "R: Reset",
            f"1: Vectors ({'ON' if SHOW_VECTORS else 'OFF'})",
            f"2: Lines ({'ON' if SHOW_LINES else 'OFF'})",
            f"3: Particles ({'ON' if SHOW_PARTICLES else 'OFF'})"
        ]
        
        for i, line in enumerate(ui_text):
            text_surf = font.render(line, True, WHITE)
            screen.blit(text_surf, (10, 10 + i * 20))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
