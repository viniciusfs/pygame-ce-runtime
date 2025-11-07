import sys
import pygame as pg
import logging
from datetime import datetime

pg.init()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("pygame-ce runtime")
        self.clock = pg.time.Clock()
        self.running = True

        self.font = pg.font.Font(None, 36)
        self.player_pos = [SCREEN_WIDTH//2, SCREEN_HEIGHT//2]

        pg.joystick.init()
        self.joystick = None
        self.joystick_num_buttons = None

        joystick_count = pg.joystick.get_count()
        logger.info(f"Detected {joystick_count} joystick(s)")

        if joystick_count > 0:
            self.joystick = pg.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_num_buttons = self.joystick.get_numbuttons()
            logger.info(f"Initialized joystick: {self.joystick.get_name()}")
            logger.info(f"Joystick buttons: {self.joystick_num_buttons}")
            logger.info(f"Joystick axes: {self.joystick.get_numaxes()}")
            logger.info(f"Joystick hats: {self.joystick.get_numhats()}")
        else:
            logger.warning("No joystick detected")

        pg.mouse.set_visible(False)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                logger.info("QUIT event received")
                self.running = False
            elif event.type == pg.KEYDOWN:
                logger.debug(f"Key pressed: {pg.key.name(event.key)}")
                if event.key == pg.K_ESCAPE:
                    logger.info("ESC key pressed - exiting game")
                    self.running = False
            elif event.type == pg.JOYBUTTONDOWN:
                logger.debug(f"Joystick button {event.button} pressed")
                if event.button == 9:
                    logger.info("Select button pressed - exiting game")
                    self.running = False
                elif event.button == 10:
                    logger.info("Start button pressed - exiting game")
                    self.running = False
                else:
                    logger.debug(f"Action button {event.button} pressed")

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.player_pos[0] = max(20, self.player_pos[0] - 5)
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.player_pos[0] = min(SCREEN_WIDTH - 20, self.player_pos[0] + 5)
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.player_pos[1] = max(20, self.player_pos[1] - 5)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.player_pos[1] = min(SCREEN_HEIGHT - 20, self.player_pos[1] + 5)

        # Joystick controls
        if self.joystick:
            # D-pad movement
            hat = self.joystick.get_hat(0)
            if hat[0] == -1:  # Left
                logger.debug("D-pad LEFT pressed")
                self.player_pos[0] = max(20, self.player_pos[0] - 5)
            elif hat[0] == 1:  # Right
                logger.debug("D-pad RIGHT pressed")
                self.player_pos[0] = min(SCREEN_WIDTH - 20, self.player_pos[0] + 5)
            if hat[1] == 1:  # Up
                logger.debug("D-pad UP pressed")
                self.player_pos[1] = max(20, self.player_pos[1] - 5)
            elif hat[1] == -1:  # Down
                logger.debug("D-pad DOWN pressed")
                self.player_pos[1] = min(SCREEN_HEIGHT - 20, self.player_pos[1] + 5)

            # Analog stick movement (left stick)
            x_axis = self.joystick.get_axis(0)
            y_axis = self.joystick.get_axis(1)

            # Apply deadzone to prevent drift
            deadzone = 0.2
            if abs(x_axis) > deadzone:
                logger.debug(f"Analog stick X: {x_axis:.2f}")
                self.player_pos[0] += x_axis * 5
                self.player_pos[0] = max(20, min(SCREEN_WIDTH - 20, self.player_pos[0]))
            if abs(y_axis) > deadzone:
                logger.debug(f"Analog stick Y: {y_axis:.2f}")
                self.player_pos[1] += y_axis * 5
                self.player_pos[1] = max(20, min(SCREEN_HEIGHT - 20, self.player_pos[1]))

    def update(self):
        pass

    def draw(self):
        self.screen.fill(BLACK)

        title_text = self.font.render("pygame-ce runtime", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)

        small_font = pg.font.Font(None, 24)
        instruction_text = small_font.render("Use D-Pad, Analog Stick or WASD to move", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(instruction_text, instruction_rect)

        if self.joystick:
            joy_text = small_font.render(f"Controller: {self.joystick_num_buttons} buttons", True, GREEN)
        else:
            joy_text = small_font.render("No controller detected", True, RED)
        joy_rect = joy_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(joy_text, joy_rect)

        pg.draw.circle(self.screen, RED, self.player_pos, 20)

        pg.display.flip()

    def run(self):
        logger.info("Game started")
        logger.info(f"Screen resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        logger.info(f"Target FPS: {FPS}")

        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        logger.info("Game ended")
        pg.quit()
        sys.exit()

# Joystick: Anbernic RG35XX-H Controller
# Button mapping:
#   Vol Down = 1
#   Vol Up = 2
#   A = 3
#   B = 4
#   Y = 5
#   X = 6
#   L1 = 7
#   R2 = 8
#   Select = 9
#   Start = 10
#   F  = 11
#   L3 = 12
#   L2 = 13
#   R2 = 14
#   R3 = 15
#   F  = 16
