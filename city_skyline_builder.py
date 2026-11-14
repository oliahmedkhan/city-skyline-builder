import math
import os
import random
import sys
if sys.platform == "win32":
    _project_directory = os.path.dirname(os.path.abspath(__file__))
    _dll_directory = os.add_dll_directory(_project_directory)
    os.environ["PATH"] = _project_directory + os.pathsep + os.environ.get("PATH", "")
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
W, H = 600, 800
FPS = 16
BLOCK_W, BLOCK_H = 92.0, 76.0
BASE_X, BASE_Y = 300.0, 150.0
tower = []
clouds = []
birds = []
score = 0
best_height = 0
moving_x, moving_y = BASE_X, 690.0
moving_speed = 2.5
swing_angle, swing_direction = 0.0, 1
dropping = False
fall_x, fall_y, fall_vy, fall_angle = BASE_X, 690.0, 0.0, 0.0
camera_offset = 0.0
camera_target = 0.0
tower_tilt = 0.0
animation_time = 0.0
collapse_started = False
collapsing = False
collapse_elapsed = 0.0
collapse_angle = 0.0
collapse_drop = 0.0
game_over = False
status = "PRESS SPACE OR CLICK TO BUILD"


def color(value):
    glColor3f(*value)


def rect(x, y, width, height, value):
    color(value)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()


def line(x1, y1, x2, y2, value, width=1):
    color(value)
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()
    glLineWidth(1)


def circle(cx, cy, radius, value, segments=24):
    color(value)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for index in range(segments + 1):
        angle = 2 * math.pi * index / segments
        glVertex2f(cx + math.cos(angle) * radius,
                   cy + math.sin(angle) * radius)
    glEnd()


def triangle(x1, y1, x2, y2, x3, y3, value):
    color(value)
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()


def text(x, y, value, shade=(1, 1, 1), font=GLUT_BITMAP_8_BY_13):
    color(shade)
    glRasterPos2f(x, y)
    for character in str(value):
        glutBitmapCharacter(font, ord(character))


def centered(y, value, shade=(1, 1, 1), font=GLUT_BITMAP_8_BY_13):
    width = sum(glutBitmapWidth(font, ord(character)) for character in str(value))
    text((W - width) / 2, y, value, shade, font)


def draw_gradient_sky():
    glBegin(GL_QUADS)
    glColor3f(.78, .91, .96)
    glVertex2f(0, 0)
    glVertex2f(W, 0)
    glColor3f(.38, .72, .91)
    glVertex2f(W, H)
    glVertex2f(0, H)
    glEnd()


def draw_windows(x, y, columns, rows, width, height, gap):
    for row in range(rows):
        for column in range(columns):
            xx = x + column * (width + gap)
            yy = y + row * (height + gap)
            rect(xx, yy, width, height, (.06, .20, .28))
            rect(xx + 2, yy + 2, width - 4, height - 4, (.24, .65, .77))
            rect(xx + 5, yy + 3, 3, height - 6, (.56, .82, .87))


def draw_city_building(x, y, width, height, shade, style=0):
    rect(x, y, width, height, shade)
    rect(x + 4, y, 5, height, (.78, .81, .78))
    rect(x + width - 7, y, 7, height, (.25, .31, .34))
    if style == 0:
        draw_windows(x + 13, y + 14, 3, max(2, int(height / 48)), 13, 23, 7)
    elif style == 1:
        for floor_y in range(int(y + 18), int(y + height - 20), 38):
            rect(x + 8, floor_y, width - 16, 5, (.72, .75, .72))
            rect(x + 12, floor_y + 8, width - 24, 20, (.10, .53, .74))
    else:
        draw_windows(x + 12, y + 12, 2, max(2, int(height / 44)), 17, 22, 9)


def draw_skyline():
    buildings = [
        (-18, 132, 88, 410, (.58, .68, .70), 0),
        (70, 132, 78, 535, (.68, .73, .72), 1),
        (148, 132, 104, 355, (.53, .60, .62), 2),
        (430, 132, 90, 445, (.62, .67, .67), 1),
        (518, 132, 100, 565, (.47, .54, .57), 0),
    ]
    for building in buildings:
        draw_city_building(*building)
    for y in range(160, 760, 62):
        rect(86, y, 18, 4, (.54, .61, .61))
        rect(522, y, 74, 5, (.34, .39, .42))


def draw_cloud(x, y, scale=1.0):
    cloud_color = (.91, .96, .97)
    rect(x, y, 74 * scale, 16 * scale, cloud_color)
    circle(x + 19 * scale, y + 14 * scale, 15 * scale, cloud_color)
    circle(x + 42 * scale, y + 18 * scale, 20 * scale, cloud_color)
    circle(x + 63 * scale, y + 13 * scale, 14 * scale, cloud_color)


def draw_cloud_group(cloud):
    draw_cloud(cloud["x"], cloud["y"], cloud["scale"])


def initialize_clouds():
    global clouds
    clouds = []
    for index in range(8):
        clouds.append({
            "x": random.uniform(-80, W + 80),
            "y": random.uniform(190, H + 280),
            "scale": random.uniform(.55, 1.15),
            "speed": random.uniform(.25, .75),
        })


def update_clouds():
    for cloud in clouds:
        cloud["x"] += cloud["speed"]
        if cloud["x"] > W + 110:
            cloud["x"] = -110
        if cloud["y"] < camera_offset - 100:
            cloud["y"] = camera_offset + H + random.uniform(40, 260)


def draw_bird(x, y, scale=1.0, phase=0.0):
    wing_lift = math.sin(phase) * 5 * scale
    bird_color = (.19, .32, .39)
    line(x - 9 * scale, y - wing_lift, x, y + 3 * scale, bird_color, 2)
    line(x, y + 3 * scale, x + 9 * scale, y - wing_lift, bird_color, 2)


def draw_bird_group(bird):
    for index in range(bird["count"]):
        offset_x = index * 17 * bird["scale"]
        offset_y = math.sin(bird["phase"] + index) * 5
        draw_bird(bird["x"] + offset_x, bird["y"] + offset_y,
                  bird["scale"], bird["phase"] + index * .7)


def initialize_birds():
    global birds
    birds = []
    for index in range(5):
        birds.append({
            "x": random.uniform(-100, W),
            "y": random.uniform(280, H + 220),
            "speed": random.uniform(1.0, 2.2),
            "scale": random.uniform(.65, 1.15),
            "phase": random.uniform(0, 2 * math.pi),
            "count": random.randint(1, 3),
        })


def update_birds():
    for bird in birds:
        bird["x"] += bird["speed"]
        bird["phase"] += .16
        if bird["x"] > W + 70:
            bird["x"] = -70
        if bird["y"] < camera_offset - 80:
            bird["y"] = camera_offset + H + random.uniform(50, 240)


def draw_tree(x, y, scale=1.0):
    rect(x - 4 * scale, y, 8 * scale, 42 * scale, (.35, .22, .10))
    circle(x, y + 54 * scale, 19 * scale, (.07, .37, .17))
    circle(x - 14 * scale, y + 46 * scale, 14 * scale, (.08, .43, .19))
    circle(x + 14 * scale, y + 45 * scale, 15 * scale, (.06, .34, .15))
    circle(x, y + 67 * scale, 13 * scale, (.10, .47, .22))


def draw_ground():
    rect(0, 0, W, 120, (.15, .14, .13))
    rect(0, 120, W, 14, (.57, .41, .18))
    rect(0, 134, W, 16, (.79, .62, .25))
    rect(0, 134, 174, 4, (.35, .40, .39))
    for x in range(0, 174, 15):
        rect(x, 138, 3, 26, (.50, .55, .52))
    line(0, 150, 174, 150, (.45, .51, .48))
    line(0, 160, 174, 160, (.45, .51, .48))
    rect(430, 136, 170, 31, (.79, .61, .16))
    for x in range(438, 600, 22):
        rect(x, 139, 2, 25, (.55, .39, .10))
    rect(448, 145, 38, 15, (.93, .79, .35))
    text(453, 150, "SITE", (.30, .24, .12))
    for x in range(205, 420, 42):
        rect(x, 108, 24, 10, (.30, .31, .29))
        rect(x + 3, 111, 18, 2, (.68, .62, .45))


def draw_building_window(x, y, width, height):
    rect(x, y, width, height, (.08, .16, .21))
    rect(x + 4, y + 4, width - 8, height - 8, (.08, .54, .76))
    rect(x + 7, y + 7, 5, height - 14, (.40, .79, .88))
    rect(x + width / 2 - 1, y + 3, 3, height - 6, (.12, .23, .30))
    rect(x + 3, y + height / 2, width - 6, 3, (.12, .23, .30))


def draw_building_module(cx, cy, width=BLOCK_W, height=BLOCK_H, tilt=0.0):
    glPushMatrix()
    glTranslatef(cx, cy, 0)
    glRotatef(tilt, 0, 0, 1)
    x, y = -width / 2, -height / 2
    rect(x - 3, y - 3, width + 6, height + 6, (.12, .14, .16))
    rect(x, y, width, height, (.91, .55, .08))
    rect(x + 4, y + 4, width - 8, height - 8, (.18, .22, .24))
    rect(x + 8, y + 8, width - 16, height - 16, (.82, .78, .58))
    pane_w = (width - 26) / 2
    pane_h = (height - 25) / 2
    draw_building_window(x + 9, y + 9, pane_w, pane_h)
    draw_building_window(x + 17 + pane_w, y + 9, pane_w, pane_h)
    draw_building_window(x + 9, y + 16 + pane_h, pane_w, pane_h)
    draw_building_window(x + 17 + pane_w, y + 16 + pane_h, pane_w, pane_h)
    rect(x + 2, y + 2, 4, height - 4, (1, .70, .12))
    rect(x + width - 6, y + 2, 4, height - 4, (1, .70, .12))
    rect(x + 3, y + height / 2 - 2, width - 6, 4, (.12, .14, .16))
    rect(x + 3, y + 2, width - 6, 3, (1, .82, .31))
    glPopMatrix()


def draw_tower():
    for module in tower:
        draw_building_module(module["x"], module["y"],
                             module["width"], module["height"], 0.0)


def draw_tower_with_tilt(extra_angle=0.0, drop=0.0):
    if not tower:
        return
    pivot_x = tower[0]["x"]
    pivot_y = tower[0]["y"] - tower[0]["height"] / 2
    glPushMatrix()
    glTranslatef(pivot_x, pivot_y - drop, 0)
    glRotatef(tower_tilt + extra_angle, 0, 0, 1)
    glTranslatef(-pivot_x, -pivot_y, 0)
    draw_tower()
    glPopMatrix()


def draw_collapsing_tower():
    draw_tower_with_tilt(collapse_angle, collapse_drop)


def draw_crane_screen_space():
    beam_y = H - 42
    rect(35, beam_y - 5, 530, 10, (.98, .63, .04))
    rect(35, beam_y + 5, 530, 4, (.30, .33, .34))
    rect(43, beam_y - 150, 14, 150, (.93, .58, .04))
    line(57, beam_y - 148, 120, beam_y - 5, (.35, .37, .35), 4)
    line(120, beam_y - 5, 180, beam_y - 148, (.35, .37, .35), 4)
    if collapse_started:
        return
    rect(moving_x - 14, beam_y - 29, 28, 12, (.20, .23, .25))
    rect(moving_x - 9, beam_y - 27, 18, 5, (1, .70, .08))
    if dropping:
        block_screen_y = fall_y - camera_offset
        block_angle = fall_angle
    else:
        block_screen_y = moving_y - camera_offset
        block_angle = swing_angle * .22
    hook_y = block_screen_y + BLOCK_H / 2 + 8
    line(moving_x, beam_y - 29, moving_x, hook_y + 8, (.04, .05, .06), 2)
    line(moving_x + 2, beam_y - 29, moving_x + 2, hook_y + 8, (.45, .47, .46), 1)
    circle(moving_x, hook_y + 5, 4, (1, .70, .08), 12)
    line(moving_x, hook_y + 1, moving_x, hook_y - 7, (.04, .05, .06), 2)
    draw_building_module(moving_x, block_screen_y, BLOCK_W, BLOCK_H, block_angle)


def tower_top_y():
    if not tower:
        return BASE_Y + BLOCK_H
    top = tower[-1]
    return top["y"] + top["height"] / 2


def calculate_camera_offset():
    return max(0.0, tower_top_y() - 510.0)


def update_camera():
    global camera_offset, camera_target
    camera_target = calculate_camera_offset()
    camera_offset += (camera_target - camera_offset) * .10
    if abs(camera_target - camera_offset) < .15:
        camera_offset = camera_target


def calculate_center_of_mass(modules=None):
    if modules is None:
        modules = tower
    total_mass = sum(module["width"] * module["height"] for module in modules)
    if total_mass == 0:
        return BASE_X
    weighted_x = sum(module["x"] * module["width"] * module["height"]
                     for module in modules)
    return weighted_x / total_mass


def calculate_support_area():
    if not tower:
        return BASE_X - BLOCK_W / 2, BASE_X + BLOCK_W / 2
    base = tower[0]
    return base["x"] - base["width"] / 2, base["x"] + base["width"] / 2


def _support_margins():
    if not tower:
        return [1.0]
    margins = []
    base_left, base_right = calculate_support_area()
    base_center = (base_left + base_right) / 2
    base_half_width = max((base_right - base_left) / 2, 1.0)
    base_com = calculate_center_of_mass()
    margins.append((base_half_width - abs(base_com - base_center)) / base_half_width)

    for index in range(len(tower) - 1):
        support = tower[index]
        load_center = calculate_center_of_mass(tower[index + 1:])
        half_width = max(support["width"] / 2, 1.0)
        margins.append((half_width - abs(load_center - support["x"])) / half_width)
    return margins


def calculate_balance_value():
    if not tower:
        return 100
    worst_margin = min(_support_margins())
    return int(round(max(0.0, min(1.0, worst_margin)) * 100))


def calculate_tower_balance():
    return calculate_balance_value()


def calculate_sway_intensity():
    instability = (100 - calculate_tower_balance()) / 100.0
    return .12 + 10.0 * instability ** 1.6


def update_tower_tilt():
    global animation_time, tower_tilt
    if collapse_started:
        return
    animation_time += FPS / 1000.0
    amplitude = calculate_sway_intensity()
    target_tilt = amplitude * math.sin(animation_time * 2.4)
    tower_tilt += (target_tilt - tower_tilt) * .18


def check_tower_stability():
    # Arcade approximation: each module must support the combined centre of mass above it.
    return (calculate_tower_balance() > 0
            and all(margin > 0 for margin in _support_margins()))


def balance_status():
    if not check_tower_stability():
        return "UNSTABLE"
    value = calculate_balance_value()
    if value >= 80:
        return "EXCELLENT"
    if value >= 60:
        return "GOOD"
    if value >= 40:
        return "WARNING"
    if value >= 20:
        return "CRITICAL"
    return "EXTREMELY UNSTABLE"


def draw_balance_indicator(x, y, width=190, height=13):
    value = calculate_balance_value()
    if value >= 60:
        shade = (.17, .72, .35)
    elif value >= 40:
        shade = (.95, .76, .12)
    elif value >= 20:
        shade = (.98, .43, .08)
    else:
        shade = (.88, .12, .12)
    rect(x, y, width, height, (.12, .16, .18))
    if value:
        rect(x, y, width * value / 100, height, shade)
    rect(x, y, width, 2, (.85, .89, .87))


def draw_hud():
    rect(14, 49, W - 28, 76, (.06, .10, .13))
    rect(18, 53, W - 36, 68, (.15, .21, .23))
    floor_count = max(0, len(tower) - 1)
    text(28, 103, "FLOORS: %d   SCORE: %d   BEST: %d" %
         (floor_count, score, best_height), (1, .88, .51))
    value = calculate_balance_value()
    text(28, 81, "BALANCE: %d%%   STATUS: %s" %
         (value, balance_status()), (1, 1, 1))
    draw_balance_indicator(385, 78, 184, 14)

    if collapsing:
        centered(59, "WARNING! TOWER IS UNSTABLE", (1, .35, .18))
    elif not game_over and status:
        centered(59, status, (.98, .82, .25))
    rect(16, 12, W - 32, 31, (.06, .10, .13))
    centered(27, "SPACE / CLICK: DROP     A/D OR ARROWS: MOVE     R: RESTART",
             (.89, .91, .87))


def draw_game_over():
    if not game_over:
        return
    rect(75, 314, 450, 176, (.03, .05, .08))
    rect(80, 319, 440, 166, (.18, .23, .26))
    centered(444, "GAME OVER", (1, .72, .12), GLUT_BITMAP_HELVETICA_18)
    centered(405, "FINAL HEIGHT: " + str(score))
    centered(375, "BEST HEIGHT: " + str(best_height))
    centered(344, "PRESS R TO RESTART")


def draw_background():
    draw_gradient_sky()


def draw_world_with_camera():
    glPushMatrix()
    glTranslatef(0, -camera_offset, 0)
    draw_skyline()
    for cloud in clouds:
        draw_cloud_group(cloud)
    for bird in birds:
        draw_bird_group(bird)
    draw_ground()
    draw_tree(176, 150, .75)
    draw_tree(418, 150, .72)
    if collapse_started:
        draw_collapsing_tower()
    else:
        draw_tower_with_tilt()
    glPopMatrix()


def draw_hud_screen_space():
    draw_hud()
    draw_game_over()


def draw_scene():
    draw_background()
    draw_world_with_camera()
    draw_crane_screen_space()
    draw_hud_screen_space()


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    draw_scene()
    glutSwapBuffers()


def get_next_block_y():
    return max(tower_top_y() + BLOCK_H / 2 + 110, camera_offset + 640)


def reset_game():
    global tower, score, moving_x, moving_y, moving_speed
    global swing_angle, swing_direction, dropping, fall_x, fall_y
    global fall_vy, fall_angle, camera_offset, camera_target
    global tower_tilt, animation_time
    global collapse_started, collapsing, collapse_elapsed, collapse_angle
    global collapse_drop, game_over, status
    tower = [{
        "x": BASE_X,
        "y": BASE_Y + BLOCK_H / 2,
        "width": BLOCK_W,
        "height": BLOCK_H,
        "angle": 0.0,
    }]
    score = 0
    moving_x, moving_y, moving_speed = BASE_X, 690.0, 2.5
    swing_angle, swing_direction = 0.0, 1
    dropping = False
    fall_x, fall_y, fall_vy, fall_angle = BASE_X, 690.0, 0.0, 0.0
    camera_offset = 0.0
    camera_target = 0.0
    tower_tilt = 0.0
    animation_time = 0.0
    collapse_started = False
    collapsing = False
    collapse_elapsed = 0.0
    collapse_angle = 0.0
    collapse_drop = 0.0
    game_over = False
    status = "PRESS SPACE OR CLICK TO BUILD"
    moving_y = get_next_block_y()
    initialize_clouds()
    initialize_birds()


def start_tower_collapse():
    global collapse_started, collapsing, collapse_elapsed, collapse_angle
    global collapse_drop, status, dropping
    if collapse_started:
        return
    collapse_started = True
    collapsing = True
    collapse_elapsed = 0.0
    collapse_angle = 0.0
    collapse_drop = 0.0
    dropping = False
    status = "WARNING! TOWER IS UNSTABLE"


def finish_game_over():
    global collapsing, game_over, status, best_height
    collapsing = False
    game_over = True
    best_height = max(best_height, score)
    status = "GAME OVER"


def land_block():
    global dropping, moving_y, fall_y, fall_angle, status
    top = tower[-1]
    landing_y = top["y"] + BLOCK_H
    placed_rotation = 0.0
    tower.append({
        "x": fall_x,
        "y": landing_y,
        "width": BLOCK_W,
        "height": BLOCK_H,
        "angle": placed_rotation,
    })
    update_score()
    fall_y = landing_y
    fall_angle = placed_rotation
    dropping = False
    if not check_tower_stability():
        start_tower_collapse()
        return
    status = "NICE STACK!" if calculate_balance_value() >= 60 else "WATCH THE BALANCE!"
    moving_y = get_next_block_y()


def release_block():
    global dropping, fall_x, fall_y, fall_vy, fall_angle, status
    if game_over or collapsing or dropping:
        return
    dropping = True
    fall_x = moving_x
    fall_y = moving_y
    fall_vy = -1.0
    fall_angle = swing_angle * .22
    status = "BUILDING IN MOTION"


def update_score():
    global score, best_height
    score += 1
    best_height = max(best_height, score)


def update_crane():
    global moving_x, moving_y, moving_speed, swing_angle, swing_direction
    if dropping or game_over or collapsing:
        return
    speed = moving_speed * (1 + min(score * .015, 1.5))
    moving_x += speed
    if moving_x > 548:
        moving_x = 548
        moving_speed = -abs(moving_speed)
    elif moving_x < 52:
        moving_x = 52
        moving_speed = abs(moving_speed)
    swing_angle += swing_direction * .8
    if swing_angle > 24:
        swing_direction = -1
    elif swing_angle < -24:
        swing_direction = 1
    moving_y = get_next_block_y()


def update_falling_block():
    global fall_y, fall_vy, fall_angle
    if not dropping:
        return
    fall_vy -= .42
    fall_y += fall_vy
    fall_angle += swing_direction * .18
    top = tower[-1]
    landing_y = top["y"] + BLOCK_H
    if fall_y <= landing_y:
        fall_y = landing_y
        land_block()


def update_tower_collapse():
    global collapse_elapsed, collapse_angle, collapse_drop
    if not collapsing:
        return
    collapse_elapsed += FPS / 1000.0
    collapse_angle = min(82.0, collapse_elapsed * 58.0)
    collapse_drop = min(110.0, max(0.0, collapse_elapsed - .9) * 82.0)
    if collapse_elapsed >= 2.25:
        collapse_angle = 82.0
        collapse_drop = 110.0
        finish_game_over()


def update(value):
    if not game_over:
        if collapsing:
            update_tower_collapse()
        else:
            update_crane()
            update_falling_block()
            update_camera()
            update_tower_tilt()
    update_clouds()
    update_birds()
    glutPostRedisplay()
    glutTimerFunc(FPS, update, 0)


def keyboard(key, x, y):
    global moving_x
    if key == b"\x1b":
        sys.exit(0)
    if key in (b"r", b"R"):
        reset_game()
    elif key == b" ":
        release_block()
    elif not dropping and not game_over and not collapsing:
        if key in (b"a", b"A"):
            moving_x = max(52, moving_x - 18)
        elif key in (b"d", b"D"):
            moving_x = min(548, moving_x + 18)
    glutPostRedisplay()


def special_keys(key, x, y):
    global moving_x
    if dropping or game_over or collapsing:
        return
    if key == GLUT_KEY_LEFT:
        moving_x = max(52, moving_x - 18)
    elif key == GLUT_KEY_RIGHT:
        moving_x = min(548, moving_x + 18)
    glutPostRedisplay()


def mouse_click(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        release_block()
        glutPostRedisplay()


def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def initialize():
    glClearColor(.40, .76, .94, 1)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    reset_game()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(W, H)
    glutInitWindowPosition(250, 40)
    glutCreateWindow(b"City Skyline Builder - OpenGL")
    initialize()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse_click)
    glutTimerFunc(FPS, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()