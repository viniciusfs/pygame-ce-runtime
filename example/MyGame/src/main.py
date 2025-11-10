import sys
import pygame
import logging
import os

from datetime import datetime
from pytmx.util_pygame import load_pygame


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-7s %(message)s',
    handlers=[
        logging.FileHandler('game.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TILED_DIR = os.path.join(ROOT_DIR, 'data/tiled')

TILE_SIZE = 16
TILES_X = 20
TILES_Y = 15
GAME_WIDTH = 320
GAME_HEIGHT = 240
SCREEN_WIDTH = GAME_WIDTH * 2
SCREEN_HEIGHT = GAME_HEIGHT * 2

FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups, hitbox_offset=None):
        super().__init__(groups)

        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.old_rect = self.rect.copy()

        if hitbox_offset:
            self.hitbox_rect = self.rect.inflate(hitbox_offset[0],
                                                 hitbox_offset[1])
            self.old_rect = self.hitbox_rect.copy()


class Tile(Sprite):
    def __init__(self, pos, surface, groups):
        super().__init__(pos, surface, groups)


class Game:
    def __init__(self):
        pygame.init()
        logger.debug(f"Pygame {pygame.version.ver} initialized!")
        logger.debug(f"System total memory: {pygame.system.get_total_ram()}MiB")
        logger.debug(f"SDL version: {pygame.version.SDL}")

        pygame.mixer.init()
        logger.debug(f"SDL mixer version: {pygame.mixer.get_sdl_mixer_version()}")

        self.screen = self._init_screen()
        self.canvas = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        self.joystick = self._init_joystick()

        self.system_info = {
            "versions": {
                "pygame": pygame.version.ver,
                "sdl": pygame.version.SDL,
                "sdl_mixer": pygame.mixer.get_sdl_mixer_version()
            },
            "system": {
                "total_memory": pygame.system.get_total_ram()
            },
            "joystick": {
                "count": pygame.joystick.get_count() if self.joystick else None,
                "buttons": self.joystick.get_numbuttons() if self.joystick else None,
                "axes": self.joystick.get_numaxes() if self.joystick else None,
                "hats": self.joystick.get_numhats() if self.joystick else None,
                "balls": self.joystick.get_numballs() if self.joystick else None,
                "name": self.joystick.get_name() if self.joystick else None
            },
            "display": {
                "driver": pygame.display.get_driver(),
                "num_displays": pygame.display.get_num_displays(),
                "available_modes": pygame.display.list_modes(),
                "current_mode": self.screen.get_size()
            }
        }

        self.sprite_groups = {
            'terrain': pygame.sprite.Group(),
            'water': pygame.sprite.Group()
        }

        self.load_map()

        self.clock = pygame.time.Clock()
        self.running = True
        self.player_pos = [SCREEN_WIDTH//2, SCREEN_HEIGHT//2]
        self.last_pressed = None

    def _init_screen(self):
        pygame.display.init()
        pygame.display.set_caption("pygame-ce runtime")

        logger.debug(f"Display driver: {pygame.display.get_driver()}")
        logger.debug(f"Number of displays: {pygame.display.get_num_displays()}")
        logger.debug(f"Available display modes: {pygame.display.list_modes()}")

        return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def _init_joystick(self):
        joystick = None
        pygame.joystick.init()
        logger.debug(f"Detected {pygame.joystick.get_count()} joystick(s)")

        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            logger.debug(f"Initialized joystick: {joystick.get_name()}")
            logger.debug(f"Joystick buttons: {joystick.get_numbuttons()}")
            logger.debug(f"Joystick trackballs: {joystick.get_numballs()}")
            logger.debug(f"Joystick axes: {joystick.get_numaxes()}")
            logger.debug(f"Joystick hats: {joystick.get_numhats()}")

        return joystick

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit event received, exiting...")
                self.running = False
            elif event.type == pygame.KEYDOWN:
                logger.debug(f"Key pressed: {pygame.key.name(event.key)}")
                if event.key == pygame.K_ESCAPE:
                    logger.info("ESC key pressed, exiting...")
                    self.running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                logger.debug(f"Joystick button {event.button} pressed")
                self.last_pressed = event.button
                if event.button == 9:
                    logger.info("Select button pressed, exiting...")
                    self.running = False
                elif event.button == 10:
                    logger.info("Start button pressed, exiting...")
                    self.running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_pos[0] = max(20, self.player_pos[0] - 5)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_pos[0] = min(SCREEN_WIDTH - 20, self.player_pos[0] + 5)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_pos[1] = max(20, self.player_pos[1] - 5)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
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
        font_size = 22 if size == "normal" else 16
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(x=pos[0], y=pos[1])
        self.canvas.blit(text_surface, text_rect)

    def draw(self):
        self.canvas.fill(BLACK)

        self.sprite_groups["water"].draw(self.canvas)

        self._render_text("pygame-ce runtime", size="normal", pos=(25, 20))
        self._render_text("use D-pad, analog stick or WASD keys to move", size="small", pos=(25, 50))

        if self.joystick:
            self._render_text(f"joystick with {self.joystick.get_numbuttons()} buttons", size="small", pos=(25, 75), color=GREEN)

            if self.last_pressed:
                self._render_text(f"button {self.last_pressed} pressed", size="small", pos=(25, 100), color=GREEN)
        else:
            self._render_text("no joystick detected", size="small", pos=(25, 75), color=RED)


        pygame.draw.circle(self.canvas, RED, self.player_pos, 20)

        self.screen.blit(
            pygame.transform.scale(self.canvas, (SCREEN_WIDTH,
                                                 SCREEN_HEIGHT)),
            (0, 0)
        )

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def load_map(self):
        tmx_data = load_pygame(os.path.join(TILED_DIR, 'default.tmx'))

        for x, y, surface in tmx_data.get_layer_by_name('background').tiles():
            Tile(
                pos=(x * TILE_SIZE, y * TILE_SIZE),
                surface=surface,
                groups=(self.sprite_groups['water'])
            )

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
