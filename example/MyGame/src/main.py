import sys
import pygame as pg
import logging

from datetime import datetime


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-7s %(message)s',
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
        pg.init()
        logger.debug(f"Pygame {pg.version.ver} initialized!")
        logger.debug(f"System total memory: {pg.system.get_total_ram()}MiB")
        logger.debug(f"SDL version: {pg.version.SDL}")

        pg.mixer.init()
        logger.debug(f"SDL mixer version: {pg.mixer.get_sdl_mixer_version()}")

        self.screen = self._init_screen()
        self.joystick = self._init_joystick()

        self.system_info = {
            "versions": {
                "pygame": pg.version.ver,
                "sdl": pg.version.SDL,
                "sdl_mixer": pg.mixer.get_sdl_mixer_version()
            },
            "system": {
                "total_memory": pg.system.get_total_ram()
            },
            "joystick": {
                "count": pg.joystick.get_count() if self.joystick else None,
                "buttons": self.joystick.get_numbuttons() if self.joystick else None,
                "axes": self.joystick.get_numaxes() if self.joystick else None,
                "hats": self.joystick.get_numhats() if self.joystick else None,
                "balls": self.joystick.get_numballs() if self.joystick else None,
                "name": self.joystick.get_name() if self.joystick else None
            },
            "display": {
                "driver": pg.display.get_driver(),
                "num_displays": pg.display.get_num_displays(),
                "available_modes": pg.display.list_modes(),
                "current_mode": self.screen.get_size()
            }
        }

        self.clock = pg.time.Clock()
        self.running = True
        self.player_pos = [SCREEN_WIDTH//2, SCREEN_HEIGHT//2]
        self.last_pressed = None

    def _init_screen(self):
        pg.display.init()
        pg.display.set_caption("pygame-ce runtime")

        logger.debug(f"Display driver: {pg.display.get_driver()}")
        logger.debug(f"Number of displays: {pg.display.get_num_displays()}")
        logger.debug(f"Available display modes: {pg.display.list_modes()}")

        return pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def _init_joystick(self):
        joystick = None
        pg.joystick.init()
        logger.debug(f"Detected {pg.joystick.get_count()} joystick(s)")

        if pg.joystick.get_count() > 0:
            joystick = pg.joystick.Joystick(0)
            logger.debug(f"Initialized joystick: {joystick.get_name()}")
            logger.debug(f"Joystick buttons: {joystick.get_numbuttons()}")
            logger.debug(f"Joystick trackballs: {joystick.get_numballs()}")
            logger.debug(f"Joystick axes: {joystick.get_numaxes()}")
            logger.debug(f"Joystick hats: {joystick.get_numhats()}")

        return joystick

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                logger.info("Quit event received, exiting...")
                self.running = False
            elif event.type == pg.KEYDOWN:
                logger.debug(f"Key pressed: {pg.key.name(event.key)}")
                if event.key == pg.K_ESCAPE:
                    logger.info("ESC key pressed, exiting...")
                    self.running = False
            elif event.type == pg.JOYBUTTONDOWN:
                logger.debug(f"Joystick button {event.button} pressed")
                self.last_pressed = event.button
                if event.button == 9:
                    logger.info("Select button pressed, exiting...")
                    self.running = False
                elif event.button == 10:
                    logger.info("Start button pressed, exiting...")
                    self.running = False

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.player_pos[0] = max(20, self.player_pos[0] - 5)
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.player_pos[0] = min(SCREEN_WIDTH - 20, self.player_pos[0] + 5)
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.player_pos[1] = max(20, self.player_pos[1] - 5)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.player_pos[1] = min(SCREEN_HEIGHT - 20, self.player_pos[1] + 5)

        if self.joystick:
            # d-pad movement
            hat = self.joystick.get_hat(0)
            if hat[0] == -1: # Left
                logger.debug("D-pad left pressed")
                self.player_pos[0] = max(20, self.player_pos[0] - 5)
                self.last_pressed = "d-pad left"
            elif hat[0] == 1: # Right
                logger.debug("D-pad right pressed")
                self.player_pos[0] = min(SCREEN_WIDTH - 20, self.player_pos[0] + 5)
                self.last_pressed = "d-pad right"
            if hat[1] == 1: # Up
                logger.debug("D-pad up pressed")
                self.player_pos[1] = max(20, self.player_pos[1] - 5)
                self.last_pressed = "d-pad up"
            elif hat[1] == -1: # Down
                logger.debug("D-pad down pressed")
                self.player_pos[1] = min(SCREEN_HEIGHT - 20, self.player_pos[1] + 5)
                self.last_pressed = "d-pad down"

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

    def _render_text(self, text, size="normal", pos=(0, 0), color=WHITE):
        font_size = 36 if size == "normal" else 24
        font = pg.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(x=pos[0], y=pos[1])
        self.screen.blit(text_surface, text_rect)

    def draw(self):
        self.screen.fill(BLACK)

        self._render_text("pygame-ce runtime", size="normal", pos=(25, 20))
        self._render_text("use D-pad, analog stick or WASD keys to move", size="small", pos=(25, 50))

        if self.joystick:
            self._render_text(f"joystick with {self.joystick.get_numbuttons()} buttons", size="small", pos=(25, 75), color=GREEN)

            if self.last_pressed:
                self._render_text(f"button {self.last_pressed} pressed", size="small", pos=(25, 100), color=GREEN)
        else:
            self._render_text("no joystick detected", size="small", pos=(25, 75), color=RED)


        pg.draw.circle(self.screen, RED, self.player_pos, 20)

        pg.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

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
