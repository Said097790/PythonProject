import pygame
import sys

# 1. Инициализация
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Меню")

# Цвета
BG_COLOR = (255, 255, 255)       
BUTTON_COLOR = (30, 144, 255)    
HOVER_COLOR = (65, 105, 225)     
DARK_OVERLAY = (0, 0, 0, 150)    

# Шрифты
font_large = pygame.font.Font(None, 60)   
font_medium = pygame.font.Font(None, 36)  
font_small = pygame.font.Font(None, 32)   

# --- Класс кнопки ---
class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font 
        self.is_hovered = False

    def draw(self, surface):
        current_color = HOVER_COLOR if self.is_hovered else BUTTON_COLOR
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

# --- Класс ползунка ---
class Slider:
    def __init__(self, x, y, width, text, value=50):
        self.rect = pygame.Rect(x, y, width, 10)
        self.text = text
        self.value = value
        self.dragging = False
        self.handle_radius = 10
        self.handle_pos = (x + (width * value / 100), y + 5)

    def draw(self, surface):
        text_surf = font_small.render(self.text, True, BUTTON_COLOR)
        surface.blit(text_surf, (self.rect.x, self.rect.y - 25))
        
        pygame.draw.rect(surface, (200, 200, 200), self.rect, border_radius=5)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, self.handle_pos[0] - self.rect.x, 10)
        pygame.draw.rect(surface, BUTTON_COLOR, fill_rect, border_radius=5)
        pygame.draw.circle(surface, BUTTON_COLOR, (int(self.handle_pos[0]), int(self.handle_pos[1])), self.handle_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            if abs(mouse_x - self.handle_pos[0]) < 20 and abs(mouse_y - self.handle_pos[1]) < 20:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.value = int((new_x - self.rect.x) / self.rect.width * 100)
            self.handle_pos = (new_x, self.rect.y + 5)

# --- Главное меню ---
# Верхняя кнопка
btn_play = Button(WIDTH//2 - 150, 150, 300, 80, "PLAY", font_large)


btn_save = Button(WIDTH//2 - 270, 300, 250, 80, "Сохранение", font_medium)
btn_settings = Button(WIDTH//2 + 20, 300, 250, 80, "Настройки", font_medium)

menu_buttons = [btn_play, btn_save, btn_settings]

# --- Настройки игры ---
SETTINGS_W, SETTINGS_H = 400, 350
SETTINGS_X = (WIDTH - SETTINGS_W) // 2
SETTINGS_Y = (HEIGHT - SETTINGS_H) // 2

btn_close = Button(SETTINGS_X + SETTINGS_W - 50, SETTINGS_Y + 10, 40, 40, "X", font_medium)
slider_music = Slider(SETTINGS_X + 50, SETTINGS_Y + 100, 300, "Музыка")
slider_sfx = Slider(SETTINGS_X + 50, SETTINGS_Y + 200, 300, "Звуки")

show_settings = False

# Главный цикл игры
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if not show_settings:
            if btn_play.check_click(mouse_pos, event):
                print("Нажата кнопка PLAY!")
            if btn_save.check_click(mouse_pos, event):
                print("Нажата кнопка СОХРАНЕНИЕ!")
            if btn_settings.check_click(mouse_pos, event):
                show_settings = True 
        else:
            if btn_close.check_click(mouse_pos, event):
                show_settings = False 
            
            slider_music.handle_event(event)
            slider_sfx.handle_event(event)

    # --- Отрисовка ---
    screen.fill(BG_COLOR)
    
    for btn in menu_buttons:
        btn.check_hover(mouse_pos)
        btn.draw(screen)

    if show_settings:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(DARK_OVERLAY)
        screen.blit(overlay, (0, 0))

        settings_rect = pygame.Rect(SETTINGS_X, SETTINGS_Y, SETTINGS_W, SETTINGS_H)
        pygame.draw.rect(screen, BG_COLOR, settings_rect, border_radius=15)
        pygame.draw.rect(screen, BUTTON_COLOR, settings_rect, width=5, border_radius=15)

        title_surf = font_large.render("Настройки", True, BUTTON_COLOR)
        screen.blit(title_surf, (SETTINGS_X + 20, SETTINGS_Y + 20))

        btn_close.check_hover(mouse_pos)
        btn_close.draw(screen)
        
        slider_music.draw(screen)
        slider_sfx.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
