import pygame
import sys
import io
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np

# Initialize Pygame
pygame.init()

# Set up display
# width, height = 1280, 720
width, height = 1920, 1080
ratio = width / 1280
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Plinko Game")

# Frame counter
frame_counter = 0

# Define colors
background = (19, 33, 45)
red = (250, 1, 62)
plt_background = tuple([x/255 for x in background])
plt_red = tuple([x/255 for x in red])
white = (255, 255, 255)
gray = (200, 200, 200)

# Font for the header
font = 'Gill Sans'
header0 = pygame.font.SysFont(font, int(24 * ratio), True)

# Ball settings
ball_radius = int(9 * ratio) 
balls = []
del_balls_x = []
fall_speed_increment = 0.3 * ratio
balls_at_once = 1

# Pin settings
pins = []
pin_radius = int(5 * ratio)
pin_spacing = int(40 * ratio)
pin_rows = 15
pin_start = 30 * ratio

# Set Plot defaults
plot_update = False
plt.switch_backend('Agg')
plt.rcParams['figure.figsize'] = [3 * ratio, 2 * ratio]
plt.rcParams['figure.facecolor'] = plt_background 
plt.rcParams['axes.facecolor'] = plt_background
plt.rcParams['xtick.labelsize'] = 0
plt.rcParams['ytick.left'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.left'] = False
plt.rcParams['figure.subplot.left'] = 0
plt.rcParams['figure.subplot.right'] = 1 
plt.rcParams['figure.subplot.top'] = 1
fig, ax = plt.subplots()
canvas = FigureCanvas(fig)

def create_pins():
    """Creates pins based on current settings."""
    pins.clear()
    offset = pin_spacing // 2
    for row in range(1, pin_rows + 1):
        row_offset = offset if row % 2 == 0 else 0
        for col in range(-(row// 2) - 1, (row - 1) // 2 + 2):
            x = width // 2 + col * pin_spacing + row_offset
            y = row * pin_spacing + pin_start
            pins.append((x, y))

def update_plot(del_balls_x):
    """Updates the histogram plot of ball locations."""
    bins = np.arange(0, pin_rows + 2, 1)
    ax.clear()
    ax.hist(del_balls_x, bins=bins, color=plt_red, edgecolor=plt_background)
    ax.set_xticks(bins)
    # Save to a BytesIO object instead of disk
    buf = io.BytesIO()
    canvas.print_png(buf)
    buf.seek(0)
    image = pygame.image.load(buf)
    buf.close()
    return image

create_pins()
plot_image = update_plot(del_balls_x)

# Slider settings
sliders = {
    'rows': {'pos': (50 * ratio, 50 * ratio), 'min': 5, 'max': 15, 'value': pin_rows},
    'ball_size': {'pos': (50 * ratio, 125 * ratio), 'min': 5 * ratio, 'max': (pin_spacing - 2*pin_radius) // 2 - 1, 'value': ball_radius},
    'balls_at_once': {'pos': (50 * ratio, 200 * ratio), 'min': 1, 'max': 50, 'value': balls_at_once}
}
for key, slider in sliders.items():
    slider['rect'] = pygame.Rect(slider['pos'][0], slider['pos'][1], 210 * ratio, 10 * ratio)
    slider['handle'] = pygame.Rect(slider['pos'][0], slider['pos'][1] - 5 * ratio, 10 * ratio, 20 * ratio)

def handle_sliders(event):
    global plot_update, del_balls_x
    """Handles slider movements and updates relevant variables."""
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for key, slider in sliders.items():
            if slider['rect'].collidepoint(event.pos):
                value = int(slider['min'] + (event.pos[0] - slider['pos'][0]) / (200 * ratio) * (slider['max'] - slider['min']))
                value = max(slider['min'], min(value, slider['max']))
                if key == 'rows':
                    global pin_rows
                    pin_rows = value
                    create_pins()
                    del_balls_x.clear()
                    update_plot(del_balls_x)
                    plot_update = True
                elif key == 'ball_size':
                    global ball_radius
                    ball_radius = value
                elif key == 'balls_at_once':
                    global balls_at_once
                    balls_at_once = value
                slider['value'] = value

def reset_sliders():
    """Rest slider pos."""
    for key, slider in sliders.items():
        if key == 'rows':
            global pin_rows
            slider['value'] = pin_rows
            create_pins()
        elif key == 'ball_size':
            global ball_radius
            slider['value'] = ball_radius
        elif key == 'balls_at_once':
            global balls_at_once
            slider['value'] = balls_at_once

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
                for idx in range(balls_at_once):
                    # Updated start_x based on pin_spacing and pin_radius
                    start_x = random.randint(width // 2 - pin_spacing + pin_radius, width // 2 + pin_spacing - pin_radius)
                    # Add a new ball with initial position and speed
                    balls.append([random.randint(-2*ball_radius,-ball_radius), 0, start_x])  # [y_position, y_speed, x_position]
            elif event.key == pygame.K_r:
                # Reset all
                pin_rows = 15
                create_pins()
                balls_at_once = 1
                ball_radius = int(9 * ratio)
                balls.clear()
                del_balls_x.clear()
                plot_image = update_plot(del_balls_x) 
                reset_sliders()
        handle_sliders(event)
    frame_counter += 1

    # Update the position of each ball
    for ball in balls.copy():
        ball[1] += fall_speed_increment  # Increase speed due to acceleration
        ball[0] += ball[1]  # Update y position based on speed

        # Check for collisions with pins
        for pin_x, pin_y in pins:
            if (ball[2] - pin_x)**2 + (ball[0] - pin_y)**2 < (ball_radius + pin_radius)**2:
                direction_change = random.choice([-10, 10])  # Randomly choose left or right direction
                ball[2] += direction_change
                break

        if ball[0] > (pin_rows+0.5) * pin_spacing + pin_start:
            ball[0] = height - ball_radius  # Stop the ball at the bottom
            bin = int(((ball[2] - (width // 2) + (not pin_rows%2) * pin_spacing//2) + (pin_spacing * ((pin_rows + 1) // 2))) // pin_spacing)
            del_balls_x.append(bin)
            balls.remove(ball)
            plot_update = True

    # Fill the screen with the background color
    screen.fill(background)

    # Draw pins
    for pin_x, pin_y in pins:
        pygame.draw.circle(screen, white, (int(pin_x), int(pin_y)), pin_radius)

    # Draw all the balls
    for ball in balls:
        pygame.draw.circle(screen, red, (int(ball[2]), int(ball[0])), ball_radius)

    # Draw sliders and their labels
    for key, slider in sliders.items():
        header_text = header0.render(f"{key.replace('_', ' ').title()}", True, white)
        header_rect = header_text.get_rect(topleft=(slider['pos'][0], slider['pos'][1] - 32 * ratio))
        screen.blit(header_text, header_rect)
        pygame.draw.rect(screen, gray, slider['rect'])
        slider['handle'].x = slider['pos'][0] + int((slider['value'] - sliders[key]['min']) / (sliders[key]['max'] - sliders[key]['min']) * 200 * ratio)
        pygame.draw.rect(screen, white, slider['handle'])

    # Display Plot
    if plot_image:
        screen.blit(plot_image, (0.75 * width, 20))
        if frame_counter >= 30 and plot_update:
            plot_image = update_plot(del_balls_x)
            frame_counter = 0
            plot_update = False

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)
