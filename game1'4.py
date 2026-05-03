import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Сверхпроводник — полноценная песочница")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (80, 140, 255)
CYAN = (80, 220, 255)

# ---------------- мир ----------------
objects = []

# стартовый магнит
objects.append({
    "type": "magnet",
    "x": WIDTH // 2,
    "y": HEIGHT // 2,
    "vx": 0,
    "vy": 0
})

gravity = 0.4
k = 50000
temperature = 50
Tc = 100

zoom = 1.0

editor_mode = False
selected_type = "magnet"

drag_index = None


# ---------------- камера ----------------
def world_to_screen(x, y):
    cx, cy = WIDTH // 2, HEIGHT // 2
    return int((x - cx) * zoom + cx), int((y - cy) * zoom + cy)


def screen_to_world(x, y):
    cx, cy = WIDTH // 2, HEIGHT // 2
    return (x - cx) / zoom + cx, (y - cy) / zoom + cy


def dist(a, b, x, y):
    return math.hypot(a - x, b - y)


def reset():
    global objects
    objects = [{
        "type": "magnet",
        "x": WIDTH // 2,
        "y": HEIGHT // 2,
        "vx": 0,
        "vy": 0
    }]


# ---------------- цикл ----------------
while True:
    screen.fill(BLACK)

    mx, my = pygame.mouse.get_pos()
    wx, wy = screen_to_world(mx, my)

    # ---------- события ----------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_q:
                editor_mode = not editor_mode

            if event.key == pygame.K_1:
                selected_type = "magnet"

            if event.key == pygame.K_2:
                selected_type = "superconductor"

            if event.key == pygame.K_e and editor_mode:
                if objects:
                    nearest = min(objects, key=lambda o: dist(o["x"], o["y"], wx, wy))
                    if dist(nearest["x"], nearest["y"], wx, wy) < 50:
                        objects.remove(nearest)

            if event.key == pygame.K_r:
                reset()

            if event.key == pygame.K_UP:
                temperature += 5
            if event.key == pygame.K_DOWN:
                temperature -= 5
            if event.key == pygame.K_RIGHT:
                k += 5000
            if event.key == pygame.K_LEFT:
                k -= 5000

        if event.type == pygame.MOUSEWHEEL:
            zoom *= 1.1 if event.y > 0 else 0.9
            zoom = max(0.3, min(zoom, 3))

        if event.type == pygame.MOUSEBUTTONDOWN:

            if editor_mode:
                # СОЗДАНИЕ ТОЛЬКО ОДИН РАЗ ЗА КЛИК
                if selected_type == "magnet":
                    objects.append({
                        "type": "magnet",
                        "x": wx,
                        "y": wy,
                        "vx": 0,
                        "vy": 0
                    })

                elif selected_type == "superconductor":
                    objects.append({
                        "type": "superconductor",
                        "x": wx,
                        "y": wy,
                        "vx": 0,
                        "vy": 0
                    })

            else:
                # drag
                for i, o in enumerate(objects):
                    size = 20 if o["type"] == "magnet" else 60
                    if dist(o["x"], o["y"], wx, wy) < size:
                        drag_index = i
                        break

        if event.type == pygame.MOUSEBUTTONUP:
            drag_index = None

    # ---------- физика ----------
    for i, o in enumerate(objects):

        if drag_index == i:
            o["x"], o["y"] = wx, wy
            o["vx"], o["vy"] = 0, 0
            continue

        if o["type"] == "magnet":

            o["vy"] += gravity
            for s in objects:
                if s["type"] != "superconductor":
                    continue

                dx = o["x"] - s["x"]
                dy = o["y"] - s["y"]
                d = math.hypot(dx, dy)

                if d > 5 and temperature < Tc:
                    strength = k / (d ** 2)

                    o["vx"] += (dx / d) * strength
                    o["vy"] += (dy / d) * strength

            o["x"] += o["vx"]
            o["y"] += o["vy"]

    # ---------- отрисовка ----------

    for o in objects:
        x, y = world_to_screen(o["x"], o["y"])

        if o["type"] == "magnet":
            pygame.draw.circle(screen, BLUE, (x, y), int(15 * zoom))

        elif o["type"] == "superconductor":
            pygame.draw.circle(screen, CYAN, (x, y), int(60 * zoom))

    # ---------- UI ----------
    ui = [
        "Q — редактор | 1 магнит | 2 сверхпроводник",
        "ЛКМ — двигать | E — удалить",
        "Колесо — зум",
        f"Режим: {'РЕДАКТОР' if editor_mode else 'ИГРА'}",
        f"Выбор: {selected_type}",
        f"Температура: {temperature}",
        f"k: {k}",
        f"Zoom: {zoom:.2f}"
    ]

    for i, line in enumerate(ui):
        screen.blit(font.render(line, True, WHITE), (10, 10 + i * 20))

    pygame.display.flip()
    clock.tick(60)