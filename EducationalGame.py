from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import sys
import random
import time
import math

# --- Game Configuration ---
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
MAP_SIZE = 10.0
TEMPO_INICIAL = 30.0


class GameState:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        # Core gameplay state
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False

        # UI / feedback
        self.feedback_msg = "ALIGN THE SCANNER WITH THE FRACTION"
        self.bonus_msg = ""
        self.bonus_timer = 0

        # Player / time
        self.player_x = 5.0
        self.time_left = TEMPO_INICIAL
        self.last_time = time.time()

        # Particles: [x, y, z, vx, vy, vz, r, g, b]
        self.particles = []

        self.reset_level()

    def reset_level(self):
        max_den = min(4 + self.level, 12)
        self.denominator = random.randint(2, max_den)
        self.numerator = random.randint(1, self.denominator - 1)
        self.target_x = (self.numerator / self.denominator) * MAP_SIZE

    def spawn_particles(self, color):
        """Spawn particles with a given RGB color"""
        for _ in range(50):
            self.particles.append([
                self.target_x, 0.2, 0,
                random.uniform(-0.05, 0.05),
                random.uniform(0.05, 0.15),
                random.uniform(-0.05, 0.05),
                color[0], color[1], color[2]
            ])


game = GameState()


def draw_text(x, y, text, color=(1, 1, 1), font=GLUT_BITMAP_HELVETICA_18):
    """Render 2D text overlay"""
    glDisable(GL_LIGHTING)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(*color)
    glRasterPos2f(x, y)

    for char in text:
        glutBitmapCharacter(font, ord(char))

    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_LIGHTING)


def draw_time_bar():
    """Top screen time bar"""
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    percent = max(0, min(1, game.time_left / TEMPO_INICIAL))

    bar_width = 400
    bar_height = 20
    x_pos = (WINDOW_WIDTH - bar_width) / 2
    y_pos = 680

    # Dynamic color based on time
    if percent > 0.5:
        color = (0.0, 1.0, 1.0)
    elif percent > 0.2:
        color = (1.0, 1.0, 0.0)
    else:
        color = (1.0, 0.0, 0.0)

    # Background
    glColor4f(0.2, 0.2, 0.2, 0.8)
    glBegin(GL_QUADS)
    glVertex2f(x_pos, y_pos)
    glVertex2f(x_pos + bar_width, y_pos)
    glVertex2f(x_pos + bar_width, y_pos + bar_height)
    glVertex2f(x_pos, y_pos + bar_height)
    glEnd()

    # Fill
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x_pos, y_pos)
    glVertex2f(x_pos + (bar_width * percent), y_pos)
    glVertex2f(x_pos + (bar_width * percent), y_pos + bar_height)
    glVertex2f(x_pos, y_pos + bar_height)
    glEnd()

    # Border
    glColor3f(1, 1, 1)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x_pos, y_pos)
    glVertex2f(x_pos + bar_width, y_pos)
    glVertex2f(x_pos + bar_width, y_pos + bar_height)
    glVertex2f(x_pos, y_pos + bar_height)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)


def draw_grid_and_ruler():
    """Draw ground grid and measurement ruler"""
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glColor4f(0.1, 0.2, 0.4, 0.3)
    glBegin(GL_LINES)
    for i in range(-5, 16):
        glVertex3f(i, -0.5, -5)
        glVertex3f(i, -0.5, 5)
        glVertex3f(-5, -0.5, i)
        glVertex3f(15, -0.5, i)
    glEnd()

    glColor4f(0.0, 1.0, 1.0, 0.4)
    glLineWidth(3.0)

    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(10, 0, 0)
    glEnd()

    for i in range(11):
        alpha = 0.8 if i % 5 == 0 else 0.3

        glColor4f(0.0, 1.0, 1.0, alpha)
        glBegin(GL_LINES)
        glVertex3f(i, 0, -0.5)
        glVertex3f(i, 0, 0.5)
        glVertex3f(i, 0, 0)
        glVertex3f(i, 0.4, 0)
        glEnd()

    glLineWidth(1.0)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


def draw_scene():
    """Main render loop"""
    current_tick = time.time()
    dt = current_tick - game.last_time
    game.last_time = current_tick

    if not game.game_over:
        game.time_left -= dt
        if game.time_left <= 0:
            game.time_left = 0
            game.game_over = True

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(5.0, 4.5, 10.0, 5.0, 1.0, 0, 0, 1, 0)

    draw_grid_and_ruler()
    draw_time_bar()

    # --- Particle system ---
    if game.particles:
        glDisable(GL_LIGHTING)
        glPointSize(3.0)

        glBegin(GL_POINTS)
        for p in game.particles:
            glColor3f(p[6], p[7], p[8])
            glVertex3f(p[0], p[1], p[2])

            p[0] += p[3]
            p[1] += p[4]
            p[2] += p[5]
            p[4] -= 0.002
        glEnd()

        glEnable(GL_LIGHTING)

        game.particles = [p for p in game.particles if p[1] > -0.5]

    # --- Player (scanner) ---
    if game.lives == 3:
        color = (0.0, 0.8, 1.0)
    elif game.lives == 2:
        color = (0.7, 0.2, 0.9)
    else:
        color = (1.0, 0.1, 0.1)

    glPushMatrix()
    glTranslatef(game.player_x, 1.0, 0)
    glColor3f(*color)

    s = 1.0 + (0.15 * math.sin(time.time() * 12)) if game.lives == 1 else 1.0
    glScalef(s, s, s)

    glutSolidSphere(0.35, 20, 20)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glColor4f(color[0], color[1], color[2], 0.2)

    glRotatef(90, 1, 0, 0)
    glutSolidCone(0.5, 1.1, 20, 1)

    glDisable(GL_BLEND)
    glPopMatrix()

    # --- HUD ---
    screen_x = 210 + (game.player_x * 86.0)

    draw_text(screen_x, 230, f"{game.player_x:.1f}", color, GLUT_BITMAP_9_BY_15)
    draw_text(50, 670, f"SCORE: {game.score} | LIVES: {game.lives}")
    draw_text(50, 640, f"LEVEL: {game.level}")
    draw_text(950, 670, f"TARGET: {game.numerator} / {game.denominator}", (0.0, 1.0, 1.0))

    if game.game_over:
        msg = "SYSTEM FAILURE! Press 'R'" if game.lives <= 0 else "TIME UP! Press 'R'"
        draw_text(450, 130, msg, (1, 0.2, 0.2))
    else:
        draw_text(500, 130, game.feedback_msg, (0.5, 0.7, 1.0))

    if game.bonus_timer > 0:
        draw_text(580, 650, game.bonus_msg, (0.0, 1.0, 0.0))
        game.bonus_timer -= dt

    glutSwapBuffers()


def reshape(w, h):
    aspect = 16.0 / 9.0

    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, aspect, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)


def keyboard(key, x, y):
    key = key.decode("utf-8").lower()

    if key == 'r':
        game.reset_game()

    if not game.game_over:
        if key == 'a':
            game.player_x -= 0.1
        if key == 'd':
            game.player_x += 0.1

        if key == ' ':
            diff = abs(game.player_x - game.target_x)

            if diff < 0.25:
                game.score += 10
                game.lives = 3

                # Particle color logic
                if diff < 0.06:
                    particle_color = (0.2, 1.0, 0.3)  # Neon green (perfect)
                    add_time = 5.0
                else:
                    particle_color = (1.0, 0.6, 0.1)  # Neon orange (good hit)
                    add_time = 2.0

                game.spawn_particles(particle_color)

                game.bonus_msg = f"+{int(add_time)}s"
                game.time_left = min(TEMPO_INICIAL, game.time_left + add_time)
                game.bonus_timer = 1.0

                if game.score % 30 == 0:
                    game.level += 1

                game.feedback_msg = "SUCCESS! Area scanned."
                game.reset_level()
            else:
                game.lives -= 1
                game.feedback_msg = f"WARNING! Calibration error. Vitals: {game.lives}"

                if game.lives <= 0:
                    game.game_over = True

        game.player_x = max(0.0, min(10.0, round(game.player_x, 1)))

    glutPostRedisplay()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1280, 720)
    glutCreateWindow(b"Neon Fraction Scanner")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 10, 1])
    glClearColor(0.01, 0.01, 0.03, 1.0)

    glutReshapeFunc(reshape)
    glutDisplayFunc(draw_scene)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(draw_scene)

    glutMainLoop()


if __name__ == "__main__":
    main()