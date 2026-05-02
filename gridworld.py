import pygame
import sys

# --- SETTINGS ---
GRID_SIZE = 5
CELL_SIZE = 100
SIDE_PANEL = 350

WIDTH = GRID_SIZE * CELL_SIZE + SIDE_PANEL
HEIGHT = GRID_SIZE * CELL_SIZE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gridworld MDP")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Segoe UI", 26)
small_font = pygame.font.SysFont("Segoe UI", 14)

# --- COLORS ---
BG = (30, 30, 40)
GRID = (60, 60, 80)
LINE = (100, 100, 120)
WALL = (90, 90, 110)
GOAL = (80, 200, 120)
TELEPORT = (180, 80, 200)
AGENT = (80, 160, 255)
TEXT = (240, 240, 240)
CURR = (255, 255, 120)
PREV = (100, 140, 255)

# --- ENVIRONMENT ---
class Gridworld:
    def __init__(self):
        self.start = (0, 0)

        # FINAL USER CONFIG
        self.goal = (4, 2)
        self.A = (0, 2)
        self.B = (4, 4)

        self.walls = {
            (1, 1),
            (1, 3),
            (3, 2),
            (3, 1)
        }

        self.reset()

    def reset(self):
        self.state = self.start
        self.prev_state = None
        self.last_action = None
        self.last_reward = 0
        self.total_return = 0
        self.steps = 0
        self.transition_progress = 0
        self.done = False

        self.teleporting = False
        self.teleport_from = None
        self.teleport_to = None

    def step(self, action):
        if self.done:
            return

        self.prev_state = self.state
        row, col = self.state

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

        # wall
        elif (new_row, new_col) in self.walls:
            next_state = (row, col)
            reward = 0
            valid = False

        else:
            next_state = (new_row, new_col)

            # TELEPORT
            if next_state == self.A:
                self.teleporting = True
                self.teleport_from = self.A
                self.teleport_to = self.B

                next_state = self.B
                reward = 10

            elif next_state == self.goal:
                reward = 10
                self.done = True

            else:
                reward = -1

            valid = True

        self.state = next_state
        self.last_action = action
        self.last_reward = reward

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

    # GRID
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = j * CELL_SIZE
            y = i * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            color = GRID

            if (i, j) in env.walls:
                color = WALL
            elif (i, j) == env.goal:
                color = GOAL
            elif (i, j) == env.A:
                color = TELEPORT
            elif (i, j) == env.B:
                color = TELEPORT

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, LINE, rect, 2)

            screen.blit(small_font.render(f"{i},{j}", True, TEXT), (x + 5, y + 5))

            if (i, j) == env.goal:
                screen.blit(small_font.render("Goal", True, TEXT), (x + 25, y + 40))
            if (i, j) == env.A:
                screen.blit(small_font.render("A→B", True, TEXT), (x + 15, y + 40))
            if (i, j) == env.B:
                screen.blit(small_font.render("B", True, TEXT), (x + 40, y + 40))

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

    # teleport animation
    if env.teleporting:
        start = (
            env.teleport_from[1]*CELL_SIZE + CELL_SIZE//2,
            env.teleport_from[0]*CELL_SIZE + CELL_SIZE//2
        )
        end = (
            env.teleport_to[1]*CELL_SIZE + CELL_SIZE//2,
            env.teleport_to[0]*CELL_SIZE + CELL_SIZE//2
        )

        pygame.draw.line(screen, (200,100,255), start, end, 6)
        pygame.draw.circle(screen, (255,255,255), start, 12)
        pygame.draw.circle(screen, (255,255,255), end, 12)

    # SIDE PANEL
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

    # END SCREEN
    if env.done:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))

        msg1 = font.render("GOAL REACHED!", True, (255,255,255))
        msg2 = font.render("Press R to Restart", True, (255,255,255))
        msg3 = font.render("Press ESC to Quit", True, (255,255,255))

        screen.blit(msg1, (WIDTH//2 - 120, HEIGHT//2 - 60))
        screen.blit(msg2, (WIDTH//2 - 150, HEIGHT//2))
        screen.blit(msg3, (WIDTH//2 - 130, HEIGHT//2 + 50))

    pygame.display.flip()


# init
visual_pos[0] = env.state[1]*CELL_SIZE + CELL_SIZE//2
visual_pos[1] = env.state[0]*CELL_SIZE + CELL_SIZE//2

# LOOP
while True:
    clock.tick(60)

    if env.transition_progress > 0:
        env.transition_progress -= 0.06

    if env.teleporting and env.transition_progress <= 0:
        env.teleporting = False

    draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                env.reset()

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            elif not env.done:
                if event.key == pygame.K_UP:
                    env.step("up")
                elif event.key == pygame.K_DOWN:
                    env.step("down")
                elif event.key == pygame.K_LEFT:
                    env.step("left")
                elif event.key == pygame.K_RIGHT:
                    env.step("right")