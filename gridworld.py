import pygame
import sys
import math

# --- SETTINGS ---
GRID_SIZE = 5
CELL_SIZE = 100
SIDE_PANEL = 350

WIDTH = GRID_SIZE * CELL_SIZE + SIDE_PANEL
HEIGHT = GRID_SIZE * CELL_SIZE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gridworld MDP Visualization")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Segoe UI", 26)
small_font = pygame.font.SysFont("Segoe UI", 14)

# --- COLORS ---
BG = (30, 30, 40)
GRID = (60, 60, 80)
LINE = (100, 100, 120)
WALL = (90, 90, 110)
GOAL = (80, 200, 120)
AGENT = (80, 160, 255)
TEXT = (240, 240, 240)
CURR = (255, 255, 120)
PREV = (100, 140, 255)
TELEPORT = (180, 80, 200)

# --- ENVIRONMENT ---
class Gridworld:
    def __init__(self):
        self.start = (0, 0)
        self.goal = (4, 4)

        # UPDATED walls
        self.walls = {(2,1), (2,2), (3,3)}

        # teleport
        self.A = (0,1)
        self.A_prime = (4,1)

        self.B = (0,3)
        self.B_prime = (2,3)

        self.reset()

    def reset(self):
        self.state = self.start
        self.prev_state = None
        self.last_action = None
        self.last_reward = 0
        self.total_return = 0
        self.steps = 0
        self.transition_progress = 0

    def step(self, action):
        self.prev_state = self.state
        row, col = self.state

        # TELEPORT
        if self.state == self.A:
            next_state = self.A_prime
            reward = 10
            valid = True

        elif self.state == self.B:
            next_state = self.B_prime
            reward = 5
            valid = True

        else:
            new_row, new_col = row, col

            if action == "up": new_row -= 1
            elif action == "down": new_row += 1
            elif action == "left": new_col -= 1
            elif action == "right": new_col += 1

            # boundary
            if not (0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE):
                next_state = (row, col)
                reward = 0
                valid = False

            elif (new_row, new_col) in self.walls:
                next_state = (row, col)
                reward = 0
                valid = False

            else:
                next_state = (new_row, new_col)

                if next_state == self.goal:
                    reward = 10
                else:
                    reward = -1

                valid = True

        self.state = next_state
        self.last_action = action
        self.last_reward = reward

        # ✅ ONLY count valid moves
        if valid:
            self.total_return += reward
            self.steps += 1

        self.transition_progress = 1


env = Gridworld()

visual_pos = [0, 0]

def lerp(a, b, t):
    return a + (b - a) * t

# --- DRAW ---
def draw():
    screen.fill(BG)

    # grid
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = j * CELL_SIZE
            y = i * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            color = GRID

            if (i,j) in env.walls:
                color = WALL
            elif (i,j) == env.goal:
                color = GOAL
            elif (i,j) in [env.A, env.B]:
                color = TELEPORT

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, LINE, rect, 2)

            screen.blit(small_font.render(f"{i},{j}", True, TEXT), (x+5, y+5))

            if (i,j) == env.goal:
                screen.blit(small_font.render("Goal", True, TEXT), (x+25, y+40))
            if (i,j) == env.A:
                screen.blit(small_font.render("A", True, TEXT), (x+40, y+40))
            if (i,j) == env.B:
                screen.blit(small_font.render("B", True, TEXT), (x+40, y+40))

    # prev state
    if env.prev_state:
        ps = env.prev_state
        pygame.draw.rect(screen, PREV,
                         (ps[1]*CELL_SIZE, ps[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    # current state
    cs = env.state
    pygame.draw.rect(screen, CURR,
                     (cs[1]*CELL_SIZE, cs[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE), 6)

    # smooth agent
    target_x = cs[1]*CELL_SIZE + CELL_SIZE//2
    target_y = cs[0]*CELL_SIZE + CELL_SIZE//2

    visual_pos[0] = lerp(visual_pos[0], target_x, 0.2)
    visual_pos[1] = lerp(visual_pos[1], target_y, 0.2)

    pygame.draw.circle(screen, AGENT,
                       (int(visual_pos[0]), int(visual_pos[1])), CELL_SIZE//3)

    # arrow
    if env.prev_state and env.transition_progress > 0:
        start = (
            env.prev_state[1]*CELL_SIZE + CELL_SIZE//2,
            env.prev_state[0]*CELL_SIZE + CELL_SIZE//2
        )
        end = (
            env.state[1]*CELL_SIZE + CELL_SIZE//2,
            env.state[0]*CELL_SIZE + CELL_SIZE//2
        )

        t = 1 - env.transition_progress
        current = (
            start[0] + (end[0]-start[0])*t,
            start[1] + (end[1]-start[1])*t
        )

        pygame.draw.line(screen, (255,255,255), start, current, 5)
        pygame.draw.circle(screen, (255,255,255), (int(current[0]), int(current[1])), 6)

    # --- SIDE PANEL ---
    panel_x = GRID_SIZE * CELL_SIZE
    pygame.draw.rect(screen, (20,20,30), (panel_x, 0, SIDE_PANEL, HEIGHT))

    x = panel_x + 20
    y = 20
    gap = 40

    screen.blit(font.render("MDP Info", True, TEXT), (x, y))
    y += 50

    screen.blit(font.render(f"State S: {env.state}", True, TEXT), (x, y))
    screen.blit(font.render(f"Action A: {env.last_action}", True, TEXT), (x, y+gap))
    screen.blit(font.render(f"Reward R_t: {env.last_reward}", True, TEXT), (x, y+2*gap))
    screen.blit(font.render(f"Return G: {env.total_return}", True, TEXT), (x, y+3*gap))
    screen.blit(font.render(f"Steps: {env.steps}", True, TEXT), (x, y+4*gap))

    pygame.display.flip()


# init
visual_pos[0] = env.state[1]*CELL_SIZE + CELL_SIZE//2
visual_pos[1] = env.state[0]*CELL_SIZE + CELL_SIZE//2

# loop
while True:
    clock.tick(60)

    if env.transition_progress > 0:
        env.transition_progress -= 0.06

    draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                env.step("up")
            elif event.key == pygame.K_DOWN:
                env.step("down")
            elif event.key == pygame.K_LEFT:
                env.step("left")
            elif event.key == pygame.K_RIGHT:
                env.step("right")
            elif event.key == pygame.K_r:
                env.reset()