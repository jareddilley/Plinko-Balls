'''
v0 basic plinko game with no bounce collision
Inputs -
    drop ball - click green "Drop" button or click SPACE
    reset board - press R
    change number of pin rows - click on "Rows" slider to change (no grab and drag)
    change ball radius - click on "Ball Size" slider to change (no grab and drag)
    change number of balls at once - click on "Ball(s) at Once" slider to change (no grab and drag)
Author - Jared Dilley
GitHub - https://github.com/jareddilley
'''
import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()

# Set up display
#width, height = 1280, 720
width, height = 1920, 1080
ratio = width / 1280
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Plinko Game")

# Define colors
background = (19, 33, 45)
red = (250, 1, 62)
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
ball_radius = int(9 * ratio)  # Updated ball radius
balls = []  # List to store ball positions and speeds
fall_speed_increment = 0.1 * ratio  # Acceleration rate
balls_at_once = 1

# Pin settings
pins = []
pin_radius = int(5 * ratio)
pin_spacing = int(40 * ratio)
pin_rows = 14  # Default number of rows of pins
pin_start = 60  # Updated vertical starting position of pins
pin_cols = 14

# Updated function to create pins based on current pin_rows
def create_pins():
    pins.clear()
    for row in range(1, pin_rows + 1):  # Loop through rows starting from 1
        offset = 0 if row % 2 else pin_spacing // 2
        for col in range(pin_cols // 2 + 1):
            x = (width // 2 - pin_spacing + offset) + col * pin_spacing
            x2 = (width // 2 + pin_spacing - offset) - col * pin_spacing
            y = (row * pin_spacing) + pin_start  # Use pin_start for the y-offset
            pins.append((x, y))
            if x != x2: pins.append((x2, y))

# Create initial pins
create_pins()

# Slider settings
slider_width = 200 * ratio
slider_height = 10 * ratio
slider_pos_0 = (50 * ratio, 50 * ratio)  # Slider position at the top-left corner
slider_pos_1 = (50 * ratio, 125 * ratio)  # Slider position at the top-left corner
slider_pos_2 = (50 * ratio, 200 * ratio)  # Slider position at the top-left corner
slider_rect_0 = pygame.Rect(slider_pos_0[0], slider_pos_0[1], slider_width + 10, slider_height)
slider_handle_rect_0 = pygame.Rect(slider_pos_0[0] + (pin_rows - 5 * ratio) * (slider_width // 10), slider_pos_0[1] - 5 * ratio, 10 * ratio, 20 * ratio)
slider_rect_1 = pygame.Rect(slider_pos_1[0], slider_pos_1[1], slider_width + 10, slider_height)
slider_handle_rect_1 = pygame.Rect(slider_pos_1[0] + (pin_rows - 5 * ratio) * (slider_width // 10), slider_pos_1[1] - 5 * ratio, 10 * ratio, 20 * ratio)
slider_rect_2 = pygame.Rect(slider_pos_2[0], slider_pos_2[1], slider_width + 10, slider_height)
slider_handle_rect_2 = pygame.Rect(slider_pos_2[0] + (pin_rows - 5 * ratio) * (slider_width // 10), slider_pos_2[1] - 5 * ratio, 10 * ratio, 20 * ratio)
slider_0_min = 5
slider_0_max = 15
slider_1_min = 5 * ratio
slider_1_max = (pin_spacing) // 2
slider_2_min = 1
slider_2_max = 50

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
        pygame.draw.rect(screen, button_color_states[1], button_under_rect)
        text_rect = button_text.get_rect(center=(160 * ratio, (button_y + 32) * ratio))
    else:
        text_rect = button_text.get_rect(center=(160 * ratio, (button_y + 25) * ratio))
        pygame.draw.rect(screen, button_color_states[2], button_under_rect)
        if button_rect.collidepoint(mouse):
            pygame.draw.rect(screen, button_color_states[1], button_rect)
        else:
            pygame.draw.rect(screen, button_color_states[0], button_rect)
    screen.blit(button_text, text_rect)
    return button_rect.collidepoint(mouse)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if render_button(button_clicked) and not button_clicked:
                button_clicked = True
                for idx in range(balls_at_once):
                    # Updated start_x based on pin_spacing and pin_radius
                    start_x = random.randint(width // 2 - pin_spacing * (pin_cols - 1) // 2 + pin_radius, width // 2 + pin_spacing * (pin_cols - 1) // 2 - pin_radius)
                    # Add a new ball with initial position and speed
                    balls.append([random.randint(-2*ball_radius,-ball_radius), 0, start_x])  # [y_position, y_speed, x_position]
        elif event.type == pygame.MOUSEBUTTONUP:
            button_clicked = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                for idx in range(balls_at_once):
                    # Updated start_x based on pin_spacing and pin_radius
                    start_x = random.randint(width // 2 - pin_spacing * (pin_cols - 1) // 2 + pin_radius, width // 2 + pin_spacing * (pin_cols - 1) // 2 - pin_radius)
                    # Add a new ball with initial position and speed
                    balls.append([random.randint(-2*ball_radius,-ball_radius), 0, start_x])  # [y_position, y_speed, x_position]
            elif event.key == pygame.K_r:
                # Reset all
                pin_rows = 14
                create_pins()
                balls_at_once = 1
                ball_radius = int(9 * ratio) 
                balls.clear()
        
        # Handle mouse input for slider
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if slider_rect_0.collidepoint(event.pos):
                # Map the mouse position (slider) 
                pin_rows = int(slider_0_min + (event.pos[0] - slider_pos_0[0]) / slider_width * (slider_0_max - slider_0_min))
                pin_rows = max(slider_0_min, min(pin_rows, slider_0_max))  # Limit rows 
                create_pins()  # Recreate pins based on new pin_rows
            if slider_rect_1.collidepoint(event.pos):
                # Map the mouse position (slider) 
                ball_radius = int(slider_1_min + (event.pos[0] - slider_pos_1[0]) / slider_width * (slider_1_max - slider_1_min))
                ball_radius = max(slider_1_min, min(ball_radius, slider_1_max))  # Limit ball radius
            if slider_rect_2.collidepoint(event.pos):
                # Map the mouse position (slider) 
                balls_at_once = int(slider_2_min + (event.pos[0]- slider_pos_2[0]) / slider_width * (slider_2_max - slider_2_min))
                balls_at_once = max(slider_2_min, min(balls_at_once, slider_2_max))  # Limit balls at once

    # Update the position of each ball
    for ball in balls:
        ball[1] += fall_speed_increment  # Increase speed due to acceleration
        ball[0] += ball[1]  # Update y position based on speed

        # Check for collisions with pins
        for pin_x, pin_y in pins:
            if (ball[2] - pin_x)**2 + (ball[0] - pin_y)**2 < (ball_radius + pin_radius)**2:
                # Improved collision response: randomize the direction change
                direction_change = random.choice([-10, 10])  # Randomly choose left or right direction
                ball[2] += direction_change
                break

        if ball[0] > height - ball_radius:
            ball[0] = height - ball_radius  # Stop the ball at the bottom

    # Fill the screen with the background color
    screen.fill(background)

    # Draw pins
    for pin_x, pin_y in pins:
        pygame.draw.circle(screen, white, (int(pin_x), int(pin_y)), pin_radius)

    # Draw all the balls
    for ball in balls:
        pygame.draw.circle(screen, red, (int(ball[2]), int(ball[0])), ball_radius)

    ### Sliders
    # Rows
    header_text_0 = header0.render("Rows", True, white)
    header_rect_0 = header_text_0.get_rect(topleft=(slider_pos_0[0], slider_pos_0[1] - 32* ratio))  # Left-aligned and moved down 5 pixels
    screen.blit(header_text_0, header_rect_0)
    pygame.draw.rect(screen, gray, slider_rect_0) # slider rail
    slider_handle_rect_0.x = slider_pos_0[0] + (pin_rows - slider_0_min) * (slider_width // (slider_0_max - slider_0_min))
    pygame.draw.rect(screen, white, slider_handle_rect_0) # slider knob

    # Ball size
    header_text_1 = header0.render("Ball Size", True, white)
    header_rect_1 = header_text_1.get_rect(topleft=(slider_pos_1[0], slider_pos_1[1] - 32* ratio))  # Left-aligned and moved down 5 pixels
    screen.blit(header_text_1, header_rect_1)
    pygame.draw.rect(screen, gray, slider_rect_1) # slider rail
    slider_handle_rect_1.x = slider_pos_1[0] + (ball_radius - slider_1_min) * (slider_width // (slider_1_max - slider_1_min))
    pygame.draw.rect(screen, white, slider_handle_rect_1) # slider knob

    # Balls at once
    header_text_2 = header0.render("Ball(s) at Once", True, white)
    header_rect_2 = header_text_2.get_rect(topleft=(slider_pos_2[0], slider_pos_2[1] - 32* ratio))  # Left-aligned and moved down 5 pixels
    screen.blit(header_text_2, header_rect_2)
    pygame.draw.rect(screen, gray, slider_rect_2) # slider rail
    slider_handle_rect_2.x = slider_pos_2[0] + (balls_at_once - slider_2_min) * (slider_width // (slider_2_max - slider_2_min))
    pygame.draw.rect(screen, white, slider_handle_rect_2) # slider knob

    # Render the button
    render_button(button_clicked)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)
