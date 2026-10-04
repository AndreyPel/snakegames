import pygame
import sys
import random
import json  # <-- ВАЖНО: Добавлен импорт для работы с JSON
from pathlib import Path

# --- НАДЕЖНОЕ ОПРЕДЕЛЕНИЕ ПУТЕЙ (Работает и в .py, и в .exe) ---
if getattr(sys, 'frozen', False):
    # Если приложение запущено как .exe
    base_path = Path(sys.executable).parent
else:
    # Если запущено как обычный .py скрипт
    base_path = Path(__file__).parent

# Пути к ресурсам
ASSETS_DIR = base_path / "assets"
SAVE_FILE = base_path / "highscore.json"  # Файл рекорда будет лежать РЯДОМ с .exe

# --- Инициализация ---
pygame.init()

# --- 1. Константы и настройки ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 25
FPS = 12

# Цвета
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (220, 20, 60)
BLUE = (70, 130, 180)
GREY = (40, 40, 40)

# --- 2. Настройка экрана и шрифтов ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Pro')
clock = pygame.time.Clock()

# Шрифты
try:
    FONT_LARGE = pygame.font.Font(str(ASSETS_DIR / "PressStart2P-Regular.ttf"), 36)
    FONT_MEDIUM = pygame.font.Font(str(ASSETS_DIR / "PressStart2P-Regular.ttf"), 24)
    FONT_SMALL = pygame.font.Font(str(ASSETS_DIR / "PressStart2P-Regular.ttf"), 18)
except FileNotFoundError:
    FONT_LARGE = pygame.font.SysFont('consolas', 36)
    FONT_MEDIUM = pygame.font.SysFont('consolas', 24)
    FONT_SMALL = pygame.font.SysFont('consolas', 18)


# --- 3. Вспомогательные функции ---
def draw_grid():
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, GREY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, GREY, (0, y), (SCREEN_WIDTH, y))

def draw_text(text, font, color, surface, x, y, center=False):
    obj = font.render(text, True, color)
    rect = obj.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(obj, rect)

def get_random_food_position(snake_body):
    while True:
        x = random.randrange(0, SCREEN_WIDTH // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randrange(0, SCREEN_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE
        if [x, y] not in snake_body:
            return [x, y]

import tempfile

def get_temp_save_path():
    """Возвращает путь к файлу во временной папке Windows."""
    temp_dir = Path(tempfile.gettempdir())
    return temp_dir / "snakepro_highscore.json"

SAVE_FILE = get_temp_save_path() # Глобальная переменная для пути

def load_high_score():
    """Загружает рекорд из Temp."""
    try:
        if SAVE_FILE.exists():
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("high_score", 0)
    except Exception:
        pass
    return 0

def save_high_score(score):
    """Сохраняет рекорд в Temp."""
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"high_score": score}, f, indent=4)
        print(f"[SUCCESS] Рекорд {score} Сохранился в TEMP: {SAVE_FILE}")
    except Exception as e:
        print(f"[FATAL ERROR] Не удалось записать даже в Temp: {e}")

# --- 5. Игровые состояния ---
def game_intro():
    """Экран главного меню."""
    intro = True
    # Загружаем рекорд один раз при входе в меню
    high_score = load_high_score() 
    
    while intro:
        screen.fill(BLACK)
        draw_text('SNAKE PRO', FONT_LARGE, GREEN, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, center=True)
        draw_text('Press ENTER to Start', FONT_MEDIUM, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
        draw_text('Use WASD or Arrows', FONT_SMALL, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)
        draw_text(f'High Score: {high_score}', FONT_SMALL, GREY, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    intro = False
                    game_loop()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()
        clock.tick(15)

def game_over_screen(current_score, high_score):
    """Экран окончания игры."""
    over = True
    while over:
        screen.fill(BLACK)
        draw_text('GAME OVER', FONT_LARGE, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, center=True)
        draw_text(f'Your Score: {current_score}', FONT_MEDIUM, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
        draw_text(f'High Score: {high_score}', FONT_MEDIUM, GREY, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)
        draw_text('Press ENTER to Play Again', FONT_MEDIUM, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120, center=True)
        draw_text('Press ESC to Quit', FONT_MEDIUM, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    over = False
                    game_loop()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()
        clock.tick(15)

def game_loop():
    game_over = False
    game_close = False

    x1, y1 = (SCREEN_WIDTH // 2 // BLOCK_SIZE) * BLOCK_SIZE, (SCREEN_HEIGHT // 2 // BLOCK_SIZE) * BLOCK_SIZE
    x1_change, y1_change = 0, 0
    
    snake_List = []
    Length_of_snake = 1
    
    score = 0
    high_score = load_high_score() # Загружаем в начале игры
    
    first_frame = True 
    foodx, foody = 0, 0

    while not game_over:
        while game_close:
            game_over_screen(score, high_score)

        # --- ОБРАБОТКА ВВОДА (Стрелки + WASD) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Стрелки
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change, y1_change = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change, y1_change = BLOCK_SIZE, 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    x1_change, y1_change = 0, -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    x1_change, y1_change = 0, BLOCK_SIZE
                # WASD
                elif event.key == pygame.K_a and x1_change == 0:
                    x1_change, y1_change = -BLOCK_SIZE, 0
                elif event.key == pygame.K_d and x1_change == 0:
                    x1_change, y1_change = BLOCK_SIZE, 0
                elif event.key == pygame.K_w and y1_change == 0:
                    x1_change, y1_change = 0, -BLOCK_SIZE
                elif event.key == pygame.K_s and y1_change == 0:
                    x1_change, y1_change = 0, BLOCK_SIZE
                elif event.key == pygame.K_ESCAPE:
                    game_over = True

        # Движение
        x1 += x1_change
        y1 += y1_change

        # Стены
        if x1 >= SCREEN_WIDTH or x1 < 0 or y1 >= SCREEN_HEIGHT or y1 < 0:
            game_close = True

        # Логика змейки
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)

        if first_frame:
            foodx, foody = get_random_food_position(snake_List)
            first_frame = False

        if x1 == foodx and y1 == foody:
            score += 10
            Length_of_snake += 1
            foodx, foody = get_random_food_position(snake_List)

        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for block in snake_List[:-1]:
            if block == snake_Head:
                game_close = True
                break

        # Отрисовка
        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, [foodx, foody, BLOCK_SIZE, BLOCK_SIZE])
        for segment in snake_List:
            pygame.draw.rect(screen, GREEN, [segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE])
        
        draw_text(f'Score: {score}', FONT_SMALL, WHITE, screen, 10, 10)
        
        pygame.display.update()
        clock.tick(10)

    # Сохранение (только если побит рекорд)
    if score > high_score:
        save_high_score(score)
    
    pygame.quit()
    sys.exit()


# --- ЗАПУСК ---
if __name__ == "__main__":
    game_intro()