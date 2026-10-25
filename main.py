import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Меню")
clock = pygame.time.Clock()

# --- Состояние игры ---
state = "menu"   # "menu" | "game"

# --- Переменные ---
Bg_flag = True

Px = WIDTH // 2 - 200
Py = HEIGHT // 2
Pr = 10
Ps = 5

# Цвета
BG_COLOR_TEMA_MENU_1 = (20, 20, 20)
BG_COLOR_TEMA_MENU_2 = (255, 255, 255)
BG_COLOR_GAME = (30, 40, 50)
BUTTON_COLOR_MENU = (30, 144, 255)
HOVER_COLOR_MENU = (65, 105, 225)
DARK_OVERLAY_MENU = (0, 0, 0, 150)
PLAYER_COLOR = (255, 80, 80)

# Шрифты
font_large = pygame.font.Font(None, 60)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 32)


class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        current_color = HOVER_COLOR_MENU if self.is_hovered else BUTTON_COLOR_MENU
        pygame.draw.rect(surface, current_color, self.rect, width=4, border_radius=12)
        text_surf = self.font.render(self.text, True, current_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                return True
        return False


class Slider:
    def __init__(self, x, y, width, text, value=50):
        self.rect = pygame.Rect(x, y, width, 10)
        self.text = text
        self.value = value
        self.dragging = False
        self.handle_radius = 10
        self.handle_pos = (x + (width * value / 100), y + 5)

    def draw(self, surface):
        text_surf = font_small.render(self.text, True, BUTTON_COLOR_MENU)
        surface.blit(text_surf, (self.rect.x, self.rect.y - 25))
        pygame.draw.rect(surface, (200, 200, 200), self.rect, border_radius=5)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y,
                                self.handle_pos[0] - self.rect.x, 10)
        pygame.draw.rect(surface, BUTTON_COLOR_MENU, fill_rect, border_radius=5)
        pygame.draw.circle(surface, BUTTON_COLOR_MENU,
                           (int(self.handle_pos[0]), int(self.handle_pos[1])),
                           self.handle_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if (abs(mx - self.handle_pos[0]) < 20 and
                    abs(my - self.handle_pos[1]) < 20) or \
                    self.rect.inflate(0, 20).collidepoint(mx, my):
                self.dragging = True
                nx = max(self.rect.x, min(mx, self.rect.x + self.rect.width))
                self.value = int((nx - self.rect.x) / self.rect.width * 100)
                self.handle_pos = (nx, self.rect.y + 5)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            nx = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.value = int((nx - self.rect.x) / self.rect.width * 100)
            self.handle_pos = (nx, self.rect.y + 5)


class RoundTable:
    def __init__(self, x, y, radius, color=(139, 90, 43), border_color=(80, 50, 20)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.border_color = border_color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, self.border_color, (int(self.x), int(self.y)), self.radius, 3)

    def collide_and_resolve(self, px, py, pr):
        dx = px - self.x
        dy = py - self.y
        dist_sq = dx * dx + dy * dy
        min_dist = pr + self.radius
        if dist_sq >= min_dist * min_dist:
            return px, py
        dist = math.sqrt(dist_sq)
        if dist == 0:
            return self.x + min_dist, self.y
        nx = dx / dist
        ny = dy / dist
        return self.x + nx * min_dist, self.y + ny * min_dist

    def point_inside(self, px, py):
        dx = px - self.x
        dy = py - self.y
        return dx * dx + dy * dy <= self.radius * self.radius


# --- Меню ---
btn_tema = Button(690, 10, 100, 50, "Тема", font_small)
btn_play = Button(WIDTH // 2 - 150, 150, 300, 80, "PLAY", font_large)
btn_save = Button(WIDTH // 2 - 270, 300, 250, 80, "Сохранение", font_medium)
btn_settings = Button(WIDTH // 2 + 20, 300, 250, 80, "Настройки", font_medium)
menu_buttons = [btn_play, btn_save, btn_settings, btn_tema]

# --- Настройки ---
SETTINGS_W, SETTINGS_H = 400, 350
SETTINGS_X = (WIDTH - SETTINGS_W) // 2
SETTINGS_Y = (HEIGHT - SETTINGS_H) // 2
btn_close = Button(SETTINGS_X + SETTINGS_W - 55, SETTINGS_Y + 10, 45, 45, "X", font_small)
slider_music = Slider(SETTINGS_X + 50, SETTINGS_Y + 100, 300, "Музыка")
slider_sfx = Slider(SETTINGS_X + 50, SETTINGS_Y + 200, 300, "Звуки")
show_settings = False

# --- Кнопка настроек внутри игры ---
btn_settings_game = Button(WIDTH - 160, 10, 150, 50, "Настройки", font_small)

# --- Столы ---
tables = [
    RoundTable(WIDTH // 2, HEIGHT // 4, 60),
    RoundTable(WIDTH-(WIDTH // 4), HEIGHT // 4, 60),
    RoundTable(WIDTH // 4, HEIGHT // 4, 60),

    #R
    RoundTable(WIDTH // 2, HEIGHT-(HEIGHT // 4), 60),
    RoundTable(WIDTH-(WIDTH // 4), HEIGHT-(HEIGHT // 4), 60),
    RoundTable(WIDTH // 4, HEIGHT-(HEIGHT // 4), 60),
]

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---------------- МЕНЮ ----------------
        if state == "menu":
            if not show_settings:
                if btn_play.check_click(mouse_pos, event):
                    state = "game"
                if btn_save.check_click(mouse_pos, event):
                    print("Нажата кнопка СОХРАНЕНИЕ!")
                if btn_settings.check_click(mouse_pos, event):
                    show_settings = True
                if btn_tema.check_click(mouse_pos, event):
                    Bg_flag = not Bg_flag
            else:
                if btn_close.check_click(mouse_pos, event):
                    show_settings = False
                slider_music.handle_event(event)
                slider_sfx.handle_event(event)

        # ---------------- ИГРА ----------------
        elif state == "game":
            if not show_settings:
                if btn_settings_game.check_click(mouse_pos, event):
                    show_settings = True
            else:
                if btn_close.check_click(mouse_pos, event):
                    show_settings = False
                slider_music.handle_event(event)
                slider_sfx.handle_event(event)

    # ---------------- ДВИЖЕНИЕ ----------------
    if state == "game" and not show_settings:
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= Ps
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += Ps
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= Ps
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += Ps
        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071
        Px = max(Pr, min(Px + dx, WIDTH - Pr))
        Py = max(Pr, min(Py + dy, HEIGHT - Pr))

        for table in tables:
            Px, Py = table.collide_and_resolve(Px, Py, Pr)

    # ---------------- ОТРИСОВКА ----------------
    if state == "menu":
        screen.fill(BG_COLOR_TEMA_MENU_1 if Bg_flag else BG_COLOR_TEMA_MENU_2)

        for btn in menu_buttons:
            btn.check_hover(mouse_pos)
            btn.draw(screen)

        if show_settings:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(DARK_OVERLAY_MENU)
            screen.blit(overlay, (0, 0))

            settings_rect = pygame.Rect(SETTINGS_X, SETTINGS_Y, SETTINGS_W, SETTINGS_H)
            pygame.draw.rect(screen, BG_COLOR_TEMA_MENU_1, settings_rect, border_radius=15)
            pygame.draw.rect(screen, BUTTON_COLOR_MENU, settings_rect, width=5, border_radius=15)

            title_surf = font_large.render("Настройки", True, BUTTON_COLOR_MENU)
            screen.blit(title_surf, (SETTINGS_X + 20, SETTINGS_Y + 20))

            btn_close.check_hover(mouse_pos)
            btn_close.draw(screen)
            slider_music.draw(screen)
            slider_sfx.draw(screen)

    elif state == "game":
        screen.fill(BG_COLOR_GAME)

        for table in tables:
            table.draw(screen)

        pygame.draw.circle(screen, PLAYER_COLOR, (int(Px), int(Py)), Pr)

        btn_settings_game.check_hover(mouse_pos)
        btn_settings_game.draw(screen)


        if show_settings:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(DARK_OVERLAY_MENU)
            screen.blit(overlay, (0, 0))

            settings_rect = pygame.Rect(SETTINGS_X, SETTINGS_Y, SETTINGS_W, SETTINGS_H)
            pygame.draw.rect(screen, BG_COLOR_TEMA_MENU_1, settings_rect, border_radius=15)
            pygame.draw.rect(screen, BUTTON_COLOR_MENU, settings_rect, width=5, border_radius=15)

            title_surf = font_large.render("Настройки", True, BUTTON_COLOR_MENU)
            screen.blit(title_surf, (SETTINGS_X + 20, SETTINGS_Y + 20))

            btn_close.check_hover(mouse_pos)
            btn_close.draw(screen)
            slider_music.draw(screen)
            slider_sfx.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()