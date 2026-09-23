import os
import threading
import pygame
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class LoadingScreen:
    def __init__(self, screen, background_surface, title="Loading..."):
        self.screen = screen
        self.bg = background_surface
        self.W, self.H = screen.get_size()
        self.title = title
        self.progress = 0.0
        self.status = "Initializing..."
        self.done = False
        self.error = None
        self.clock = pygame.time.Clock()

        try:
            self.font_title = pygame.font.SysFont("arial", max(20, int(self.H * 0.045)), bold=True)
            self.font_status = pygame.font.SysFont("arial", max(14, int(self.H * 0.022)))
        except Exception:
            self.font_title = pygame.font.Font(None, 40)
            self.font_status = pygame.font.Font(None, 22)

    def set_progress(self, value, status=None):
        self.progress = max(0.0, min(1.0, value))
        if status:
            self.status = status

    def _draw(self, overlay_alpha=200):
        self.screen.blit(self.bg, (0, 0))

        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, overlay_alpha))
        self.screen.blit(overlay, (0, 0))

        title_surf = self.font_title.render(self.title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.W // 2, int(self.H * 0.42)))
        self.screen.blit(title_surf, title_rect)

        bar_w = int(self.W * 0.55)
        bar_h = max(18, int(self.H * 0.028))
        bar_x = (self.W - bar_w) // 2
        bar_y = int(self.H * 0.52)

        pygame.draw.rect(self.screen, (40, 40, 55), (bar_x, bar_y, bar_w, bar_h), border_radius=bar_h // 2)
        fill_w = int(bar_w * self.progress)
        if fill_w > 0:
            pygame.draw.rect(
                self.screen, (90, 200, 120),
                (bar_x, bar_y, fill_w, bar_h),
                border_radius=bar_h // 2,
            )
        pygame.draw.rect(
            self.screen, (200, 200, 200),
            (bar_x, bar_y, bar_w, bar_h),
            width=2, border_radius=bar_h // 2,
        )

        pct_surf = self.font_status.render(f"{int(self.progress * 100)}%", True, (255, 255, 255))
        pct_rect = pct_surf.get_rect(center=(self.W // 2, bar_y + bar_h + int(self.H * 0.035)))
        self.screen.blit(pct_surf, pct_rect)

        status_surf = self.font_status.render(self.status, True, (200, 200, 210))
        status_rect = status_surf.get_rect(center=(self.W // 2, bar_y + bar_h + int(self.H * 0.075)))
        self.screen.blit(status_surf, status_rect)

        pygame.display.flip()

    def run_with(self, work_fn):
        result_box = {"result": None, "error": None}

        def worker():
            try:
                result_box["result"] = work_fn(self)
            except Exception as e:
                result_box["error"] = e

        t = threading.Thread(target=worker, daemon=True)
        t.start()

        displayed = 0.0
        while t.is_alive() or displayed < 1.0:
            dt = self.clock.tick(60) / 1000.0

            target = self.progress if t.is_alive() else 1.0
            if displayed < target:
                displayed = min(target, displayed + dt * 0.8)
            elif not t.is_alive():
                displayed = min(1.0, displayed + dt * 2.5)

            self._draw_with(displayed)
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            if not t.is_alive() and displayed >= 1.0:
                break

        if result_box["error"] is not None:
            raise result_box["error"]
        return result_box["result"]

    def _draw_with(self, displayed_progress):
        old = self.progress
        self.progress = displayed_progress
        self._draw()
        self.progress = old


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