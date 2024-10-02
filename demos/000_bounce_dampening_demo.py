import pygame
import math
import sys
import os

# Set the position of the window to the top-left corner
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

# Initialize Pygame
pygame.init()

# Set up display
#width, height = 1280, 720
width, height = 1920, 1080
ratio = width / 1280
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ball Bounce Dampening Demo")
font = 'Gill Sans'
header0 = pygame.font.SysFont(font, int(24 * ratio), True)

# Colors
RED = (250, 1, 62)
DARK_RED = (150, 0, 38)
DARK_BLUE = (19, 33, 45)
CYAN = (0, 255, 255)
DARK_CYAN = (0, 150, 150)
WHITE = (255, 255, 255)
GREEN = (32, 250, 32)
GRAY = (128, 128, 128)#

# Constants
CIRCLE2_RADIUS = int(24 * ratio)  # Radius for Circle 2
ARROW_LENGTH = 10 * ratio  # Initial length of arrow
ARROW_THICKNESS = 8 * ratio  # Thickness of the arrow

# Ball settings
ball_radius = int(24 * ratio) 
balls = []
del_balls_x = []
fall_speed_increment = 0.3 * ratio

# Component vector visibility toggle (on by default)
y_dampening = 0
sliders = {
    'y_dampening': {'pos': (50 * ratio, 80 * ratio), 'min': 0, 'max': 1},
}
for key, slider in sliders.items():
    slider['rect'] = pygame.Rect(slider['pos'][0], slider['pos'][1], 210 * ratio, 10 * ratio)
    slider['handle'] = pygame.Rect(slider['pos'][0], slider['pos'][1] - 5 * ratio, 10 * ratio, 20 * ratio)

pin_spacing = height / 4
pin_rows = 3
pin_start = height / 4
pins = []
def create_pins():
    """Creates pins based on current settings."""
    pins.clear()
    offset = pin_spacing // 2
    for row in range(0, pin_rows):
        row_offset = offset if row % 2 == 0 else 0
        for col in range(-(row// 2) - 1, (row - 1) // 2 + 2):
            x = width // 2 + col * pin_spacing + row_offset
            y = row * pin_spacing + pin_start
            pins.append((x, y))
# create_pins()

# Function to draw a vector with an arrowhead
def draw_vector_with_arrowhead(base_x, base_y, end_x, end_y, color, thickness, dampening = 0):
    end_x = end_x - dampening * (end_x - base_x)
    pygame.draw.line(screen, color, (base_x, base_y), (end_x, end_y), int(thickness))
    # Calculate direction of the line
    angle = math.atan2(end_y - base_y, end_x - base_x)
    # Calculate arrowhead points
    arrowhead_length = 20 * ratio
    inset_x =  -arrowhead_length * math.cos(angle) * 0.1
    inset_y =  -arrowhead_length * math.sin(angle) * 0.1
    tip_x = end_x + arrowhead_length * math.cos(angle) * 0.866 + inset_x
    tip_y = end_y + arrowhead_length * math.sin(angle) * 0.866 + inset_y
    left_x = end_x + arrowhead_length / 2 * math.cos(angle - math.pi / 2) + inset_x
    left_y = end_y + arrowhead_length / 2 * math.sin(angle - math.pi / 2) + inset_y
    right_x = end_x + arrowhead_length / 2 * math.cos(angle + math.pi / 2) + inset_x
    right_y = end_y + arrowhead_length / 2 * math.sin(angle + math.pi / 2) + inset_y
    # Draw arrowhead
    pygame.draw.polygon(screen, color, [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])

# Rounded rect gen
def draw_rounded_rect(surface, rect, color, corner_radius, corners=[True, True, True, True]):
    """ Draw a rectangle with selectable rounded or square corners on the given surface. """
    top_left, top_right, bottom_left, bottom_right = corners
    # Central rectangle, always drawn to avoid complexity in vertical and horizontal bars
    central_rect = pygame.Rect(rect.x + corner_radius, rect.y + corner_radius, rect.width - 2 * corner_radius, rect.height - 2 * corner_radius)
    pygame.draw.rect(surface, color, central_rect)

    # Horizontal and vertical bars
    horizontal_rect = pygame.Rect(rect.x + corner_radius, rect.y, rect.width - 2 * corner_radius, rect.height)
    vertical_rect = pygame.Rect(rect.x, rect.y + corner_radius, rect.width, rect.height - 2 * corner_radius)
    pygame.draw.rect(surface, color, horizontal_rect)
    pygame.draw.rect(surface, color, vertical_rect)

    # Helper function to draw a circle for the rounded corners
    def draw_corner_circle(center, radius, color):
        pygame.draw.circle(surface, color, center, radius)

    # Draw rounded corners if specified, otherwise fill in square corners
    if top_left: draw_corner_circle((rect.left + corner_radius, rect.top + corner_radius), corner_radius, color)
    else: pygame.draw.rect(surface, color, (rect.left, rect.top, corner_radius, corner_radius))

    if top_right:  draw_corner_circle((rect.right - corner_radius, rect.top + corner_radius), corner_radius, color)
    else: pygame.draw.rect(surface, color, (rect.right - corner_radius, rect.top, corner_radius, corner_radius))

    if bottom_left: draw_corner_circle((rect.left + corner_radius, rect.bottom - corner_radius), corner_radius, color)
    else: pygame.draw.rect(surface, color, (rect.left, rect.bottom - corner_radius, corner_radius, corner_radius))

    if bottom_right: draw_corner_circle((rect.right - corner_radius, rect.bottom - corner_radius), corner_radius, color)
    else: pygame.draw.rect(surface, color, (rect.right - corner_radius, rect.bottom - corner_radius, corner_radius, corner_radius))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                    start_x = width // 2
                    start_y = height // 2
                    # Add a new ball with initial position and speed
                    balls.clear()
                    balls.append([start_x, start_y, 0, 0])  # [x_position, y_position, x_speed, y_speed]
            elif event.key == pygame.K_r:
                balls.clear()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up to increase cyan line length
                y_dampening += 0.1
                if y_dampening > 1:  # Ensure there's a maximum length
                    y_dampening = 1
            elif event.button == 5:  # Scroll down to decrease cyan line length
                y_dampening -= 0.1
                if y_dampening < 0:  # Ensure there's a minimum length
                    y_dampening = 0

    # Fill the screen with the background color
    screen.fill(DARK_BLUE)

    # Update the position of each ball [x_position, y_position, x_speed, y_speed]
    for ball in balls:
        ball[0] += ball[2]  # Update x position by x speed
        ball[1] += ball[3]  # Update y position by y speed
        ball[3] += fall_speed_increment  # Apply gravity to y speed

        if ball[1] > height - ball_radius:
            ball[1] = height - ball_radius
            ball[3] = -ball[3] * (1 - y_dampening)
            if abs(ball[3]) < 1.5:
                ball[3] = 0

    if len(balls) > 0:
        draw_vector_with_arrowhead(balls[0][0], balls[0][1], balls[0][0] + ARROW_LENGTH * balls[0][2], balls[0][1] + ARROW_LENGTH * balls[0][3], DARK_RED, ARROW_THICKNESS)

    # Draw all the balls
    for ball in balls:
        pygame.draw.circle(screen, RED, (int(ball[0]), int(ball[1])), ball_radius)

    # Draw sliders and their labels
    for key, slider in sliders.items():
        header_text = header0.render(f"{key.replace('_', ' ').title()}", True, WHITE)
        header_rect = header_text.get_rect(topleft=(slider['pos'][0], slider['pos'][1] - 40 * ratio))
        screen.blit(header_text, header_rect)
        draw_rounded_rect(screen, slider['rect'], GRAY, 2 * ratio)
        slider['handle'].x = slider['pos'][0] + int((y_dampening - sliders[key]['min']) / (sliders[key]['max'] - sliders[key]['min']) * 200 * ratio)
        draw_rounded_rect(screen, slider['handle'], WHITE, 2 * ratio)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)
