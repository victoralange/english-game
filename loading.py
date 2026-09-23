import os
import math
import threading
import pygame
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class LoadingScreen:
    def __init__(self, screen, background_surface):
        self.screen = screen
        self.bg = background_surface
        self.W, self.H = screen.get_size()
        self.clock = pygame.time.Clock()
        self.angle = 0.0
        self.running = True

    def _draw_spinner(self):
        self.screen.blit(self.bg, (0, 0))

        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        cx = self.W // 2
        cy = self.H // 2
        radius = max(30, int(min(self.W, self.H) * 0.06))
        thickness = max(6, radius // 5)

        steps = 12
        for i in range(steps):
            a = self.angle + (i * (2 * math.pi / steps))
            alpha = int(255 * (i / steps))
            x = cx + int(math.cos(a) * radius)
            y = cy + int(math.sin(a) * radius)
            dot_r = thickness
            surf = pygame.Surface((dot_r * 2, dot_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 255, alpha), (dot_r, dot_r), dot_r)
            self.screen.blit(surf, (x - dot_r, y - dot_r))

        pygame.display.flip()

    def update_spinner(self, dt):
        self.angle += dt * 6.0
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi

    def pump_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

    def run_blocking(self, work_fn):
        result_box = {"result": None, "error": None, "done": False}

        def worker():
            try:
                result_box["result"] = work_fn()
            except Exception as e:
                import traceback
                traceback.print_exc()
                result_box["error"] = e
            finally:
                result_box["done"] = True

        t = threading.Thread(target=worker, daemon=True)
        t.start()

        while not result_box["done"]:
            dt = self.clock.tick(60) / 1000.0
            self.update_spinner(dt)
            self._draw_spinner()
            self.pump_events()

        for _ in range(8):
            dt = self.clock.tick(60) / 1000.0
            self.update_spinner(dt)
            self._draw_spinner()
            self.pump_events()

        if result_box["error"] is not None:
            raise result_box["error"]
        return result_box["result"]


def load_background_fast(screen, filename="background.png"):
    W, H = screen.get_size()
    try:
        pil = Image.open(os.path.join(ASSETS_DIR, filename)).convert("RGB")
        pil = pil.resize((W, H), Image.Resampling.BILINEAR)
        bg = pygame.image.fromstring(pil.tobytes(), pil.size, "RGB").convert()
        return bg
    except Exception:
        bg = pygame.Surface((W, H))
        bg.fill((20, 20, 30))
        return bg