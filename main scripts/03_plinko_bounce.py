import sys
import io
import random
import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import os

# Set the position of the window to the top-left corner
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

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
black = (0, 0, 0)
green = (32, 250, 32)
hover_green = (24, 200, 24)
dark_green = (16, 150, 16)
button_color_states = (green, hover_green, dark_green)

# Font for the header
font = 'Gill Sans'
header0 = pygame.font.SysFont(font, int(24 * ratio), True)
header1 = pygame.font.SysFont(font, int(22 * ratio), True)
header2 = pygame.font.SysFont(font, int(14 * ratio), True)

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

def draw_rounded_rect(surface, rect, color, corner_radius):
    """Draw a rectangle with rounded corners on the given surface."""
    if rect.width < 2 * corner_radius or rect.height < 2 * corner_radius:
        raise ValueError("The rectangle dimensions must be greater than twice the corner radius.")

    # Draw inner rectangle
    inner_rect = pygame.Rect(rect.x + corner_radius, rect.y + corner_radius, rect.width - 2 * corner_radius, rect.height - 2 * corner_radius)
    pygame.draw.rect(surface, color, inner_rect)

    # Draw the four side rectangles
    pygame.draw.rect(surface, color, pygame.Rect(rect.x + corner_radius, rect.y, rect.width - 2 * corner_radius, corner_radius))
    pygame.draw.rect(surface, color, pygame.Rect(rect.x + corner_radius, rect.y + rect.height - corner_radius, rect.width - 2 * corner_radius, corner_radius))
    pygame.draw.rect(surface, color, pygame.Rect(rect.x, rect.y + corner_radius, corner_radius, rect.height - 2 * corner_radius))
    pygame.draw.rect(surface, color, pygame.Rect(rect.x + rect.width - corner_radius, rect.y + corner_radius, corner_radius, rect.height - 2 * corner_radius))

    # Draw four corner circles
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.x, rect.y, 2 * corner_radius, 2 * corner_radius))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.x + rect.width - 2 * corner_radius, rect.y, 2 * corner_radius, 2 * corner_radius))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.x, rect.y + rect.height - 2 * corner_radius, 2 * corner_radius, 2 * corner_radius))
    pygame.draw.ellipse(surface, color, pygame.Rect(rect.x + rect.width - 2 * corner_radius, rect.y + rect.height - 2 * corner_radius, 2 * corner_radius, 2 * corner_radius))

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

# Button settings
button_y = 255
button_rect = pygame.Rect(50 * ratio, button_y * ratio, 210 * ratio, 50 * ratio)
button_under_rect = pygame.Rect(50 * ratio, (button_y + 7) * ratio, 210 * ratio, 50 * ratio)
button_clicked = False

def render_button(button_clicked):
    """Handle button states and actions."""
    mouse = pygame.mouse.get_pos()
    # Only change color on hover; clicking is handled via event loop
    button_text = header1.render("Drop", True, black)
    if button_clicked:
        draw_rounded_rect(screen, button_under_rect, button_color_states[1], 10)
        text_rect = button_text.get_rect(center=(160 * ratio, (button_y + 32) * ratio))
    else:
        text_rect = button_text.get_rect(center=(160 * ratio, (button_y + 25) * ratio))
        draw_rounded_rect(screen, button_under_rect, button_color_states[2], int(10 * ratio))
        if button_rect.collidepoint(mouse):
            draw_rounded_rect(screen, button_rect, button_color_states[1], int(10 * ratio))
        else:
            draw_rounded_rect(screen, button_rect, button_color_states[0], int(10 * ratio))
    screen.blit(button_text, text_rect)
    return button_rect.collidepoint(mouse)

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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if render_button(button_clicked) and not button_clicked:
                button_clicked = True
                for idx in range(balls_at_once):
                    # Updated start_x based on pin_spacing and pin_radius
                    start_x = random.randint(width // 2 - pin_spacing + pin_radius, width // 2 + pin_spacing - pin_radius)
                    # Add a new ball with initial position and speed
                    balls.append([start_x, random.randint(-2*ball_radius,-ball_radius), 0, 0])  # [x_position, y_position, x_speed, y_speed]
        elif event.type == pygame.MOUSEBUTTONUP:
            button_clicked = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                for idx in range(balls_at_once):
                    # Updated start_x based on pin_spacing and pin_radius
                    start_x = random.randint(width // 2 - pin_spacing + pin_radius, width // 2 + pin_spacing - pin_radius)
                    # Add a new ball with initial position and speed
                    balls.append([start_x, random.randint(-2*ball_radius,-ball_radius), 0, 0])  # [x_position, y_position, x_speed, y_speed]
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
    for ball in balls:
        ball[0] += ball[2]  # Update x position by x speed
        ball[1] += ball[3]  # Update y position by y speed
        ball[3] += fall_speed_increment  # Apply gravity to y speed

        # Check for collisions with pins
        for pin_x, pin_y in pins:
            dist_sq = (ball[0] - pin_x) ** 2 + (ball[1] - pin_y) ** 2
            radius_sum = ball_radius + pin_radius
            if dist_sq < radius_sum ** 2:
                overlap = radius_sum - np.sqrt(dist_sq)
                angle = np.arctan2(ball[1] - pin_y, ball[0] - pin_x)

                # Move the ball away from the pin a bit further than the overlap
                displacement = overlap + 0.5  # Extra 0.5 pixels to ensure it moves out of collision
                ball[0] += np.cos(angle) * displacement
                ball[1] += np.sin(angle) * displacement

                # Reflect the velocity and add randomness
                normal_vector = np.array([np.cos(angle), np.sin(angle)])
                velocity_vector = np.array([ball[2], ball[3]])
                reflected_velocity = velocity_vector - 2 * np.dot(velocity_vector, normal_vector) * normal_vector
                random_factor = 0.35 + random.uniform(-0.1, 0.1)  # Random factor between 0.85 and 1.05

                # Apply randomness and dampening
                ball[2], ball[3] = reflected_velocity * random_factor

                direction_change = random.choice([-1, 1])
                ball[0] += direction_change

        if ball[1] > (pin_rows+0.5) * pin_spacing + pin_start:
            ball[1] = height - ball_radius  # Stop the ball at the bottom
            bin = int(((ball[0] - (width // 2) + (not pin_rows%2) * pin_spacing//2) + (pin_spacing * ((pin_rows + 1) // 2))) // pin_spacing)
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
        pygame.draw.circle(screen, red, (int(ball[0]), int(ball[1])), ball_radius)

    # Draw sliders and their labels
    for key, slider in sliders.items():
        header_text = header0.render(f"{key.replace('_', ' ').title()}", True, white)
        header_rect = header_text.get_rect(topleft=(slider['pos'][0], slider['pos'][1] - 32 * ratio))
        screen.blit(header_text, header_rect)
        draw_rounded_rect(screen, slider['rect'], gray, 3 + (ratio > 1))
        slider['handle'].x = slider['pos'][0] + int((slider['value'] - sliders[key]['min']) / (sliders[key]['max'] - sliders[key]['min']) * 200 * ratio)
        draw_rounded_rect(screen, slider['handle'], white, 3 + (ratio > 1))

    # Display Plot
    if plot_image:
        screen.blit(plot_image, (0.75 * width, 20))
        if frame_counter >= 30 and plot_update:
            plot_image = update_plot(del_balls_x)
            frame_counter = 0
            plot_update = False
    
    # Render the button
    render_button(button_clicked)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)
