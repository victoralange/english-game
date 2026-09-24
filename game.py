import os
import json
import random
import pygame
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

W, H = 0, 0
screen = None
clock = pygame.time.Clock()

MIXER_OK = False


def dbg(*args, **kwargs):
    print("[GAME]", *args, **kwargs, flush=True)


def load_sound(filename):
    if not MIXER_OK:
        return None
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print("Erro carregando som", filename, e)
        return None


def play_sound(filename, volume=0.3):
    snd = load_sound(filename)
    if snd is not None:
        try:
            snd.set_volume(volume)
            snd.play()
        except Exception:
            pass


def start_background_music():
    global MIXER_OK
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        MIXER_OK = True
    except Exception:
        MIXER_OK = False
    if not MIXER_OK:
        return
    path = os.path.join(ASSETS_DIR, "background.ogg")
    if not os.path.exists(path):
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.02)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Erro tocando música de fundo:", e)


def stop_background_music():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass


def load_image_hq(filename, target_size=None):
    full = os.path.join(ASSETS_DIR, filename)
    pil_img = Image.open(full).convert("RGBA")
    if target_size:
        pil_img = pil_img.resize(target_size, Image.Resampling.LANCZOS)
    surface = pygame.image.fromstring(pil_img.tobytes(), pil_img.size, "RGBA")
    return surface.convert_alpha()


def load_questions():
    path = os.path.join(BASE_DIR, "questions.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]


_fit_cover_cache = {}


def fit_image_cover(filename, screen_w, screen_h):
    key = (filename, screen_w, screen_h)
    if key in _fit_cover_cache:
        return _fit_cover_cache[key]
    full = os.path.join(ASSETS_DIR, filename)
    pil = Image.open(full).convert("RGBA")
    img_w, img_h = pil.size
    ratio = max(screen_w / img_w, screen_h / img_h)
    new_w = int(img_w * ratio)
    new_h = int(img_h * ratio)
    pil = pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
    surface = pygame.image.fromstring(pil.tobytes(), pil.size, "RGBA").convert_alpha()
    offset_x = (screen_w - new_w) // 2
    offset_y = (screen_h - new_h) // 2
    rect = surface.get_rect(topleft=(offset_x, offset_y))
    result = (surface, rect, offset_x, offset_y)
    _fit_cover_cache[key] = result
    return result


_font_cache = {}


def load_font(size, bold=False):
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    font_path = os.path.join(ASSETS_DIR, "Inter-VariableFont_opsz,wght.ttf")
    f = None
    if os.path.exists(font_path):
        try:
            f = pygame.font.Font(font_path, size)
            if bold:
                f.set_bold(True)
        except Exception:
            f = None
    if f is None:
        try:
            f = pygame.font.SysFont("arial", size, bold=bold)
        except Exception:
            f = pygame.font.Font(None, size)
    _font_cache[key] = f
    return f


def apply_rounded_corners(surface, radius):
    if radius <= 0:
        return surface
    w, h = surface.get_size()
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.5))

    surf_str = pygame.image.tostring(surface, "RGBA")
    pil_img = Image.frombytes("RGBA", (w, h), surf_str)
    pil_img.putalpha(mask)
    data = pil_img.tobytes()
    new_surface = pygame.image.fromstring(data, (w, h), "RGBA").convert_alpha()
    return new_surface


def make_square_surface(surface):
    w, h = surface.get_size()
    side = min(w, h)
    x = (w - side) // 2
    y = (h - side) // 2
    cropped = surface.subsurface(pygame.Rect(x, y, side, side)).copy()
    return cropped


BUTTON_SS = 2


def make_rounded_button_image(w, h, bg_color, border_color, radius=12, border_width=3):
    if w <= 0 or h <= 0:
        return pygame.Surface((1, 1), pygame.SRCALPHA)

    ss_w = w * BUTTON_SS
    ss_h = h * BUTTON_SS
    ss_radius = radius * BUTTON_SS
    ss_border = max(1, border_width * BUTTON_SS)

    img = Image.new("RGBA", (ss_w, ss_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (0, 0, ss_w - 1, ss_h - 1),
        radius=ss_radius,
        fill=bg_color,
        outline=border_color,
        width=ss_border,
    )
    img = img.resize((w, h), Image.Resampling.LANCZOS)
    return pygame.image.fromstring(img.tobytes(), img.size, "RGBA").convert_alpha()


def make_rounded_rect_image(w, h, fill_color, outline_color=None, radius=10, outline_width=4):
    if w <= 0 or h <= 0:
        return pygame.Surface((1, 1), pygame.SRCALPHA)

    ss_w = w * BUTTON_SS
    ss_h = h * BUTTON_SS
    ss_radius = radius * BUTTON_SS

    img = Image.new("RGBA", (ss_w, ss_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if outline_color:
        ss_outline = max(1, outline_width * BUTTON_SS)
        draw.rounded_rectangle(
            (0, 0, ss_w - 1, ss_h - 1),
            radius=ss_radius,
            fill=fill_color,
            outline=outline_color,
            width=ss_outline,
        )
    else:
        draw.rounded_rectangle(
            (0, 0, ss_w - 1, ss_h - 1),
            radius=ss_radius,
            fill=fill_color,
        )
    img = img.resize((w, h), Image.Resampling.LANCZOS)
    return pygame.image.fromstring(img.tobytes(), img.size, "RGBA").convert_alpha()


BTN_COLORS = {
    "normal":    ((45, 55, 100), (20, 25, 55)),
    "hover":     ((60, 75, 130), (30, 40, 90)),
    "pressed":   ((40, 50, 90), (20, 25, 55)),
    "correct":   ((80, 180, 90), (50, 130, 60)),
    "wrong":     ((200, 80, 80), (140, 50, 50)),
}

ING_COLORS = {
    "normal":   ((255, 255, 255, 15), (255, 255, 255)),
    "hover":    ((255, 255, 255, 30), (255, 220, 120)),
    "correct":  ((40, 120, 50, 180), (80, 220, 100)),
    "wrong":    ((140, 40, 40, 180), (240, 80, 80)),
}

ING_GRID_X = [0.054, 0.359, 0.656]
ING_GRID_Y = [0.201, 0.369, 0.535]
ING_CELL_W = 0.290
ING_CELL_H = [0.151, 0.151, 0.135]

MARGIN_X = 0.05
MARGIN_Y = 0.1

WDS_SPEECH_X0 = 0.355
WDS_SPEECH_X1 = 0.905
WDS_SPEECH_Y0 = 0.112
WDS_SPEECH_Y1 = 0.295

WDS_BOX_X0 = 0.036
WDS_BOX_X1 = 0.963
WDS_BOX_Y0 = 0.426
WDS_BOX_Y1 = 0.975

WDS_CENTER_Y = 0.50

BTN_IN_BOX_X = [0.03, 0.51]
BTN_IN_BOX_Y = [0.06, 0.53]
BTN_IN_BOX_W = 0.46
BTN_IN_BOX_H = 0.42

BTN_BOX_Y_OFFSET_PX = 0

BTN_IMG_SQUARE_RATIO = 0.62
BTN_IMG_PADDING = 12
BTN_IMG_RADIUS = 16

BTN_BORDER_RADIUS = 12
BTN_BORDER_WIDTH = 3

CUSTOMER_FALLBACK = "background.png"

WDS_FALLBACK_IMG = "what_do_you_serve.png"

ING_PANEL_X0 = 42 / 1402
ING_PANEL_Y0 = 104 / 1122
ING_PANEL_W  = 1318 / 1402
ING_PANEL_H  = 906 / 1122

ING_TITLE_X = 117 / 1402
ING_TITLE_Y = 140 / 1122
ING_TITLE_W = 1080 / 1402
ING_TITLE_H = 100 / 1122

ING_CLOSE_X = 1236 / 1402
ING_CLOSE_Y = 144 / 1122
ING_CLOSE_W = (1325 - 1236) / 1402
ING_CLOSE_H = (232 - 144) / 1122

ING_GRID_AREA_X = 117 / 1402
ING_GRID_AREA_Y = 300 / 1122
ING_GRID_AREA_W = 1169 / 1402
ING_GRID_AREA_H = 550 / 1122

ING_BTN_AREA_X = 441 / 1402
ING_BTN_AREA_Y = 880 / 1122
ING_BTN_AREA_W = 520 / 1402
ING_BTN_AREA_H = 80 / 1122

ING_GRID_COLS = 3
ING_GRID_ROWS = 3
ING_GAP_X_RATIO = 0.02
ING_GAP_Y_RATIO = 0.03

WRONG_PANEL_X0 = 63 / 1299
WRONG_PANEL_Y0 = 100 / 1211
WRONG_PANEL_W  = 1171 / 1299
WRONG_PANEL_H  = 958 / 1211

WRONG_WANTED_X = 0.043
WRONG_WANTED_Y = 0.295
WRONG_WANTED_W = 0.915
WRONG_WANTED_H = 0.115

WRONG_SERVED_X = 0.043
WRONG_SERVED_Y = 0.495
WRONG_SERVED_W = 0.915
WRONG_SERVED_H = 0.112

WRONG_JUST_X = 0.043
WRONG_JUST_Y = 0.687
WRONG_JUST_W = 0.915
WRONG_JUST_H = 0.260

WRONG_TEXT_PADDING = 0.02

CORRECT_PANEL_X0 = 103 / 1299
CORRECT_PANEL_Y0 = 285 / 1211
CORRECT_PANEL_W  = 1089 / 1299
CORRECT_PANEL_H  = 616 / 1211

CORRECT_TEXT_X = 0.057
CORRECT_TEXT_Y = 0.39
CORRECT_TEXT_W = 0.886
CORRECT_TEXT_H = 0.315

CORRECT_BTN_X = 0.306
CORRECT_BTN_Y = 0.753
CORRECT_BTN_W = 0.388
CORRECT_BTN_H = 0.146

CORRECT_BTN_PAD_X = 0.038
CORRECT_BTN_PAD_Y = 0.08

CORRECT_TEXT_PADDING = 0.02

COMPLETED_PANEL_X0 = 25 / 2014
COMPLETED_PANEL_Y0 = 92 / 781
COMPLETED_PANEL_W  = 1966 / 2014
COMPLETED_PANEL_H  = 660 / 781

COMPLETED_LEFTBOX_X = 84 / 2014
COMPLETED_LEFTBOX_Y = 180 / 781
COMPLETED_LEFTBOX_W = 940 / 2014
COMPLETED_LEFTBOX_H = 420 / 781

COMPLETED_LINE_X = 143 / 2014
COMPLETED_LINE_W = (600 - 143) / 2014
COMPLETED_LINE_H = 70 / 781

COMPLETED_LINE1_Y = 230 / 781
COMPLETED_LINE2_Y = 320 / 781
COMPLETED_LINE3_Y = 410 / 781
COMPLETED_LINE4_Y = 500 / 781

COMPLETED_VALUE_X = 750 / 2014
COMPLETED_VALUE_W = (985 - 750) / 2014

COMPLETED_RIGHTBOX_X = 1049 / 2014
COMPLETED_RIGHTBOX_Y = 263 / 781
COMPLETED_RIGHTBOX_W = 884 / 2014
COMPLETED_RIGHTBOX_H = 276 / 781

COMPLETED_RANK_Y_RATIO = 0.18
COMPLETED_STAR_Y_RATIO = 0.62

COMPLETED_BTN_PLAY_X = 104 / 2014
COMPLETED_BTN_PLAY_Y = 563 / 781
COMPLETED_BTN_PLAY_W = 915 / 2014
COMPLETED_BTN_PLAY_H = 155 / 781

COMPLETED_BTN_MENU_X = 1054 / 2014
COMPLETED_BTN_MENU_Y = 563 / 781
COMPLETED_BTN_MENU_W = 859 / 2014
COMPLETED_BTN_MENU_H = 155 / 781

COMPLETED_PANEL_PADDING = 0.02


MS_SIZE_RATIO = 0.14
MS_MARGIN_RIGHT = 0.03
MS_MARGIN_TOP = 0.03

MS_MONEY_X = 850  / 2172
MS_MONEY_Y = 165  / 724
MS_MONEY_W = 1155 / 2172
MS_MONEY_H = 207  / 724

MS_SCORE_X = 850  / 2172
MS_SCORE_Y = 396  / 724
MS_SCORE_W = 1155 / 2172
MS_SCORE_H = 190  / 724

MS_TEXT_PAD_PX = 40

MS_IMG_ALPHA = 160


_ingredient_cache = {}
_dish_image_cache = {}
_star_cache = {}
_customer_image_cache = {}
_money_score_cache = {}
_wds_image_cache = {}


def get_ingredient_image(rel_path):
    if rel_path in _ingredient_cache:
        return _ingredient_cache[rel_path]
    full_path = os.path.join(ASSETS_DIR, rel_path)
    if os.path.exists(full_path):
        img = load_image_hq(rel_path)
    else:
        img = pygame.Surface((120, 120), pygame.SRCALPHA)
        img.fill((120, 120, 120, 200))
        pygame.draw.rect(img, (200, 200, 200), img.get_rect(), 3)
    _ingredient_cache[rel_path] = img
    return img


def get_dish_image(rel_path):
    if rel_path in _dish_image_cache:
        return _dish_image_cache[rel_path]
    if not rel_path:
        _dish_image_cache[rel_path] = None
        return None
    full_path = os.path.join(ASSETS_DIR, rel_path)
    if os.path.exists(full_path):
        img = load_image_hq(rel_path)
    else:
        img = None
    _dish_image_cache[rel_path] = img
    return img


_star_scaled_cache = {}


def get_star_image(stars):
    stars = max(1, min(5, stars))
    if stars in _star_cache:
        return _star_cache[stars]
    path = os.path.join(ASSETS_DIR, f"{stars}_star.png")
    if os.path.exists(path):
        img = load_image_hq(f"{stars}_star.png")
    else:
        img = None
    _star_cache[stars] = img
    return img


def get_star_scaled(stars, max_w):
    key = (stars, max_w)
    if key in _star_scaled_cache:
        return _star_scaled_cache[key]
    img = get_star_image(stars)
    if img is None:
        _star_scaled_cache[key] = None
        return None
    ratio = min(1.0, max_w / img.get_width())
    new_w = int(img.get_width() * ratio)
    new_h = int(img.get_height() * ratio)
    scaled = pygame.transform.smoothscale(img, (new_w, new_h))
    _star_scaled_cache[key] = scaled
    return scaled


def get_customer_image(rel_path):
    if not rel_path:
        return None
    if rel_path in _customer_image_cache:
        return _customer_image_cache[rel_path]
    full_path = os.path.join(ASSETS_DIR, rel_path)
    if os.path.exists(full_path):
        img = load_image_hq(rel_path)
    else:
        img = None
    _customer_image_cache[rel_path] = img
    return img


def get_money_score_image(rel_path="money_score.png"):
    if rel_path in _money_score_cache:
        return _money_score_cache[rel_path]
    full_path = os.path.join(ASSETS_DIR, rel_path)
    if os.path.exists(full_path):
        img = load_image_hq(rel_path)
    else:
        img = None
    _money_score_cache[rel_path] = img
    return img


def load_wds_image(customer_path, W, H):
    key = (customer_path, W, H)
    if key in _wds_image_cache:
        return _wds_image_cache[key]

    filename = customer_path
    full = os.path.join(ASSETS_DIR, filename) if filename else ""

    if not filename or not os.path.exists(full):
        filename = WDS_FALLBACK_IMG
        full = os.path.join(ASSETS_DIR, filename)

    pil = Image.open(full).convert("RGBA")

    max_w = int(W * (1 - 2 * MARGIN_X))
    max_h = int(H * (1 - 2 * MARGIN_Y))

    ratio = min(
        max_w / pil.width,
        max_h / pil.height
    )

    target_w = int(pil.width * ratio)
    target_h = int(pil.height * ratio)

    pil = pil.resize(
        (target_w, target_h),
        Image.Resampling.LANCZOS
    )

    surface = pygame.image.fromstring(
        pil.tobytes(),
        pil.size,
        "RGBA"
    ).convert_alpha()

    _wds_image_cache[key] = surface
    return surface


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def truncate_with_ellipsis(text, font, max_width):
    if font.size(text)[0] <= max_width:
        return text
    ellipsis = "..."
    t = text
    while t and font.size(t + ellipsis)[0] > max_width:
        t = t[:-1]
    return t + ellipsis if t else ellipsis


def draw_text_centered(surface, text, font, rect, color, padding_x=0, padding_y=0, line_spacing=4):
    inner_w = rect.width - padding_x * 2
    inner_h = rect.height - padding_y * 2
    if inner_w < 10:
        inner_w = rect.width
    lines = wrap_text(text, font, inner_w)
    line_h = font.get_linesize()
    total_h = line_h * len(lines) + line_spacing * max(0, len(lines) - 1)
    y = rect.centery - total_h // 2
    for line in lines:
        surf = font.render(line, True, color)
        surface.blit(surf, surf.get_rect(center=(rect.centerx, y + line_h // 2)))
        y += line_h + line_spacing


def get_rank_and_stars(final_score):
    if final_score >= 5000:
        return "FOOD EXPERT", 5
    elif final_score >= 4000:
        return "HEAD CHEF", 4
    elif final_score >= 3000:
        return "SOUS CHEF", 3
    elif final_score >= 2000:
        return "LINE COOK", 2
    else:
        return "TRAINEE", 1


class AnswerButton:
    _bg_cache = {}

    def __init__(self, rect, text, font, index, callback, dish_image_path=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.index = index
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.selected = None

        self.dish_img = None
        self._build_dish_image(dish_image_path)

        self.bg_normal = None
        self.bg_hover = None
        self.bg_pressed = None
        self.bg_correct = None
        self.bg_wrong = None
        self._build_bg_images()

        self._text_cache = None
        self._text_cache_lines = None

    def _build_bg_images(self):
        w, h = self.rect.width, self.rect.height
        key = (w, h)
        cached = AnswerButton._bg_cache.get(key)
        if cached is not None:
            (self.bg_normal, self.bg_hover, self.bg_pressed,
             self.bg_correct, self.bg_wrong) = cached
            return
        self.bg_normal = make_rounded_button_image(
            w, h, BTN_COLORS["normal"][0], BTN_COLORS["normal"][1],
            radius=BTN_BORDER_RADIUS, border_width=BTN_BORDER_WIDTH
        )
        self.bg_hover = make_rounded_button_image(
            w, h, BTN_COLORS["hover"][0], BTN_COLORS["hover"][1],
            radius=BTN_BORDER_RADIUS, border_width=BTN_BORDER_WIDTH
        )
        self.bg_pressed = make_rounded_button_image(
            w, h, BTN_COLORS["pressed"][0], BTN_COLORS["pressed"][1],
            radius=BTN_BORDER_RADIUS, border_width=BTN_BORDER_WIDTH
        )
        self.bg_correct = make_rounded_button_image(
            w, h, BTN_COLORS["correct"][0], BTN_COLORS["correct"][1],
            radius=BTN_BORDER_RADIUS, border_width=BTN_BORDER_WIDTH
        )
        self.bg_wrong = make_rounded_button_image(
            w, h, BTN_COLORS["wrong"][0], BTN_COLORS["wrong"][1],
            radius=BTN_BORDER_RADIUS, border_width=BTN_BORDER_WIDTH
        )
        AnswerButton._bg_cache[key] = (
            self.bg_normal, self.bg_hover, self.bg_pressed,
            self.bg_correct, self.bg_wrong
        )

    def _build_dish_image(self, dish_image_path):
        raw = get_dish_image(dish_image_path)
        if raw is None:
            self.dish_img = None
            return

        square = make_square_surface(raw)

        max_w = self.rect.width - BTN_IMG_PADDING * 2
        max_h = int(self.rect.height * BTN_IMG_SQUARE_RATIO)
        target_side = min(max_w, max_h, square.get_width())
        if target_side < 4:
            target_side = 4

        scaled = pygame.transform.smoothscale(square, (target_side, target_side))
        radius = min(BTN_IMG_RADIUS, target_side // 4)
        scaled = apply_rounded_corners(scaled, radius)
        self.dish_img = scaled

    def _get_dish_rect(self):
        if self.dish_img is None:
            return None
        side = self.dish_img.get_width()
        return pygame.Rect(
            self.rect.centerx - side // 2,
            self.rect.top + BTN_IMG_PADDING,
            side, side
        )

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                if self.callback:
                    self.callback(self.index)
            else:
                self.pressed = False

    def _get_text_surfs(self):
        if self._text_cache is not None:
            return self._text_cache
        max_w = self.rect.width - 20
        lines = wrap_text(self.text, self.font, max_w)
        surfs = [self.font.render(line, True, (255, 255, 255)) for line in lines]
        self._text_cache = surfs
        return surfs

    def draw(self, surface):
        if self.selected is True:
            bg_img = self.bg_correct
        elif self.selected is False:
            bg_img = self.bg_wrong
        elif self.pressed:
            bg_img = self.bg_pressed
        elif self.hovered:
            bg_img = self.bg_hover
        else:
            bg_img = self.bg_normal

        surface.blit(bg_img, self.rect.topleft)

        if self.dish_img is not None:
            rect = self._get_dish_rect()
            surface.blit(self.dish_img, rect)

        surfs = self._get_text_surfs()
        line_h = self.font.get_linesize()
        total_h = line_h * len(surfs)
        y = self.rect.bottom - total_h - 10
        for surf in surfs:
            surface.blit(surf, surf.get_rect(center=(self.rect.centerx, y + line_h // 2)))
            y += line_h


_ing_bg_cache = {}
_ing_checkbox_cache = None


def _get_ing_checkbox_images():
    global _ing_checkbox_cache
    if _ing_checkbox_cache is not None:
        return _ing_checkbox_cache
    cb_size = 32
    cb_normal = make_rounded_rect_image(
        cb_size, cb_size, (0, 0, 0, 0), (255, 255, 255),
        radius=6, outline_width=3
    )

    def make_check(color):
        ss = BUTTON_SS
        img = Image.new("RGBA", (cb_size * ss, cb_size * ss), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(
            (0, 0, cb_size * ss - 1, cb_size * ss - 1),
            radius=6 * ss,
            outline=color,
            width=3 * ss,
        )
        pts = [
            (cb_size * ss * 0.22, cb_size * ss * 0.55),
            (cb_size * ss * 0.42, cb_size * ss * 0.75),
            (cb_size * ss * 0.78, cb_size * ss * 0.28),
        ]
        draw.line(pts, fill=color, width=4 * ss, joint="curve")
        img = img.resize((cb_size, cb_size), Image.Resampling.LANCZOS)
        return pygame.image.fromstring(img.tobytes(), img.size, "RGBA").convert_alpha()

    cb_checked = make_check((255, 220, 120))
    cb_checked_wrong = make_check((240, 80, 80))
    cb_checked_correct = make_check((80, 220, 100))
    _ing_checkbox_cache = (cb_normal, cb_checked, cb_checked_wrong, cb_checked_correct)
    return _ing_checkbox_cache


class IngredientBox:
    def __init__(self, rect, index, name, image_path, font):
        self.rect = pygame.Rect(rect)
        self.index = index
        self.name = name
        self.font = font
        self.hovered = False
        self.checked = False
        self.revealed = None

        raw = get_ingredient_image(image_path)
        max_w = self.rect.width - 24
        max_h = self.rect.height - self.font.get_height() - 30
        if max_w < 10: max_w = 10
        if max_h < 10: max_h = 10
        ratio = min(max_w / raw.get_width(), max_h / raw.get_height(), 1.0)
        new_size = (max(1, int(raw.get_width() * ratio)), max(1, int(raw.get_height() * ratio)))
        self.image = pygame.transform.smoothscale(raw, new_size)
        self.image_rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery - 10))

        self.bg_normal = None
        self.bg_hover = None
        self.bg_correct = None
        self.bg_wrong = None
        self._build_bg_images()

        self.cb_normal, self.cb_checked, self.cb_checked_wrong, self.cb_checked_correct = _get_ing_checkbox_images()

        self._name_surf = None

    def _build_bg_images(self):
        w, h = self.rect.width, self.rect.height
        key = (w, h)
        cached = _ing_bg_cache.get(key)
        if cached is not None:
            (self.bg_normal, self.bg_hover,
             self.bg_correct, self.bg_wrong) = cached
            return
        self.bg_normal = make_rounded_rect_image(
            w, h, ING_COLORS["normal"][0], ING_COLORS["normal"][1],
            radius=10, outline_width=4
        )
        self.bg_hover = make_rounded_rect_image(
            w, h, ING_COLORS["hover"][0], ING_COLORS["hover"][1],
            radius=10, outline_width=4
        )
        self.bg_correct = make_rounded_rect_image(
            w, h, ING_COLORS["correct"][0], ING_COLORS["correct"][1],
            radius=10, outline_width=4
        )
        self.bg_wrong = make_rounded_rect_image(
            w, h, ING_COLORS["wrong"][0], ING_COLORS["wrong"][1],
            radius=10, outline_width=4
        )
        _ing_bg_cache[key] = (self.bg_normal, self.bg_hover,
                              self.bg_correct, self.bg_wrong)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.revealed is None:
                self.checked = not self.checked
                return True
        return False

    def draw(self, surface):
        if self.revealed is True:
            bg = self.bg_correct
        elif self.revealed is False:
            bg = self.bg_wrong
        elif self.hovered:
            bg = self.bg_hover
        else:
            bg = self.bg_normal

        surface.blit(bg, self.rect.topleft)
        surface.blit(self.image, self.image_rect)

        if self._name_surf is None:
            self._name_surf = self.font.render(self.name, True, (255, 255, 255))
        name_rect = self._name_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 18))
        surface.blit(self._name_surf, name_rect)

        cb_size = 32
        cb_pos = (self.rect.right - cb_size - 10, self.rect.top + 10)
        if self.checked:
            if self.revealed is True:
                cb_img = self.cb_checked_correct
            elif self.revealed is False:
                cb_img = self.cb_checked_wrong
            else:
                cb_img = self.cb_checked
        else:
            cb_img = self.cb_normal

        surface.blit(cb_img, cb_pos)


class ConfirmButton:
    _img_cache = None

    def __init__(self, rect, callback):
        self.rect = pygame.Rect(rect)
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.enabled = True

        try:
            if ConfirmButton._img_cache is None:
                raw = load_image_hq("button_confirm.png")
                ConfirmButton._img_cache = raw
            raw = ConfirmButton._img_cache
            target_h = rect[3]
            ratio = target_h / raw.get_height()
            target_w = int(raw.get_width() * ratio)
            scaled = pygame.transform.smoothscale(raw, (target_w, target_h))
            self.img_normal = scaled
            self.rect = pygame.Rect(
                rect[0] + (rect[2] - target_w) // 2,
                rect[1],
                target_w,
                target_h,
            )
        except Exception:
            self.img_normal = None

        if self.img_normal is not None:
            self.img_hover = self._tint(self.img_normal, 1.15)
            self.img_pressed = self._tint(self.img_normal, 0.75)
        else:
            self.img_hover = None
            self.img_pressed = None

    def _tint(self, surface, factor):
        copy = surface.copy()
        if factor < 1.0:
            v = int(255 * factor)
            copy.fill((v, v, v, 255), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            v = int(255 * (factor - 1.0))
            copy.fill((v, v, v, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return copy

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if not self.enabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = False
                if self.callback:
                    self.callback()
            else:
                self.pressed = False

    def draw(self, surface):
        if not self.enabled:
            return
        if self.img_normal is None:
            pygame.draw.rect(surface, (60, 120, 60), self.rect, border_radius=12)
            pygame.draw.rect(surface, (30, 80, 30), self.rect, width=3, border_radius=12)
        else:
            if self.pressed:
                surface.blit(self.img_pressed, self.rect.topleft)
            elif self.hovered:
                surface.blit(self.img_hover, self.rect.topleft)
            else:
                surface.blit(self.img_normal, self.rect.topleft)


class CloseButton:
    def __init__(self, rect, callback):
        self.rect = pygame.Rect(rect)
        self.callback = callback
        self.hovered = False
        self.pressed = False

        self.img_normal = self._make_close_image()
        self.img_hover = self.img_normal
        self.img_pressed = self.img_normal

    def _make_close_image(self):
        w, h = self.rect.width, self.rect.height
        if w <= 0 or h <= 0:
            return pygame.Surface((1, 1), pygame.SRCALPHA)

        ss = BUTTON_SS
        img = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        fill_color = (30, 30, 40, 220)

        padding = int(min(w, h) * 0.10) * ss
        draw.ellipse((padding, padding, w * ss - padding, h * ss - padding), fill=fill_color)

        line_w = max(2, int(min(w, h) * 0.10)) * ss
        color = (255, 255, 255)
        margin = int(min(w, h) * 0.32) * ss
        draw.line([(margin, margin), (w * ss - margin, h * ss - margin)], fill=color, width=line_w)
        draw.line([(w * ss - margin, margin), (margin, h * ss - margin)], fill=color, width=line_w)

        img = img.resize((w, h), Image.Resampling.LANCZOS)
        return pygame.image.fromstring(img.tobytes(), img.size, "RGBA").convert_alpha()

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = False
                if self.callback:
                    self.callback()
            else:
                self.pressed = False

    def draw(self, surface):
        if self.pressed:
            surface.blit(self.img_pressed, self.rect.topleft)
        elif self.hovered:
            surface.blit(self.img_hover, self.rect.topleft)
        else:
            surface.blit(self.img_normal, self.rect.topleft)


class InvisibleButton:
    def __init__(self, rect, callback):
        self.rect = pygame.Rect(rect)
        self.callback = callback
        self.hovered = False
        self.pressed = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                if self.callback:
                    self.callback()
            else:
                self.pressed = False

    def draw(self, surface):
        pass


def build_game_state(screen, W, H, tick=None):
    def _tick():
        if tick:
            tick()

    state = {
        "W": W,
        "H": H,
        "customer_bg": None,
        "cust_rect": None,
        "serving_bg": None,
        "serve_rect": None,
        "serving_current": None,
        "ingredients_bg": None,
        "ing_rect": None,
        "wrong_bg": None,
        "wrong_rect": None,
        "correct_bg": None,
        "correct_rect": None,
        "completed_bg": None,
        "completed_rect": None,
        "wds_img": None,
        "WDS_W_PX": 0,
        "WDS_H_PX": 0,
        "ing_cells": [],
        "fonts": {},
        "ing_modal_rect": None,
        "wds_speech_rect": None,
        "wds_box_rect": None,
        "ing_grid_area": None,
        "ing_btn_area": None,
        "ing_title_rect": None,
        "ing_close_rect": None,
        "wrong_panel_rect": None,
        "wrong_wanted_rect": None,
        "wrong_served_rect": None,
        "wrong_just_rect": None,
        "correct_panel_rect": None,
        "correct_text_rect": None,
        "correct_btn_rect": None,
        "completed_panel_rect": None,
        "completed_leftbox_rect": None,
        "completed_rightbox_rect": None,
        "completed_lines_rects": [],
        "completed_values_rects": [],
        "completed_btn_play_rect": None,
        "completed_btn_menu_rect": None,
        "money_score_img": None,
        "ms_rect": None,
        "ms_money_rect": None,
        "ms_score_rect": None,
    }

    _tick()
    state["customer_bg"], state["cust_rect"], _, _ = fit_image_cover(
        "customer.png", W, H
    )

    _tick()
    state["serving_bg"], state["serve_rect"], _, _ = fit_image_cover(
        CUSTOMER_FALLBACK, W, H
    )
    state["serving_current"] = CUSTOMER_FALLBACK

    _tick()
    wds_pil = Image.open(
        os.path.join(ASSETS_DIR, "what_do_you_serve.png")
    ).convert("RGBA")

    max_w = int(W * (1 - 2 * MARGIN_X))
    max_h = int(H * (1 - 2 * MARGIN_Y))

    ratio = min(
        max_w / wds_pil.width,
        max_h / wds_pil.height
    )

    target_w = int(wds_pil.width * ratio)
    target_h = int(wds_pil.height * ratio)

    wds_pil = wds_pil.resize(
        (target_w, target_h),
        Image.Resampling.LANCZOS
    )

    state["wds_img"] = pygame.image.fromstring(
        wds_pil.tobytes(),
        wds_pil.size,
        "RGBA"
    ).convert_alpha()

    state["WDS_W_PX"] = state["wds_img"].get_width()
    state["WDS_H_PX"] = state["wds_img"].get_height()

    state["wds_speech_rect"] = pygame.Rect(
        int(state["WDS_W_PX"] * WDS_SPEECH_X0),
        int(state["WDS_H_PX"] * WDS_SPEECH_Y0),
        int(
            state["WDS_W_PX"]
            * (WDS_SPEECH_X1 - WDS_SPEECH_X0)
        ),
        int(
            state["WDS_H_PX"]
            * (WDS_SPEECH_Y1 - WDS_SPEECH_Y0)
        )
    )

    state["wds_box_rect"] = pygame.Rect(
        int(state["WDS_W_PX"] * WDS_BOX_X0),
        int(state["WDS_H_PX"] * WDS_BOX_Y0),
        int(
            state["WDS_W_PX"]
            * (WDS_BOX_X1 - WDS_BOX_X0)
        ),
        int(
            state["WDS_H_PX"]
            * (WDS_BOX_Y1 - WDS_BOX_Y0)
        )
    )

    _tick()
    ing_pil = Image.open(
        os.path.join(ASSETS_DIR, "ingredients.png")
    ).convert("RGBA")

    max_w = int(W * (1 - 2 * MARGIN_X))
    max_h = int(H * (1 - 2 * MARGIN_Y))

    ratio = min(
        max_w / ing_pil.width,
        max_h / ing_pil.height
    )

    modal_w = int(ing_pil.width * ratio)
    modal_h = int(ing_pil.height * ratio)

    ing_pil = ing_pil.resize(
        (modal_w, modal_h),
        Image.Resampling.LANCZOS
    )

    state["ingredients_bg"] = pygame.image.fromstring(
        ing_pil.tobytes(),
        ing_pil.size,
        "RGBA"
    ).convert_alpha()

    modal_x = (W - modal_w) // 2
    modal_y = (H - modal_h) // 2

    state["ing_modal_rect"] = pygame.Rect(
        modal_x,
        modal_y,
        modal_w,
        modal_h
    )

    state["ing_rect"] = state["ing_modal_rect"]

    state["ing_title_rect"] = pygame.Rect(
        modal_x + int(modal_w * ING_TITLE_X),
        modal_y + int(modal_h * ING_TITLE_Y),
        int(modal_w * ING_TITLE_W),
        int(modal_h * ING_TITLE_H),
    )

    state["ing_close_rect"] = pygame.Rect(
        modal_x + int(modal_w * ING_CLOSE_X),
        modal_y + int(modal_h * ING_CLOSE_Y),
        int(modal_w * ING_CLOSE_W),
        int(modal_h * ING_CLOSE_H),
    )

    grid_x = modal_x + int(modal_w * ING_GRID_AREA_X)
    grid_y = modal_y + int(modal_h * ING_GRID_AREA_Y)
    grid_w = int(modal_w * ING_GRID_AREA_W)
    grid_h = int(modal_h * ING_GRID_AREA_H)

    state["ing_grid_area"] = pygame.Rect(
        grid_x,
        grid_y,
        grid_w,
        grid_h
    )

    state["ing_btn_area"] = pygame.Rect(
        modal_x + int(modal_w * ING_BTN_AREA_X),
        modal_y + int(modal_h * ING_BTN_AREA_Y),
        int(modal_w * ING_BTN_AREA_W),
        int(modal_h * ING_BTN_AREA_H),
    )

    gap_x = int(grid_w * ING_GAP_X_RATIO)
    gap_y = int(grid_h * ING_GAP_Y_RATIO)

    cell_w = (
        grid_w - gap_x * (ING_GRID_COLS - 1)
    ) // ING_GRID_COLS

    cell_h = (
        grid_h - gap_y * (ING_GRID_ROWS - 1)
    ) // ING_GRID_ROWS

    ing_cells = []

    for row in range(ING_GRID_ROWS):
        for col in range(ING_GRID_COLS):
            x = grid_x + col * (cell_w + gap_x)
            y = grid_y + row * (cell_h + gap_y)

            ing_cells.append(
                pygame.Rect(
                    x,
                    y,
                    cell_w,
                    cell_h
                )
            )

    state["ing_cells"] = ing_cells

    _tick()
    wrong_pil = Image.open(
        os.path.join(ASSETS_DIR, "wrong.png")
    ).convert("RGBA")

    max_w = int(W * (1 - 2 * MARGIN_X))
    max_h = int(H * (1 - 2 * MARGIN_Y))

    ratio = min(
        max_w / wrong_pil.width,
        max_h / wrong_pil.height
    )

    wr_w = int(wrong_pil.width * ratio)
    wr_h = int(wrong_pil.height * ratio)

    wrong_pil = wrong_pil.resize(
        (wr_w, wr_h),
        Image.Resampling.LANCZOS
    )

    state["wrong_bg"] = pygame.image.fromstring(
        wrong_pil.tobytes(),
        wrong_pil.size,
        "RGBA"
    ).convert_alpha()

    wr_x = (W - wr_w) // 2
    wr_y = (H - wr_h) // 2

    state["wrong_rect"] = pygame.Rect(
        wr_x,
        wr_y,
        wr_w,
        wr_h
    )

    panel_x = wr_x + int(wr_w * WRONG_PANEL_X0)
    panel_y = wr_y + int(wr_h * WRONG_PANEL_Y0)
    panel_w = int(wr_w * WRONG_PANEL_W)
    panel_h = int(wr_h * WRONG_PANEL_H)

    state["wrong_panel_rect"] = pygame.Rect(
        panel_x,
        panel_y,
        panel_w,
        panel_h
    )

    def make_box_wrong(bx, by, bw, bh):
        return pygame.Rect(
            panel_x + int(panel_w * bx),
            panel_y + int(panel_h * by),
            int(panel_w * bw),
            int(panel_h * bh),
        )

    state["wrong_wanted_rect"] = make_box_wrong(
        WRONG_WANTED_X,
        WRONG_WANTED_Y,
        WRONG_WANTED_W,
        WRONG_WANTED_H
    )

    state["wrong_served_rect"] = make_box_wrong(
        WRONG_SERVED_X,
        WRONG_SERVED_Y,
        WRONG_SERVED_W,
        WRONG_SERVED_H
    )

    state["wrong_just_rect"] = make_box_wrong(
        WRONG_JUST_X,
        WRONG_JUST_Y,
        WRONG_JUST_W,
        WRONG_JUST_H
    )

    _tick()
    correct_pil = Image.open(
        os.path.join(ASSETS_DIR, "correct.png")
    ).convert("RGBA")

    max_w = int(W * (1 - 2 * MARGIN_X))
    max_h = int(H * (1 - 2 * MARGIN_Y))

    ratio = min(
        max_w / correct_pil.width,
        max_h / correct_pil.height
    )

    cr_w = int(correct_pil.width * ratio)
    cr_h = int(correct_pil.height * ratio)

    correct_pil = correct_pil.resize(
        (cr_w, cr_h),
        Image.Resampling.LANCZOS
    )

    state["correct_bg"] = pygame.image.fromstring(
        correct_pil.tobytes(),
        correct_pil.size,
        "RGBA"
    ).convert_alpha()

    cr_x = (W - cr_w) // 2
    cr_y = (H - cr_h) // 2

    state["correct_rect"] = pygame.Rect(
        cr_x,
        cr_y,
        cr_w,
        cr_h
    )

    cpanel_x = cr_x + int(cr_w * CORRECT_PANEL_X0)
    cpanel_y = cr_y + int(cr_h * CORRECT_PANEL_Y0)
    cpanel_w = int(cr_w * CORRECT_PANEL_W)
    cpanel_h = int(cr_h * CORRECT_PANEL_H)

    state["correct_panel_rect"] = pygame.Rect(
        cpanel_x,
        cpanel_y,
        cpanel_w,
        cpanel_h
    )

    def make_box_correct(bx, by, bw, bh):
        return pygame.Rect(
            cpanel_x + int(cpanel_w * bx),
            cpanel_y + int(cpanel_h * by),
            int(cpanel_w * bw),
            int(cpanel_h * bh),
        )

    state["correct_text_rect"] = make_box_correct(
        CORRECT_TEXT_X,
        CORRECT_TEXT_Y,
        CORRECT_TEXT_W,
        CORRECT_TEXT_H
    )

    state["correct_btn_rect"] = make_box_correct(
        CORRECT_BTN_X,
        CORRECT_BTN_Y,
        CORRECT_BTN_W,
        CORRECT_BTN_H
    )

    _tick()
    comp_pil = Image.open(
        os.path.join(ASSETS_DIR, "completed.png")
    ).convert("RGBA")

    max_w = int(W * (1 - 2 * MARGIN_X))
    max_h = int(H * (1 - 2 * MARGIN_Y))

    ratio = min(
        max_w / comp_pil.width,
        max_h / comp_pil.height
    )

    cp_w = int(comp_pil.width * ratio)
    cp_h = int(comp_pil.height * ratio)

    comp_pil = comp_pil.resize(
        (cp_w, cp_h),
        Image.Resampling.LANCZOS
    )

    state["completed_bg"] = pygame.image.fromstring(
        comp_pil.tobytes(),
        comp_pil.size,
        "RGBA"
    ).convert_alpha()

    cp_x = (W - cp_w) // 2
    cp_y = (H - cp_h) // 2

    state["completed_rect"] = pygame.Rect(
        cp_x,
        cp_y,
        cp_w,
        cp_h
    )

    panel_x = cp_x + int(cp_w * COMPLETED_PANEL_X0)
    panel_y = cp_y + int(cp_h * COMPLETED_PANEL_Y0)
    panel_w = int(cp_w * COMPLETED_PANEL_W)
    panel_h = int(cp_h * COMPLETED_PANEL_H)

    state["completed_panel_rect"] = pygame.Rect(
        panel_x,
        panel_y,
        panel_w,
        panel_h
    )

    def make_box_comp(bx, by, bw, bh):
        return pygame.Rect(
            panel_x + int(panel_w * bx),
            panel_y + int(panel_h * by),
            int(panel_w * bw),
            int(panel_h * bh),
        )

    state["completed_leftbox_rect"] = make_box_comp(
        COMPLETED_LEFTBOX_X,
        COMPLETED_LEFTBOX_Y,
        COMPLETED_LEFTBOX_W,
        COMPLETED_LEFTBOX_H
    )

    state["completed_rightbox_rect"] = make_box_comp(
        COMPLETED_RIGHTBOX_X,
        COMPLETED_RIGHTBOX_Y,
        COMPLETED_RIGHTBOX_W,
        COMPLETED_RIGHTBOX_H
    )

    lines_rects = []
    values_rects = []

    for ly in [
        COMPLETED_LINE1_Y,
        COMPLETED_LINE2_Y,
        COMPLETED_LINE3_Y,
        COMPLETED_LINE4_Y
    ]:
        lines_rects.append(
            make_box_comp(
                COMPLETED_LINE_X,
                ly,
                COMPLETED_LINE_W,
                COMPLETED_LINE_H
            )
        )

        values_rects.append(
            make_box_comp(
                COMPLETED_VALUE_X,
                ly,
                COMPLETED_VALUE_W,
                COMPLETED_LINE_H
            )
        )

    state["completed_lines_rects"] = lines_rects
    state["completed_values_rects"] = values_rects

    state["completed_btn_play_rect"] = make_box_comp(
        COMPLETED_BTN_PLAY_X,
        COMPLETED_BTN_PLAY_Y,
        COMPLETED_BTN_PLAY_W,
        COMPLETED_BTN_PLAY_H
    )

    state["completed_btn_menu_rect"] = make_box_comp(
        COMPLETED_BTN_MENU_X,
        COMPLETED_BTN_MENU_Y,
        COMPLETED_BTN_MENU_W,
        COMPLETED_BTN_MENU_H
    )

    _tick()
    ms_img = get_money_score_image("money_score.png")

    state["money_score_img"] = ms_img

    if ms_img is not None:
        img_w = int(W * MS_SIZE_RATIO)

        ratio = img_w / ms_img.get_width()
        img_h = int(ms_img.get_height() * ratio)

        scaled = pygame.transform.smoothscale(
            ms_img,
            (img_w, img_h)
        )

        scaled.set_alpha(MS_IMG_ALPHA)

        state["money_score_img"] = scaled

        ms_x = (
            W
            - img_w
            - int(W * MS_MARGIN_RIGHT)
        )

        ms_y = int(H * MS_MARGIN_TOP)

        state["ms_rect"] = pygame.Rect(
            ms_x,
            ms_y,
            img_w,
            img_h
        )

        state["ms_money_rect"] = pygame.Rect(
            ms_x + int(img_w * MS_MONEY_X),
            ms_y + int(img_h * MS_MONEY_Y),
            int(img_w * MS_MONEY_W),
            int(img_h * MS_MONEY_H),
        )

        state["ms_score_rect"] = pygame.Rect(
            ms_x + int(img_w * MS_SCORE_X),
            ms_y + int(img_h * MS_SCORE_Y),
            int(img_w * MS_SCORE_W),
            int(img_h * MS_SCORE_H),
        )

    else:
        state["ms_rect"] = None
        state["ms_money_rect"] = None
        state["ms_score_rect"] = None

    _tick()
    state["fonts"] = {
        "answer": load_font(
            int(state["WDS_H_PX"] * 0.035),
            bold=False
        ),
        "ui": load_font(
            int(H * 0.028),
            bold=False
        ),
        "feedback": load_font(
            int(H * 0.032),
            bold=False
        ),
        "ing_name": load_font(
            int(modal_h * 0.022),
            bold=False
        ),
        "end": load_font(
            int(H * 0.06),
            bold=False
        ),
        "question": load_font(
            int(state["WDS_H_PX"] * 0.040),
            bold=False
        ),
        "wrong": load_font(
            int(state["WDS_H_PX"] * 0.034),
            bold=False
        ),
        "wrong_just": load_font(
            int(state["WDS_H_PX"] * 0.030),
            bold=False
        ),
        "ing_title": load_font(
            int(modal_h * 0.045),
            bold=False
        ),
        "correct_text": load_font(
            int(state["WDS_H_PX"] * 0.038),
            bold=False
        ),
        "correct_btn": load_font(
            int(state["WDS_H_PX"] * 0.036),
            bold=False
        ),
        "completed_label": load_font(
            int(H * 0.032),
            bold=False
        ),
        "completed_value": load_font(
            int(H * 0.032),
            bold=False
        ),
        "rank": load_font(
            int(H * 0.045),
            bold=False
        ),
        "money_score": load_font(
            max(12, int(img_h * 0.16)),
            bold=True
        ) if ms_img is not None else load_font(16, bold=True),
    }

    _tick()
    questions = load_questions()
    questions = random.sample(questions, 10) 

    current_question = questions[0]

    first_customer = current_question.get("customer_image")
    state["wds_img"] = load_wds_image(first_customer, W, H)
    state["WDS_W_PX"] = state["wds_img"].get_width()
    state["WDS_H_PX"] = state["wds_img"].get_height()

    state["wds_speech_rect"] = pygame.Rect(
        int(state["WDS_W_PX"] * WDS_SPEECH_X0),
        int(state["WDS_H_PX"] * WDS_SPEECH_Y0),
        int(state["WDS_W_PX"] * (WDS_SPEECH_X1 - WDS_SPEECH_X0)),
        int(state["WDS_H_PX"] * (WDS_SPEECH_Y1 - WDS_SPEECH_Y0))
    )

    state["wds_box_rect"] = pygame.Rect(
        int(state["WDS_W_PX"] * WDS_BOX_X0),
        int(state["WDS_H_PX"] * WDS_BOX_Y0),
        int(state["WDS_W_PX"] * (WDS_BOX_X1 - WDS_BOX_X0)),
        int(state["WDS_H_PX"] * (WDS_BOX_Y1 - WDS_BOX_Y0))
    )

    _tick()
    wds_rect = pygame.Rect(
        (W - state["WDS_W_PX"]) // 2,
        int(H * WDS_CENTER_Y)
        - state["WDS_H_PX"] // 2,
        state["WDS_W_PX"],
        state["WDS_H_PX"],
    )

    box_rel = state["wds_box_rect"]

    box_abs_x = wds_rect.x + box_rel.x
    box_abs_y = wds_rect.y + box_rel.y

    box_w = box_rel.width
    box_h = box_rel.height

    cells = []

    for row in range(2):
        for col in range(2):
            x = (
                box_abs_x
                + int(box_w * BTN_IN_BOX_X[col])
            )

            y = (
                box_abs_y
                + int(box_h * BTN_IN_BOX_Y[row])
            )

            cw = int(box_w * BTN_IN_BOX_W)
            ch = int(box_h * BTN_IN_BOX_H)

            cells.append(
                pygame.Rect(
                    x,
                    y,
                    cw,
                    ch
                )
            )

    options = list(current_question["options"])

    option_images = list(
        current_question.get("option_images", [])
    )

    correct_idx = current_question["correct"]

    perm = list(range(len(options)))
    random.shuffle(perm)

    shuffled_options = [
        options[i]
        for i in perm
    ]

    shuffled_images = [
        option_images[i]
        if i < len(option_images)
        else None
        for i in perm
    ]

    new_correct = perm.index(correct_idx)

    current_question["options"] = shuffled_options
    current_question["option_images"] = shuffled_images
    current_question["correct"] = new_correct

    answer_buttons = []

    for i, opt in enumerate(shuffled_options):
        if i >= len(cells):
            break

        _tick()

        dish_img_path = (
            shuffled_images[i]
            if i < len(shuffled_images)
            else None
        )

        answer_buttons.append(
            AnswerButton(
                cells[i],
                opt,
                state["fonts"]["answer"],
                i,
                None,
                dish_img_path
            )
        )

    return {
        "state": state,
        "questions": questions,
        "current_index": 0,
        "current_question": current_question,
        "answer_buttons": answer_buttons,
    }


def run_loop(screen, W, H, bundle):
    dbg("run_loop() iniciado")

    state = bundle["state"]
    questions = bundle["questions"]
    current_index = bundle["current_index"]
    current_question = bundle["current_question"]
    answer_buttons = bundle["answer_buttons"]

    score = 0
    money = 0
    happy_customers = 0
    served_customers = 0

    feedback = ""
    feedback_color = (255, 255, 255)
    answered = False
    answer_was_correct = False

    FADE_SPEED = 6.0

    backdrop = pygame.Surface((state["W"], state["H"]), pygame.SRCALPHA)
    backdrop.fill((0, 0, 0))
    backdrop_base_alpha = 220

    modal_open = False
    modal_alpha = 0.0
    modal_state = "closed"

    ingredient_boxes = []
    plate_evaluated = False

    confirm_button = None
    close_button = None

    wrong_modal_open = False
    wrong_modal_alpha = 0.0
    wrong_modal_state = "closed"
    wrong_selected_index = None

    correct_modal_open = False
    correct_modal_alpha = 0.0
    correct_modal_state = "closed"
    correct_points = 0

    completed_modal_open = False
    completed_modal_alpha = 0.0
    completed_modal_state = "closed"

    play_again_button = None
    main_menu_button = None

    ing_surf_cache = None
    wrong_surf_cache = None
    correct_surf_cache = None
    completed_surf_cache = None

    def get_wds_rect():
        w = state["W"]
        h = state["H"]
        wds_w = state["WDS_W_PX"]
        wds_h = state["WDS_H_PX"]
        cx = (w - wds_w) // 2
        cy = int(h * WDS_CENTER_Y) - wds_h // 2
        return pygame.Rect(cx, cy, wds_w, wds_h)

    def compute_answer_cells():
        wds_rect = get_wds_rect()
        box_rel = state["wds_box_rect"]
        box_abs_x = wds_rect.x + box_rel.x
        box_abs_y = wds_rect.y + box_rel.y + BTN_BOX_Y_OFFSET_PX
        box_w = box_rel.width
        box_h = box_rel.height

        cells = []
        for row in range(2):
            for col in range(2):
                x = box_abs_x + int(box_w * BTN_IN_BOX_X[col])
                y = box_abs_y + int(box_h * BTN_IN_BOX_Y[row])
                cw = int(box_w * BTN_IN_BOX_W)
                ch = int(box_h * BTN_IN_BOX_H)
                cells.append(pygame.Rect(x, y, cw, ch))
        return cells

    def open_modal():
        nonlocal modal_open, modal_alpha, modal_state, ingredient_boxes, plate_evaluated, confirm_button, close_button
        nonlocal ing_surf_cache
        modal_open = True
        modal_alpha = 0.0
        modal_state = "fading_in"
        plate_evaluated = False
        ingredient_boxes = []
        for i, ing_data in enumerate(current_question["ingredients"][:9]):
            ingredient_boxes.append(
                IngredientBox(
                    state["ing_cells"][i],
                    i,
                    ing_data["name"],
                    ing_data["image"],
                    state["fonts"]["ing_name"]
                )
            )
        confirm_button = ConfirmButton(state["ing_btn_area"], on_confirm)
        close_button = CloseButton(state["ing_close_rect"], close_modal)
        ing_surf_cache = state["ingredients_bg"].copy()

    def close_modal():
        nonlocal modal_state
        if modal_state != "fading_out":
            modal_state = "fading_out"

    def on_confirm():
        nonlocal plate_evaluated
        if not plate_evaluated:
            evaluate_plate()

    def evaluate_plate():
        nonlocal plate_evaluated
        nonlocal score, money, happy_customers

        correct_set = set(current_question["correct_ingredients"])
        gained = 0
        lost = 0

        for box in ingredient_boxes:
            if box.checked and box.index in correct_set:
                box.revealed = True
                gained += 1
            elif box.checked and box.index not in correct_set:
                box.revealed = False
                lost += 1
            elif not box.checked and box.index in correct_set:
                box.revealed = False
            else:
                box.revealed = True

        earned = gained * 30 - lost * 15
        if earned < 0:
            earned = 0
        money += earned
        score += gained * 50

        plate_evaluated = True

        if earned > 0:
            happy_customers += 1
            close_modal()
            open_correct_modal(earned)
        else:
            close_modal()
            open_wrong_modal(-1)

    def open_wrong_modal(selected_idx):
        nonlocal wrong_modal_open, wrong_modal_alpha, wrong_modal_state, wrong_selected_index
        nonlocal wrong_surf_cache
        wrong_modal_open = True
        wrong_modal_alpha = 0.0
        wrong_modal_state = "fading_in"
        wrong_selected_index = selected_idx
        wrong_surf_cache = state["wrong_bg"].copy()
        play_sound("wrong.ogg")

    def close_wrong_modal():
        nonlocal wrong_modal_state
        if wrong_modal_state != "fading_out":
            wrong_modal_state = "fading_out"

    def open_correct_modal(points):
        nonlocal correct_modal_open, correct_modal_alpha, correct_modal_state, correct_points
        nonlocal correct_surf_cache
        correct_modal_open = True
        correct_modal_alpha = 0.0
        correct_modal_state = "fading_in"
        correct_points = points
        correct_surf_cache = state["correct_bg"].copy()
        play_sound("correct.ogg")

    def close_correct_modal():
        nonlocal correct_modal_state
        if correct_modal_state != "fading_out":
            correct_modal_state = "fading_out"

    def open_completed_modal():
        nonlocal completed_modal_open, completed_modal_alpha, completed_modal_state
        nonlocal play_again_button, main_menu_button, completed_surf_cache
        completed_modal_open = True
        completed_modal_alpha = 0.0
        completed_modal_state = "fading_in"
        play_again_button = InvisibleButton(state["completed_btn_play_rect"], on_play_again)
        main_menu_button = InvisibleButton(state["completed_btn_menu_rect"], on_main_menu)
        completed_surf_cache = state["completed_bg"].copy()

    def close_completed_modal():
        nonlocal completed_modal_state
        if completed_modal_state != "fading_out":
            completed_modal_state = "fading_out"

    def on_play_again():
        nonlocal score, money, happy_customers, served_customers, current_index, current_question, answer_buttons
        score = 0
        money = 0
        happy_customers = 0
        served_customers = 0
        current_index = 0
        random.shuffle(questions)
        close_completed_modal()
        load_question(0)

    def on_main_menu():
        nonlocal running
        close_completed_modal()
        running = False

    def load_question(idx):
        nonlocal current_question, answer_buttons, feedback, answered, answer_was_correct
        if idx >= len(questions):
            current_question = None
            open_completed_modal()
            return
        current_question = questions[idx]
        answered = False
        answer_was_correct = False
        feedback = ""

        cust_path = current_question.get("customer_image")
        state["wds_img"] = load_wds_image(cust_path, W, H)
        state["WDS_W_PX"] = state["wds_img"].get_width()
        state["WDS_H_PX"] = state["wds_img"].get_height()

        state["wds_speech_rect"] = pygame.Rect(
            int(state["WDS_W_PX"] * WDS_SPEECH_X0),
            int(state["WDS_H_PX"] * WDS_SPEECH_Y0),
            int(state["WDS_W_PX"] * (WDS_SPEECH_X1 - WDS_SPEECH_X0)),
            int(state["WDS_H_PX"] * (WDS_SPEECH_Y1 - WDS_SPEECH_Y0))
        )

        state["wds_box_rect"] = pygame.Rect(
            int(state["WDS_W_PX"] * WDS_BOX_X0),
            int(state["WDS_H_PX"] * WDS_BOX_Y0),
            int(state["WDS_W_PX"] * (WDS_BOX_X1 - WDS_BOX_X0)),
            int(state["WDS_H_PX"] * (WDS_BOX_Y1 - WDS_BOX_Y0))
        )

        cells = compute_answer_cells()

        options = list(current_question["options"])
        option_images = list(current_question.get("option_images", []))
        correct_idx = current_question["correct"]

        perm = list(range(len(options)))
        random.shuffle(perm)
        shuffled_options = [options[i] for i in perm]
        shuffled_images = [
            option_images[i] if i < len(option_images) else None
            for i in perm
        ]
        new_correct = perm.index(correct_idx)

        current_question["options"] = shuffled_options
        current_question["option_images"] = shuffled_images
        current_question["correct"] = new_correct

        answer_buttons = []
        for i, opt in enumerate(shuffled_options):
            if i >= len(cells):
                break
            dish_img_path = shuffled_images[i] if i < len(shuffled_images) else None
            answer_buttons.append(
                AnswerButton(cells[i], opt, state["fonts"]["answer"], i, on_answer, dish_img_path)
            )

    def on_answer(index):
        nonlocal score, money, answered, feedback, feedback_color, answer_was_correct, served_customers
        if answered:
            return
        answered = True
        served_customers += 1
        for btn in answer_buttons:
            if btn.index == index:
                btn.selected = (index == current_question["correct"])
            else:
                btn.selected = None

        if index == current_question["correct"]:
            score += 100
            money += 20
            answer_was_correct = True
            feedback = ""
            feedback_color = (120, 255, 140)
            open_modal()
        else:
            answer_was_correct = False
            feedback = ""
            feedback_color = (255, 120, 120)
            open_wrong_modal(index)

    def next_question():
        nonlocal current_index, current_question
        current_index += 1
        if current_index >= len(questions):
            current_question = None
            open_completed_modal()
        else:
            load_question(current_index)

    for btn in answer_buttons:
        btn.callback = on_answer

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if completed_modal_open and completed_modal_state != "fading_out":
                    continue
                if wrong_modal_open and wrong_modal_state != "fading_out":
                    close_wrong_modal()
                    continue
                if correct_modal_open and correct_modal_state != "fading_out":
                    close_correct_modal()
                    continue

                if event.key == pygame.K_ESCAPE:
                    if modal_open and modal_state != "fading_out":
                        close_modal()
                    else:
                        running = False

                elif current_question is not None:
                    if modal_open and modal_state == "open":
                        if event.key == pygame.K_RETURN and not plate_evaluated:
                            evaluate_plate()
                        elif event.key == pygame.K_SPACE and plate_evaluated:
                            close_modal()
                else:
                    if event.key == pygame.K_RETURN:
                        running = False

            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and event.button == 1:
                if completed_modal_open and completed_modal_state != "fading_out":
                    if play_again_button:
                        play_again_button.handle_event(event)
                    if main_menu_button:
                        main_menu_button.handle_event(event)
                    continue

                if wrong_modal_open and wrong_modal_state != "fading_out":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        close_wrong_modal()
                    continue

                if correct_modal_open and correct_modal_state != "fading_out":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        close_correct_modal()
                    continue

                if not modal_open:
                    if current_question and not answered:
                        for btn in answer_buttons:
                            btn.handle_event(event)
                else:
                    if modal_state == "open":
                        if not plate_evaluated:
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if not state["ing_modal_rect"].collidepoint(event.pos):
                                    close_modal()
                                    continue

                            for box in ingredient_boxes:
                                box.handle_event(event)
                            if confirm_button:
                                confirm_button.handle_event(event)
                            if close_button:
                                close_button.handle_event(event)

        if modal_state == "fading_in":
            modal_alpha = min(1.0, modal_alpha + FADE_SPEED * dt)
            if modal_alpha >= 1.0:
                modal_state = "open"
        elif modal_state == "fading_out":
            modal_alpha = max(0.0, modal_alpha - FADE_SPEED * dt)
            if modal_alpha <= 0.0:
                modal_state = "closed"
                modal_open = False
                ing_surf_cache = None
                if current_question is not None and not plate_evaluated and answered and answer_was_correct:
                    plate_evaluated = True
                    open_correct_modal(0)

        if wrong_modal_state == "fading_in":
            wrong_modal_alpha = min(1.0, wrong_modal_alpha + FADE_SPEED * dt)
            if wrong_modal_alpha >= 1.0:
                wrong_modal_state = "open"
        elif wrong_modal_state == "fading_out":
            wrong_modal_alpha = max(0.0, wrong_modal_alpha - FADE_SPEED * dt)
            if wrong_modal_alpha <= 0.0:
                wrong_modal_state = "closed"
                wrong_modal_open = False
                wrong_surf_cache = None
                next_question()

        if correct_modal_state == "fading_in":
            correct_modal_alpha = min(1.0, correct_modal_alpha + FADE_SPEED * dt)
            if correct_modal_alpha >= 1.0:
                correct_modal_state = "open"
        elif correct_modal_state == "fading_out":
            correct_modal_alpha = max(0.0, correct_modal_alpha - FADE_SPEED * dt)
            if correct_modal_alpha <= 0.0:
                correct_modal_state = "closed"
                correct_modal_open = False
                correct_surf_cache = None
                next_question()

        if completed_modal_state == "fading_in":
            completed_modal_alpha = min(1.0, completed_modal_alpha + FADE_SPEED * dt)
            if completed_modal_alpha >= 1.0:
                completed_modal_state = "open"
        elif completed_modal_state == "fading_out":
            completed_modal_alpha = max(0.0, completed_modal_alpha - FADE_SPEED * dt)
            if completed_modal_alpha <= 0.0:
                completed_modal_state = "closed"
                completed_modal_open = False
                completed_surf_cache = None

        if current_question is not None and not modal_open and not wrong_modal_open and not correct_modal_open and not completed_modal_open:
            new_cells = compute_answer_cells()
            for btn, new_rect in zip(answer_buttons, new_cells):
                btn.rect = new_rect

        if not modal_open and not wrong_modal_open and not correct_modal_open and not completed_modal_open:
            if current_question and not answered:
                for btn in answer_buttons:
                    btn.update(mouse_pos)
                if any(btn.hovered for btn in answer_buttons):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif modal_open and not wrong_modal_open and not correct_modal_open and not completed_modal_open:
            if modal_state == "open" and not plate_evaluated:
                for box in ingredient_boxes:
                    box.update(mouse_pos)
                if confirm_button:
                    confirm_button.update(mouse_pos)
                if close_button:
                    close_button.update(mouse_pos)
                hovering = (
                    any(box.hovered for box in ingredient_boxes)
                    or (confirm_button and confirm_button.hovered)
                    or (close_button and close_button.hovered)
                )
                if hovering:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif completed_modal_open:
            if play_again_button:
                play_again_button.update(mouse_pos)
            if main_menu_button:
                main_menu_button.update(mouse_pos)
            if (play_again_button and play_again_button.hovered) or (main_menu_button and main_menu_button.hovered):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        screen.fill((0, 0, 0))

        if current_question is not None:
            screen.blit(state["serving_bg"], state["serve_rect"])

            s_rect = state["serve_rect"]

            if state["money_score_img"] is not None and state["ms_rect"] is not None:
                screen.blit(state["money_score_img"], state["ms_rect"].topleft)
                ms_font = state["fonts"]["money_score"]

                if state["ms_money_rect"] is not None:
                    money_surf = ms_font.render(f"${money}", True, (255, 255, 255))
                    money_rect = state["ms_money_rect"]
                    pad_px = int(MS_TEXT_PAD_PX * (money_rect.width / 1155))
                    text_x = money_rect.right - money_surf.get_width() - pad_px
                    text_y = money_rect.centery - money_surf.get_height() // 2
                    screen.blit(money_surf, (text_x, text_y))

                if state["ms_score_rect"] is not None:
                    score_surf = ms_font.render(f"{score}", True, (255, 255, 255))
                    score_rect = state["ms_score_rect"]
                    pad_px = int(MS_TEXT_PAD_PX * (score_rect.width / 1155))
                    text_x = score_rect.right - score_surf.get_width() - pad_px
                    text_y = score_rect.centery - score_surf.get_height() // 2
                    screen.blit(score_surf, (text_x, text_y))
            else:
                score_surf = state["fonts"]["ui"].render(f"Score: {score}", True, (255, 255, 255))
                money_surf = state["fonts"]["ui"].render(f"Money: ${money}", True, (255, 255, 255))
                screen.blit(score_surf, (s_rect.x + s_rect.width - score_surf.get_width() - int(s_rect.width * 0.03), s_rect.y + int(s_rect.height * 0.03)))
                screen.blit(money_surf, (s_rect.x + s_rect.width - money_surf.get_width() - int(s_rect.width * 0.03), s_rect.y + int(s_rect.height * 0.03) + score_surf.get_height() + 8))

            wds_rect = get_wds_rect()
            screen.blit(state["wds_img"], wds_rect.topleft)

            speech_rel = state["wds_speech_rect"]
            speech_abs = pygame.Rect(
                wds_rect.x + speech_rel.x,
                wds_rect.y + speech_rel.y,
                speech_rel.width,
                speech_rel.height
            )
            q_text = current_question["question"]
            max_text_w = speech_abs.width - 50
            lines = wrap_text(q_text, state["fonts"]["question"], max_text_w)
            line_h = state["fonts"]["question"].get_linesize()
            total_h = line_h * len(lines)
            y = speech_abs.centery - total_h // 2
            for line in lines:
                surf = state["fonts"]["question"].render(line, True, (30, 30, 30))
                screen.blit(surf, surf.get_rect(center=(speech_abs.centerx, y + line_h // 2)))
                y += line_h

            for btn in answer_buttons:
                btn.draw(screen)
        else:
            screen.blit(state["customer_bg"], state["cust_rect"])

        if feedback:
            max_fb_w = int(state["serve_rect"].width * 0.85)
            fb_lines = wrap_text(feedback, state["fonts"]["feedback"], max_fb_w)
            fy = state["serve_rect"].y + int(state["serve_rect"].height * 0.93)
            for line in fb_lines:
                fb_surf = state["fonts"]["feedback"].render(line, True, feedback_color)
                screen.blit(fb_surf, fb_surf.get_rect(center=(state["serve_rect"].x + state["serve_rect"].width // 2, fy)))
                fy += fb_surf.get_height() + 4

        if modal_open:
            backdrop.set_alpha(int(backdrop_base_alpha * modal_alpha))
            screen.blit(backdrop, (0, 0))

            if ing_surf_cache is not None:
                ing_surf_cache.set_alpha(int(255 * modal_alpha))
                screen.blit(ing_surf_cache, state["ing_modal_rect"].topleft)

            if modal_alpha > 0.5:
                plate_name = current_question.get("plate_name", "")
                title_text = f'Prepare "{plate_name}"'
                title_rect = state["ing_title_rect"]
                title_text = truncate_with_ellipsis(title_text, state["fonts"]["ing_title"], title_rect.width)
                title_surf = state["fonts"]["ing_title"].render(title_text, True, (255, 255, 255))
                title_pos = title_surf.get_rect(midleft=(title_rect.left, title_rect.centery))
                screen.blit(title_surf, title_pos)

                for box in ingredient_boxes:
                    box.draw(screen)

                if confirm_button and not plate_evaluated:
                    confirm_button.draw(screen)

                if close_button:
                    close_button.draw(screen)

                m_rect = state["ing_modal_rect"]
                if not plate_evaluated:
                    hint = state["fonts"]["ui"].render("Check the ingredients and press CONFIRM", True, (220, 220, 220))
                    screen.blit(hint, hint.get_rect(center=(m_rect.centerx, m_rect.bottom - int(m_rect.height * 0.03))))

        if wrong_modal_open and state["wrong_bg"] is not None:
            backdrop.set_alpha(int(backdrop_base_alpha * wrong_modal_alpha))
            screen.blit(backdrop, (0, 0))

            if wrong_surf_cache is not None:
                wrong_surf_cache.set_alpha(int(255 * wrong_modal_alpha))
                screen.blit(wrong_surf_cache, state["wrong_rect"].topleft)

            if wrong_modal_alpha > 0.5:
                if state["wrong_wanted_rect"] is not None:
                    wanted_text = current_question["keyword"].capitalize()
                    draw_text_centered(
                        screen,
                        wanted_text,
                        state["fonts"]["wrong"],
                        state["wrong_wanted_rect"],
                        (255, 255, 255),
                        padding_x=int(state["wrong_wanted_rect"].width * WRONG_TEXT_PADDING),
                        padding_y=int(state["wrong_wanted_rect"].height * 0.10),
                    )

                if state["wrong_served_rect"] is not None:
                    if wrong_selected_index is not None and wrong_selected_index >= 0:
                        served_text = current_question["options"][wrong_selected_index]
                    else:
                        served_text = "The wrong ingredients"
                    draw_text_centered(
                        screen,
                        served_text,
                        state["fonts"]["wrong"],
                        state["wrong_served_rect"],
                        (255, 255, 255),
                        padding_x=int(state["wrong_served_rect"].width * WRONG_TEXT_PADDING),
                        padding_y=int(state["wrong_served_rect"].height * 0.10),
                    )

                if state["wrong_just_rect"] is not None:
                    just_text = current_question.get("explanation", "")
                    draw_text_centered(
                        screen,
                        just_text,
                        state["fonts"]["wrong_just"],
                        state["wrong_just_rect"],
                        (255, 255, 255),
                        padding_x=int(state["wrong_just_rect"].width * WRONG_TEXT_PADDING),
                        padding_y=int(state["wrong_just_rect"].height * 0.08),
                        line_spacing=6,
                    )

                hint = state["fonts"]["ui"].render("Click anywhere or press any key to continue", True, (220, 220, 220))
                screen.blit(hint, hint.get_rect(center=(state["W"] // 2, state["H"] - 30)))

        if correct_modal_open and state["correct_bg"] is not None:
            backdrop.set_alpha(int(backdrop_base_alpha * correct_modal_alpha))
            screen.blit(backdrop, (0, 0))

            if correct_surf_cache is not None:
                correct_surf_cache.set_alpha(int(255 * correct_modal_alpha))
                screen.blit(correct_surf_cache, state["correct_rect"].topleft)

            if correct_modal_alpha > 0.5:
                if state["correct_text_rect"] is not None:
                    explanation = current_question.get("explanation", "")
                    keyword = current_question["keyword"]
                    vocab_text = f'"{keyword}" — {explanation}'
                    draw_text_centered(
                        screen,
                        vocab_text,
                        state["fonts"]["correct_text"],
                        state["correct_text_rect"],
                        (255, 255, 255),
                        padding_x=int(state["correct_text_rect"].width * CORRECT_TEXT_PADDING),
                        padding_y=int(state["correct_text_rect"].height * 0.08),
                        line_spacing=6,
                    )

                if state["correct_btn_rect"] is not None and correct_points > 0:
                    btn_rect = state["correct_btn_rect"]
                    pad_x = int(btn_rect.width * CORRECT_BTN_PAD_X)
                    points_text = f"+{correct_points} POINTS"
                    btn_font = state["fonts"]["correct_btn"]
                    points_text = truncate_with_ellipsis(
                        points_text, btn_font, btn_rect.width - pad_x * 2
                    )
                    surf = btn_font.render(points_text, True, (255, 255, 255))
                    rect = surf.get_rect(center=btn_rect.center)
                    screen.blit(surf, rect)

                hint = state["fonts"]["ui"].render("Click anywhere or press any key to continue", True, (220, 220, 220))
                screen.blit(hint, hint.get_rect(center=(state["W"] // 2, state["H"] - 30)))

        if completed_modal_open and state["completed_bg"] is not None:
            backdrop.set_alpha(int(backdrop_base_alpha * completed_modal_alpha))
            screen.blit(backdrop, (0, 0))

            if completed_surf_cache is not None:
                completed_surf_cache.set_alpha(int(255 * completed_modal_alpha))
                screen.blit(completed_surf_cache, state["completed_rect"].topleft)

            if completed_modal_alpha > 0.5:
                labels = ["", "", "", ""]
                values = [str(served_customers), str(happy_customers), f"${money}", str(score)]

                for i in range(4):
                    if i >= len(state["completed_lines_rects"]):
                        break
                    label_rect = state["completed_lines_rects"][i]
                    value_rect = state["completed_values_rects"][i]

                    label_surf = state["fonts"]["completed_label"].render(labels[i], True, (255, 255, 255))
                    label_pos = label_surf.get_rect(midleft=(label_rect.left, label_rect.centery))
                    screen.blit(label_surf, label_pos)

                    value_surf = state["fonts"]["completed_value"].render(values[i], True, (255, 255, 255))
                    value_pos = value_surf.get_rect(midleft=(value_rect.left, value_rect.centery))
                    screen.blit(value_surf, value_pos)

                if state["completed_rightbox_rect"] is not None:
                    right_box = state["completed_rightbox_rect"]
                    rank_text, star_count = get_rank_and_stars(score)

                    rank_surf = state["fonts"]["rank"].render(rank_text, True, (255, 255, 255))
                    rank_rect = rank_surf.get_rect(center=(right_box.centerx, right_box.top + int(right_box.height * COMPLETED_RANK_Y_RATIO)))
                    screen.blit(rank_surf, rank_rect)

                    max_star_w = int(right_box.width * 0.80)
                    scaled = get_star_scaled(star_count, max_star_w)
                    if scaled is not None:
                        star_rect = scaled.get_rect(center=(right_box.centerx, right_box.top + int(right_box.height * COMPLETED_STAR_Y_RATIO)))
                        screen.blit(scaled, star_rect)

                if play_again_button:
                    play_again_button.draw(screen)
                if main_menu_button:
                    main_menu_button.draw(screen)

        pygame.display.flip()

    stop_background_music()
    dbg("run_loop() finalizado")


def run(screen=None, W=None, H=None):
    global MIXER_OK

    if screen is None:
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.display.init()
        pygame.font.init()
        try:
            pygame.mixer.init()
            MIXER_OK = True
        except Exception:
            MIXER_OK = False
        info = pygame.display.Info()
        W, H = info.current_w, info.current_h
        screen = pygame.display.set_mode(
            (W, H),
            pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF,
            vsync=1,
        )
        pygame.display.set_caption("Flavor Chef")
    else:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            MIXER_OK = True
        except Exception:
            MIXER_OK = False

    start_background_music()
    bundle = build_game_state(screen, W, H)
    run_loop(screen, W, H, bundle)


if __name__ == "__main__":
    run()