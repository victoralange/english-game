import os
import pygame
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

pygame.display.init()
pygame.font.init()

info = pygame.display.Info()
W, H = info.current_w, info.current_h

screen = pygame.display.set_mode(
    (W, H),
    pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF,
    vsync=1
)
pygame.display.set_caption("Restaurant Simulator")

clock = pygame.time.Clock()


def load_image_hq(filename, target_size=None):
    pil_img = Image.open(os.path.join(ASSETS_DIR, filename)).convert("RGBA")
    if target_size:
        pil_img = pil_img.resize(target_size, Image.Resampling.LANCZOS)
    surface = pygame.image.fromstring(pil_img.tobytes(), pil_img.size, "RGBA")
    return surface.convert_alpha()


background = load_image_hq("background.png", (W, H))

button_width = int(W * 0.20)
button_height = int(H * 0.075)
hover_scale = 1.08

backdrop = pygame.Surface((W, H), pygame.SRCALPHA)
backdrop.fill((0, 0, 0, 220))
backdrop_base_alpha = 220


def load_modal(filename):
    pil = Image.open(os.path.join(ASSETS_DIR, filename)).convert("RGBA")
    max_w = int(W * 0.95)
    max_h = int(H * 0.95)
    ratio = min(max_w / pil.width, max_h / pil.height)
    size = (int(pil.width * ratio), int(pil.height * ratio))
    img = load_image_hq(filename, size)
    rect = img.get_rect(center=(W // 2, H // 2))
    return img, rect


modal_images = {
    "vocabulary": load_modal("food_vocabulary.png"),
    "tutorial": load_modal("tutorial.png"),
}


class Button:
    def __init__(self, filename, y_ratio, command):
        self.original = load_image_hq(filename)
        self.base_size = (button_width, button_height)
        self.command = command
        self.scale = 1.0
        self.target = 1.0
        self.hovered = False
        self.pressed = False
        self.center = (W // 2, int(H * y_ratio))
        self._update_image()
        self.rect = self.image.get_rect(center=self.center)

    def _update_image(self):
        w = int(self.base_size[0] * self.scale)
        h = int(self.base_size[1] * self.scale)
        img = pygame.transform.smoothscale(self.original, (w, h))
        if self.pressed:
            img = img.copy()
            img.fill((150, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
        self.image = img
        self.rect = self.image.get_rect(center=self.center)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.target = hover_scale if self.hovered else 1.0
        if abs(self.scale - self.target) > 0.005:
            step = 0.02 if self.scale < self.target else -0.02
            self.scale += step
            if (step > 0 and self.scale > self.target) or (step < 0 and self.scale < self.target):
                self.scale = self.target
            self._update_image()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self._update_image()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                self._update_image()
                self.command()
            else:
                self.pressed = False
                self._update_image()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


modal_open = False
modal_alpha = 0.0
modal_state = "closed"
modal_key = None
FADE_SPEED = 6.0

running = True


def play_game():
    global running
    running = False


def open_tutorial():
    open_modal("tutorial")


def open_vocabulary():
    open_modal("vocabulary")


def open_modal(key):
    global modal_open, modal_alpha, modal_state, modal_key
    modal_key = key
    modal_open = True
    modal_alpha = 0.0
    modal_state = "fading_in"


def exit_game():
    global running
    running = False
    pygame.event.post(pygame.event.Event(pygame.QUIT))


buttons = [
    Button("play_game.png", 0.60, play_game),
    Button("how_to_play.png", 0.685, open_tutorial),
    Button("vocabulary.png", 0.77, open_vocabulary),
    Button("exit.png", 0.855, exit_game),
]


def run_menu():
    global running, modal_open, modal_alpha, modal_state, modal_key
    running = True
    modal_open = False
    modal_alpha = 0.0
    modal_state = "closed"
    modal_key = None

    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return "quit"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and modal_open and modal_state != "fading_out":
                modal_state = "fading_out"
            elif not modal_open:
                for btn in buttons:
                    btn.handle_event(event)

        if modal_state == "fading_in":
            modal_alpha = min(1.0, modal_alpha + FADE_SPEED * dt)
            if modal_alpha >= 1.0:
                modal_state = "open"
        elif modal_state == "fading_out":
            modal_alpha = max(0.0, modal_alpha - FADE_SPEED * dt)
            if modal_alpha <= 0.0:
                modal_state = "closed"
                modal_open = False
                modal_key = None

        if not modal_open:
            for btn in buttons:
                btn.update(mouse_pos)
                if btn.hovered:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    break
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        screen.blit(background, (0, 0))

        if not modal_open:
            for btn in buttons:
                btn.draw(screen)
        else:
            img, rect = modal_images[modal_key]
            backdrop.set_alpha(int(backdrop_base_alpha * modal_alpha))
            screen.blit(backdrop, (0, 0))
            img.set_alpha(int(255 * modal_alpha))
            screen.blit(img, rect)

        pygame.display.flip()

    return "play"


def main():
    while True:
        result = run_menu()
        if result == "quit":
            break
        elif result == "play":
            try:
                import importlib
                import game
                importlib.reload(game)
                game.run()
            except Exception as e:
                print(f"Erro ao rodar game.py: {e}")
                break

    pygame.quit()


if __name__ == "__main__":
    main()