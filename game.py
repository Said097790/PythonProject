import pygame
import sys
import math
import random
import json
import os

pygame.init()

infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Карьерный Дрейф")
clock = pygame.time.Clock()

state = "menu"
Bg_flag = True

Px = WIDTH // 2
Py = HEIGHT // 2
Pr = 15
Ps = 5

BG_COLOR_TEMA_MENU_1 = (20, 20, 20)
BG_COLOR_TEMA_MENU_2 = (255, 255, 255)
BUTTON_COLOR_MENU = (30, 144, 255)
HOVER_COLOR_MENU = (65, 105, 225)
DARK_OVERLAY_MENU = (0, 0, 0, 150)

PLAYER_COLOR = (255, 80, 80)
BG_COLOR_STREET = (50, 60, 70)
BG_COLOR_RESTAURANT = (200, 180, 150)
WALL_COLOR = (100, 80, 60)
DOOR_COLOR = (139, 69, 19)
TRASH_COLOR = (100, 100, 100)
PALETTE_GARBAGEWE = [
    (10, 10, 10), (30, 30, 30), (50, 50, 50), (70, 70, 70), (80, 80, 80),
    (100, 100, 100), (120, 120, 120), (140, 140, 140), (160, 160, 160),
    (180, 180, 180), (200, 200, 200), (220, 220, 220), (240, 240, 240),
]
RED_COLOR = (220, 20, 60)

font_large = pygame.font.Font(None, 80)
font_medium = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 32)

base_shift_duration = 60
shift_time_left = base_shift_duration

def get_shift_duration(shift):
    return base_shift_duration + (shift - 1) * 20


# =========================================================
# --- СОХРАНЕНИЯ ---
# =========================================================
def get_save_file(slot):
    return f"save_slot_{slot}.json"

def save_game(slot, shift, xp, money, market_data):
    data = {"shift": shift, "xp": xp, "money": money, "market_data": market_data}
    path = get_save_file(slot)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, path)
    except OSError:
        pass

def load_game(slot):
    path = get_save_file(slot)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                return (data.get("shift", 1),
                        data.get("xp", 0),
                        data.get("money", 0),
                        data.get("market_data", []))
        except (json.JSONDecodeError, OSError):
            return None, None, None, None
    return None, None, None, None

def delete_save(slot):
    path = get_save_file(slot)
    if os.path.exists(path):
        os.remove(path)

current_slot = None
current_shift = 1
player_xp = 0
player_money = 0
market_data = []
target_xp = 50 + (current_shift * 30)
game_over_reason = ""
garbage_spawn_delay = 0
max_garbage_on_map = 3 + current_shift

GARBAGE_SPAWN_INTERVAL = 2.0


# =========================================================
# --- ВСПОМОГАТЕЛЬНЫЕ ---
# =========================================================
def draw_text_wrapped(surface, text, font, color, x, y, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        if font.size(test_line)[0] > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y + i * font.get_linesize()))


# =========================================================
# --- КЛАССЫ ---
# =========================================================
class Button:
    def __init__(self, x, y, width, height, text, font, color=BUTTON_COLOR_MENU, hover_color=HOVER_COLOR_MENU):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
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
        surface.blit(text_surf, (self.rect.x, self.rect.y - 35))
        pygame.draw.rect(surface, (200, 200, 200), self.rect, border_radius=5)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, self.handle_pos[0] - self.rect.x, 10)
        pygame.draw.rect(surface, BUTTON_COLOR_MENU, fill_rect, border_radius=5)
        pygame.draw.circle(surface, BUTTON_COLOR_MENU, (int(self.handle_pos[0]), int(self.handle_pos[1])), self.handle_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if (abs(mx - self.handle_pos[0]) < 20 and abs(my - self.handle_pos[1]) < 20) or self.rect.inflate(0, 20).collidepoint(mx, my):
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


class MovingFloor:
    def __init__(self, width, height, plank_height=60, plank_width=300, speed=80):
        self.width, self.height = width, height
        self.plank_height, self.plank_width = plank_height, plank_width
        self.speed, self.offset = speed, 0

    def update(self, dt):
        self.offset += self.speed * dt
        if self.offset >= self.plank_width:
            self.offset = 0

    def draw(self, surface, is_light_theme):
        if is_light_theme:
            color1, color2, line_color = (210, 180, 140), (190, 160, 120), (160, 130, 90)
        else:
            color1, color2, line_color = (60, 40, 30), (45, 30, 20), (20, 10, 5)
        for row in range(-1, (self.height // self.plank_height) + 2):
            y = row * self.plank_height
            color = color1 if row % 2 == 0 else color2
            for col in range(-2, (self.width // self.plank_width) + 2):
                shift = (self.plank_width // 2) if row % 2 != 0 else 0
                x = col * self.plank_width + shift + self.offset
                pygame.draw.rect(surface, color, (x, y, self.plank_width, self.plank_height))
                pygame.draw.rect(surface, line_color, (x, y, self.plank_width, self.plank_height), 2)


class RoundTable:
    def __init__(self, x, y, radius, color=(139, 90, 43)):
        self.x, self.y, self.radius = x, y, radius
        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (80, 50, 20), (int(self.x), int(self.y)), self.radius, 3)

    def collide_and_resolve(self, px, py, pr):
        dx, dy = px - self.x, py - self.y
        dist = math.hypot(dx, dy)
        min_dist = pr + self.radius
        if dist < min_dist:
            if dist == 0: return self.x + min_dist, self.y
            return self.x + (dx / dist) * min_dist, self.y + (dy / dist) * min_dist
        return px, py


class Garbage:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 15
        self.collected = False
        self.pieces = []
        count = random.randint(3, 6)
        for _ in range(count):
            ox = random.randint(-9, 9)
            oy = random.randint(-9, 9)
            r = random.randint(5, 9)
            color = random.choice(PALETTE_GARBAGEWE)
            self.pieces.append((ox, oy, r, color))

    def draw(self, surface):
        if self.collected:
            return
        for ox, oy, r, color in self.pieces:
            pygame.draw.circle(surface, color, (int(self.x + ox), int(self.y + oy)), r)
            pygame.draw.circle(surface, (0, 0, 0), (int(self.x + ox), int(self.y + oy)), r, 2)


def draw_carried_garbage(surface, px, py, count, colors):
    if count <= 0:
        return
    shown = min(count, 5)
    base_x = px
    base_y = py - 22
    spacing = 9
    total_w = (shown - 1) * spacing
    start_x = base_x - total_w // 2
    for i in range(shown):
        color = colors[i] if i < len(colors) else (80, 80, 80)
        ox = start_x + i * spacing
        oy = base_y - (3 if i % 2 == 0 else 0)
        pygame.draw.circle(surface, color, (int(ox), int(oy)), 5)
        pygame.draw.circle(surface, (0, 0, 0), (int(ox), int(oy)), 5, 1)
    if count > 5:
        extra = font_small.render(f"+{count - 5}", True, (255, 255, 255))
        surface.blit(extra, (base_x + total_w // 2 + 10, base_y - 10))


# =========================================================
# --- ИНТЕРФЕЙС ---
# =========================================================
btn_play = Button(WIDTH // 2 - 200, HEIGHT // 2 - 150, 400, 100, "PLAY", font_large)
btn_save = Button(WIDTH // 2 - 350, HEIGHT // 2 + 50, 300, 80, "Сохранение", font_medium)
btn_settings = Button(WIDTH // 2 + 50, HEIGHT // 2 + 50, 300, 80, "Настройки", font_medium)
btn_tema = Button(WIDTH - 150, 20, 120, 60, "Тема", font_small)
menu_buttons = [btn_play, btn_save, btn_settings, btn_tema]

btn_slot1 = Button(WIDTH // 2 - 250, HEIGHT // 2 - 100, 400, 80, "Слот 1", font_medium)
btn_slot2 = Button(WIDTH // 2 - 250, HEIGHT // 2, 400, 80, "Слот 2", font_medium)
btn_slot3 = Button(WIDTH // 2 - 250, HEIGHT // 2 + 100, 400, 80, "Слот 3", font_medium)
slot_buttons = [btn_slot1, btn_slot2, btn_slot3]

btn_del1 = Button(WIDTH // 2 + 170, HEIGHT // 2 - 100, 80, 80, "X", font_medium, color=RED_COLOR, hover_color=(255, 50, 50))
btn_del2 = Button(WIDTH // 2 + 170, HEIGHT // 2, 80, 80, "X", font_medium, color=RED_COLOR, hover_color=(255, 50, 50))
btn_del3 = Button(WIDTH // 2 + 170, HEIGHT // 2 + 100, 80, 80, "X", font_medium, color=RED_COLOR, hover_color=(255, 50, 50))
delete_buttons = [btn_del1, btn_del2, btn_del3]

btn_back = Button(50, 50, 150, 60, "Назад", font_medium)

SETTINGS_W, SETTINGS_H = 500, 400
SETTINGS_X, SETTINGS_Y = (WIDTH - SETTINGS_W) // 2, (HEIGHT - SETTINGS_H) // 2
btn_close = Button(SETTINGS_X + SETTINGS_W - 60, SETTINGS_Y + 10, 50, 50, "X", font_small)
slider_music = Slider(SETTINGS_X + 50, SETTINGS_Y + 120, 400, "Музыка")
slider_sfx = Slider(SETTINGS_X + 50, SETTINGS_Y + 240, 400, "Звуки")
show_settings = False

floor_bg = MovingFloor(WIDTH, HEIGHT)

tables = [
    RoundTable(WIDTH // 4, HEIGHT // 4, 80),
    RoundTable(WIDTH // 2, HEIGHT // 4, 80),
    RoundTable(WIDTH - (WIDTH // 4), HEIGHT // 4, 80),
    RoundTable(WIDTH // 4, HEIGHT - (HEIGHT // 4), 80),
    RoundTable(WIDTH // 2, HEIGHT - (HEIGHT // 4), 80),
    RoundTable(WIDTH - (WIDTH // 4), HEIGHT - (HEIGHT // 4), 80)
]

btn_menu_game = Button(WIDTH - 160, 20, 130, 50, "Меню", font_small)
show_pause_menu = False

PAUSE_W, PAUSE_H = 400, 500
PAUSE_X, PAUSE_Y = (WIDTH - PAUSE_W) // 2, (HEIGHT - PAUSE_H) // 2
btn_continue = Button(PAUSE_X + 50, PAUSE_Y + 100, 300, 70, "Продолжить", font_medium)
btn_pause_save = Button(PAUSE_X + 50, PAUSE_Y + 200, 300, 70, "Сохраниться", font_medium)
btn_pause_settings = Button(PAUSE_X + 50, PAUSE_Y + 300, 300, 70, "Настройки", font_medium)
btn_pause_exit = Button(PAUSE_X + 50, PAUSE_Y + 400, 300, 70, "Выйти", font_medium)
pause_buttons = [btn_pause_save, btn_pause_settings, btn_pause_exit, btn_continue]

# --- Магазин ---
Market_W, Market_H = 500, 500
MARKET_X, MARKET_Y = (WIDTH - Market_W) // 2, (HEIGHT - Market_H) // 2

MARKET_ITEMS = [
    {"id": "speed", "name": "Быстрые ботинки", "price": 30, "desc": "+1 к скорости"},
    {"id": "bag",   "name": "Большая сумка",   "price": 25, "desc": "+5 к вместимости"},
    {"id": "time",  "name": "Часы",            "price": 40, "desc": "+15 сек к смене"},
]

btn_market_next = Button(MARKET_X + 50, MARKET_Y + 420, 400, 60, "Дальше", font_medium)
market_item_buttons = []
for i, item in enumerate(MARKET_ITEMS):
    bx = MARKET_X + 30
    by = MARKET_Y + 100 + i * 100
    market_item_buttons.append(Button(bx, by, 440, 75, "", font_small))


def player_has(item_id):
    return item_id in market_data


def can_buy(item):
    return (not player_has(item["id"])) and player_money >= item["price"]


def buy_item(item):
    global player_money, Ps
    if not can_buy(item):
        return
    player_money -= item["price"]
    market_data.append(item["id"])
    if item["id"] == "speed":
        Ps += 1


# --- Диалог ---
dialogue_stage = 0
dialogue_texts = [
    "Директор: Здравствуйте! Вы кто такой?",
    "Вы: Здравствуйте! Я хочу устроиться к вам на работу.",
    "Директор: Хм... У нас сейчас есть только вакансия уборщика.",
    "Вы: Я согласен! Буду работать!",
    "Директор: Отлично! Твоя задача: собери мусор возле столов и выкинь его в бак."
]

# --- Мусор ---
trash_can_rect = pygame.Rect(WIDTH - 150, HEIGHT // 2 - 50, 80, 100)
garbage_items = []
garbage_collected = 0
garbage_in_inventory = 0
carried_colors = []

def spawn_garbage():
    angle = random.uniform(0, 2 * math.pi)
    t = random.choice(tables)
    distance = t.radius + 35
    gx = t.x + math.cos(angle) * distance
    gy = t.y + math.sin(angle) * distance
    return Garbage(gx, gy)


def start_shift():
    global state, Px, Py, garbage_items, garbage_collected, garbage_in_inventory, shift_time_left, player_xp, target_xp, max_garbage_on_map, garbage_spawn_delay, Ps
    state = "game_janitor"
    Px, Py = WIDTH // 2, HEIGHT // 2
    garbage_items.clear()

    max_garbage_on_map = 3 + current_shift
    target_xp = 50 + (current_shift * 30)

    for _ in range(max_garbage_on_map):
        garbage_items.append(spawn_garbage())
    garbage_collected = 0
    garbage_in_inventory = 0
    carried_colors.clear()
    shift_time_left = get_shift_duration(current_shift)
    if player_has("time"):
        shift_time_left += 15
    player_xp = 0
    garbage_spawn_delay = 0
    # пересчёт Ps по купленным улучшениям (страховка)
    Ps = 5 + (1 if player_has("speed") else 0)


# =========================================================
# --- ГЛАВНЫЙ ЦИКЛ ---
# =========================================================
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    dt = clock.tick(60) / 1000

    if state in ["menu", "slots"]:
        floor_bg.update(dt)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if state == "menu":
            if not show_settings:
                if btn_play.check_click(mouse_pos, event):
                    if current_slot is None:
                        state = "slots"
                    else:
                        saved_shift, saved_xp, saved_money, saved_market = load_game(current_slot)
                        if saved_shift is not None:
                            current_shift = saved_shift
                            player_money = saved_money
                            market_data = saved_market
                            if current_shift == 1:
                                state = "street"
                                Px, Py = WIDTH // 2, HEIGHT - 150
                            else:
                                start_shift()
                        else:
                            current_shift = 1
                            state = "street"
                            Px, Py = WIDTH // 2, HEIGHT - 150

                if btn_save.check_click(mouse_pos, event):
                    state = "slots"
                if btn_settings.check_click(mouse_pos, event): show_settings = True
                if btn_tema.check_click(mouse_pos, event): Bg_flag = not Bg_flag
            else:
                if btn_close.check_click(mouse_pos, event): show_settings = False
                slider_music.handle_event(event)
                slider_sfx.handle_event(event)

        elif state == "slots":
            if btn_back.check_click(mouse_pos, event):
                state = "menu"

            for i, btn in enumerate(slot_buttons):
                if btn.check_click(mouse_pos, event):
                    current_slot = i + 1
                    saved_shift, saved_xp, saved_money, saved_market = load_game(current_slot)
                    if saved_shift is not None:
                        current_shift = saved_shift
                        player_money = saved_money
                        market_data = saved_market
                        player_xp = 0
                    else:
                        current_shift = 1
                        player_money = 0
                        market_data = []
                        player_xp = 0
                    state = "menu"
                    print(f"Выбран слот {current_slot}, смена {current_shift}")

            for i, btn_del in enumerate(delete_buttons):
                slot_num = i + 1
                if os.path.exists(get_save_file(slot_num)):
                    if btn_del.check_click(mouse_pos, event):
                        delete_save(slot_num)
                        if current_slot == slot_num:
                            current_slot = None

        elif state == "street":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                state = "inside"
                Px, Py = 150, HEIGHT // 2

        elif state == "inside":
            if Px > WIDTH - 200 and Py > HEIGHT // 2 - 150 and Py < HEIGHT // 2 + 150:
                state = "dialogue"
                dialogue_stage = 0

        elif state == "dialogue":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                dialogue_stage += 1
                if dialogue_stage >= len(dialogue_texts):
                    start_shift()

        elif state == "game_janitor":
            if not show_pause_menu and not show_settings:
                if btn_menu_game.check_click(mouse_pos, event):
                    show_pause_menu = True

                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    if garbage_in_inventory > 0:
                        dist_to_can = math.hypot(Px - trash_can_rect.centerx, Py - trash_can_rect.centery)
                        if dist_to_can < Pr + 100:
                            garbage_in_inventory = 0
                            carried_colors.clear()
                            player_xp += 15
                            player_money += 5
                            if player_xp >= target_xp:
                                game_over_reason = "success"
                                save_game(current_slot, current_shift, player_xp, player_money, market_data)
                                state = "shift_end"
                    else:
                        bag_limit = 5 + (5 if player_has("bag") else 0)
                        if garbage_in_inventory < bag_limit:
                            for g in garbage_items:
                                if not g.collected:
                                    dist = math.hypot(Px - g.x, Py - g.y)
                                    if dist < Pr + g.radius + 40:
                                        g.collected = True
                                        garbage_in_inventory += 1
                                        garbage_collected += 1
                                        carried_colors.append(random.choice(g.pieces)[3])
                                        break

            elif show_pause_menu and not show_settings:
                if btn_continue.check_click(mouse_pos, event):
                    show_pause_menu = False
                if btn_pause_save.check_click(mouse_pos, event):
                    save_game(current_slot, current_shift, player_xp, player_money, market_data)
                    print(f"Сохранено в слот {current_slot}!")
                if btn_pause_settings.check_click(mouse_pos, event): show_settings = True
                if btn_pause_exit.check_click(mouse_pos, event):
                    state = "menu"
                    show_pause_menu = False

            elif show_settings:
                if btn_close.check_click(mouse_pos, event): show_settings = False
                slider_music.handle_event(event)
                slider_sfx.handle_event(event)

        elif state == "shift_end":
            if btn_continue.check_click(mouse_pos, event):
                if game_over_reason == "success":
                    current_shift += 1
                    if current_shift > 5:
                        game_over_reason = "game_win"
                        delete_save(current_slot)
                        state = "menu"
                    else:
                        save_game(current_slot, current_shift, player_xp, player_money, market_data)
                        state = "market"    # ← в магазин
                else:
                    current_shift = 1
                    delete_save(current_slot)
                    state = "menu"
                show_pause_menu = False

        elif state == "market":
            for i, btn in enumerate(market_item_buttons):
                if btn.check_click(mouse_pos, event):
                    buy_item(MARKET_ITEMS[i])
            if btn_market_next.check_click(mouse_pos, event):
                save_game(current_slot, current_shift, player_xp, player_money, market_data)
                start_shift()

    # --- ЛОГИКА ---
    if state == "game_janitor" and not show_pause_menu and not show_settings:
        shift_time_left -= dt
        if shift_time_left <= 0:
            shift_time_left = 0
            if player_xp >= target_xp:
                game_over_reason = "success"
                save_game(current_slot, current_shift, player_xp, player_money, market_data)
            else:
                game_over_reason = "fail"
            state = "shift_end"

        garbage_spawn_delay += dt
        if garbage_spawn_delay >= GARBAGE_SPAWN_INTERVAL:
            active_garbage = [g for g in garbage_items if not g.collected]
            if len(active_garbage) < max_garbage_on_map:
                garbage_items.append(spawn_garbage())
            garbage_spawn_delay = 0

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= Ps
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += Ps
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= Ps
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += Ps
        if dx and dy: dx *= 0.7071; dy *= 0.7071
        Px = max(Pr, min(Px + dx, WIDTH - Pr))
        Py = max(Pr, min(Py + dy, HEIGHT - Pr))
        for t in tables:
            Px, Py = t.collide_and_resolve(Px, Py, Pr)

    elif state == "inside" and not show_pause_menu and not show_settings:
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= Ps
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += Ps
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= Ps
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += Ps
        if dx and dy: dx *= 0.7071; dy *= 0.7071
        Px = max(Pr, min(Px + dx, WIDTH - Pr))
        Py = max(Pr, min(Py + dy, HEIGHT - Pr))
        for t in tables:
            Px, Py = t.collide_and_resolve(Px, Py, Pr)

    # --- ОТРИСОВКА ---
    if state == "menu":
        floor_bg.draw(screen, Bg_flag)
        for btn in menu_buttons:
            btn.check_hover(mouse_pos)
            btn.draw(screen)
        if current_slot is not None:
            slot_text = font_medium.render(f"Активный слот: {current_slot}", True, (255, 255, 255))
            screen.blit(slot_text, (20, 20))
        if show_settings:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(DARK_OVERLAY_MENU)
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, BG_COLOR_TEMA_MENU_1, (SETTINGS_X, SETTINGS_Y, SETTINGS_W, SETTINGS_H), border_radius=15)
            pygame.draw.rect(screen, BUTTON_COLOR_MENU, (SETTINGS_X, SETTINGS_Y, SETTINGS_W, SETTINGS_H), width=5, border_radius=15)
            screen.blit(font_large.render("Настройки", True, BUTTON_COLOR_MENU), (SETTINGS_X + 30, SETTINGS_Y + 20))
            btn_close.draw(screen)
            slider_music.draw(screen)
            slider_sfx.draw(screen)

    elif state == "slots":
        screen.fill(BG_COLOR_TEMA_MENU_1)
        title = font_large.render("ВЫБЕРИТЕ СЛОТ", True, BUTTON_COLOR_MENU)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        for i, btn in enumerate(slot_buttons):
            btn.check_hover(mouse_pos)
            saved_shift, saved_xp, saved_money, saved_market = load_game(i + 1)
            if saved_shift is not None:
                btn.text = f"Слот {i+1} (Смена {saved_shift})"
                btn.draw(screen)
                del_btn = delete_buttons[i]
                del_btn.check_hover(mouse_pos)
                del_btn.draw(screen)
            else:
                btn.text = f"Слот {i+1} (Пусто)"
                btn.draw(screen)
        btn_back.check_hover(mouse_pos)
        btn_back.draw(screen)

    elif state == "street":
        screen.fill(BG_COLOR_STREET)
        pygame.draw.rect(screen, (80, 50, 40), (WIDTH//2 - 300, HEIGHT//4, 600, HEIGHT - HEIGHT//4))
        pygame.draw.rect(screen, DOOR_COLOR, (WIDTH//2 - 80, HEIGHT - 300, 160, 300))
        pygame.draw.rect(screen, (255, 215, 0), (WIDTH//2 + 40, HEIGHT - 160, 15, 15))
        sign = font_large.render("РЕСТОРАН", True, (255, 255, 255))
        screen.blit(sign, (WIDTH // 2 - sign.get_width() // 2, HEIGHT // 4 + 50))
        pygame.draw.circle(screen, PLAYER_COLOR, (Px, Py), Pr)
        hint = font_medium.render("Нажмите ПРОБЕЛ, чтобы войти", True, (255, 255, 255))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 50))

    elif state == "inside":
        screen.fill(BG_COLOR_RESTAURANT)
        pygame.draw.rect(screen, WALL_COLOR, (0, 0, WIDTH, 30))
        pygame.draw.rect(screen, WALL_COLOR, (0, HEIGHT - 30, WIDTH, 30))
        pygame.draw.rect(screen, WALL_COLOR, (0, 0, 30, HEIGHT))
        pygame.draw.rect(screen, WALL_COLOR, (WIDTH - 30, 0, 30, HEIGHT))
        for t in tables: t.draw(screen)
        director_zone = pygame.Rect(WIDTH - 200, HEIGHT // 2 - 150, 170, 300)
        pygame.draw.rect(screen, (255, 165, 0), director_zone, 5)
        pygame.draw.rect(screen, (255, 165, 0, 100), director_zone)
        dir_text = font_medium.render("Директор", True, (0, 0, 0))
        screen.blit(dir_text, (director_zone.centerx - 60, director_zone.centery))
        pygame.draw.circle(screen, PLAYER_COLOR, (int(Px), int(Py)), Pr)
        task_bg = pygame.Surface((380, 50), pygame.SRCALPHA)
        task_bg.fill((0, 0, 0, 120))
        screen.blit(task_bg, (WIDTH - 400, 90))
        task_text = font_medium.render("Дойти до директора", True, (255, 255, 255))
        screen.blit(task_text, (WIDTH - 380, 100))
        btn_menu_game.check_hover(mouse_pos)
        btn_menu_game.draw(screen)

    elif state == "dialogue":
        screen.fill(BG_COLOR_RESTAURANT)
        for t in tables: t.draw(screen)
        pygame.draw.rect(screen, (20, 20, 20), (100, HEIGHT - 250, WIDTH - 200, 200), border_radius=15)
        pygame.draw.rect(screen, BUTTON_COLOR_MENU, (100, HEIGHT - 250, WIDTH - 200, 200), 4, border_radius=15)
        current_text = dialogue_texts[dialogue_stage]
        draw_text_wrapped(screen, current_text, font_medium, (255, 255, 255), 130, HEIGHT - 210, WIDTH - 260)
        hint = font_small.render("Нажмите ПРОБЕЛ, чтобы продолжить...", True, (150, 150, 150))
        screen.blit(hint, (WIDTH - 450, HEIGHT - 100))

    elif state == "game_janitor":
        screen.fill(BG_COLOR_RESTAURANT)
        pygame.draw.rect(screen, WALL_COLOR, (0, 0, WIDTH, 30))
        pygame.draw.rect(screen, WALL_COLOR, (0, HEIGHT - 30, WIDTH, 30))
        pygame.draw.rect(screen, WALL_COLOR, (0, 0, 30, HEIGHT))
        pygame.draw.rect(screen, WALL_COLOR, (WIDTH - 30, 0, 30, HEIGHT))
        for t in tables: t.draw(screen)
        pygame.draw.rect(screen, TRASH_COLOR, trash_can_rect)
        pygame.draw.rect(screen, (50, 50, 50), trash_can_rect, 4)
        pygame.draw.rect(screen, (80, 80, 80), (trash_can_rect.x - 5, trash_can_rect.y - 15, trash_can_rect.width + 10, 15))
        trash_text = font_medium.render("Бак", True, (255, 255, 255))
        screen.blit(trash_text, (trash_can_rect.centerx - 25, trash_can_rect.y + 35))
        for g in garbage_items: g.draw(screen)
        pygame.draw.circle(screen, PLAYER_COLOR, (int(Px), int(Py)), Pr)
        draw_carried_garbage(screen, Px, Py, garbage_in_inventory, carried_colors)

        if not show_pause_menu and not show_settings:
            btn_menu_game.check_hover(mouse_pos)
            btn_menu_game.draw(screen)

        task_bg = pygame.Surface((500, 220), pygame.SRCALPHA)
        task_bg.fill((0, 0, 0, 150))
        screen.blit(task_bg, (WIDTH - 520, 90))
        mins = int(shift_time_left) // 60
        secs = int(shift_time_left) % 60
        time_str = f"Смена {current_shift}/5 | Время: {mins:02d}:{secs:02d}"
        time_text = font_small.render(time_str, True, (255, 255, 255))
        screen.blit(time_text, (WIDTH - 500, 100))
        xp_color = (0, 255, 0) if player_xp >= target_xp else (255, 215, 0)
        xp_str = f"Опыт: {player_xp} / {target_xp}"
        xp_text = font_small.render(xp_str, True, xp_color)
        screen.blit(xp_text, (WIDTH - 500, 135))
        money_str = f"Деньги: {player_money}"
        money_text = font_small.render(money_str, True, (255, 215, 0))
        screen.blit(money_text, (WIDTH - 500, 170))

        if show_pause_menu and not show_settings:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(DARK_OVERLAY_MENU)
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, BG_COLOR_TEMA_MENU_1, (PAUSE_X, PAUSE_Y, PAUSE_W, PAUSE_H), border_radius=15)
            pygame.draw.rect(screen, BUTTON_COLOR_MENU, (PAUSE_X, PAUSE_Y, PAUSE_W, PAUSE_H), width=5, border_radius=15)
            pause_title = font_large.render("Пауза", True, BUTTON_COLOR_MENU)
            screen.blit(pause_title, (WIDTH//2 - pause_title.get_width()//2, PAUSE_Y + 20))
            for btn in pause_buttons:
                btn.check_hover(mouse_pos)
                btn.draw(screen)

        if show_settings:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(DARK_OVERLAY_MENU)
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, BG_COLOR_TEMA_MENU_1, (SETTINGS_X, SETTINGS_Y, SETTINGS_W, SETTINGS_H), border_radius=15)
            pygame.draw.rect(screen, BUTTON_COLOR_MENU, (SETTINGS_X, SETTINGS_Y, SETTINGS_W, SETTINGS_H), width=5, border_radius=15)
            screen.blit(font_large.render("Настройки", True, BUTTON_COLOR_MENU), (SETTINGS_X + 30, SETTINGS_Y + 20))
            btn_close.draw(screen)
            slider_music.draw(screen)
            slider_sfx.draw(screen)

    elif state == "market":
        screen.fill((30, 40, 50))
        pygame.draw.rect(screen, BG_COLOR_TEMA_MENU_1, (MARKET_X, MARKET_Y, Market_W, Market_H), border_radius=15)
        pygame.draw.rect(screen, BUTTON_COLOR_MENU, (MARKET_X, MARKET_Y, Market_W, Market_H), width=5, border_radius=15)
        market_title = font_large.render("Магазин", True, BUTTON_COLOR_MENU)
        screen.blit(market_title, (WIDTH//2 - market_title.get_width()//2, MARKET_Y + 15))
        money_str = font_medium.render(f"Деньги: {player_money}", True, (255, 215, 0))
        screen.blit(money_str, (MARKET_X + 30, MARKET_Y + 60))

        for i, item in enumerate(MARKET_ITEMS):
            btn = market_item_buttons[i]
            btn.check_hover(mouse_pos)
            if player_has(item["id"]):
                btn.color = (80, 200, 80)
                btn.text = f"{item['name']} — Куплено"
            elif player_money >= item["price"]:
                btn.color = BUTTON_COLOR_MENU
                btn.text = f"{item['name']} — {item['price']}"
            else:
                btn.color = (120, 120, 120)
                btn.text = f"{item['name']} — {item['price']} (нет денег)"
            btn.draw(screen)
            desc = font_small.render(item["desc"], True, (200, 200, 200))
            screen.blit(desc, (MARKET_X + 30, MARKET_Y + 145 + i * 100))

        btn_market_next.check_hover(mouse_pos)
        btn_market_next.draw(screen)

    elif state == "shift_end":
        screen.fill((20, 30, 40))
        if game_over_reason == "success":
            if current_shift >= 5:
                title = font_large.render("ВЫ СТАЛИ ДИРЕКТОРОМ!", True, (0, 255, 0))
                desc = font_medium.render("Поздравляем! Вы прошли все 5 смен уборщика.", True, (255, 255, 255))
            else:
                title = font_large.render("СМЕНА ЗАВЕРШЕНА!", True, (0, 255, 0))
                desc = font_medium.render(f"Вы набрали {player_xp} XP. Переход к смене {current_shift + 1}!", True, (255, 255, 255))
        else:
            title = font_large.render("ВАС УВОЛИЛИ!", True, (255, 0, 0))
            desc = font_medium.render("Вы не набрали нужный опыт. Прогресс сброшен.", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(desc, (WIDTH // 2 - desc.get_width() // 2, HEIGHT // 2 - 20))
        btn_continue.check_hover(mouse_pos)
        btn_continue.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()