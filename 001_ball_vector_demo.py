import pygame
import math
import sys

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Vector Direction Demo")

# Set the screen resolution
#width, height = 1280, 720
width, height = 1920, 1080
ratio = width / 1280
screen = pygame.display.set_mode((width, height))
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
GRAY = (128, 128, 128)

# Constants
CIRCLE1_RADIUS = int(16 * ratio)  # Radius for Circle 1
CIRCLE2_RADIUS = int(24 * ratio)  # Radius for Circle 2
ARROW_LENGTH = 0  # Initial length of the cyan line, adjustable
ARROW_THICKNESS = 0  # Thickness of the arrow

# Component vector visibility toggle (on by default)
show_components = False
x_dampening = 0
touching_x, touching_y = 0, 0
sliders = {
    'x_dampening': {'pos': (50 * ratio, 80 * ratio), 'min': 0, 'max': 1},
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
create_pins()

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

# Main loop
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
            elif event.key == pygame.K_SPACE:  # Toggle component vectors with the space key
                show_components = not show_components
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up to increase cyan line length
                x_dampening += 0.1
                if x_dampening > 1:  # Ensure there's a maximum length
                    x_dampening = 1
            elif event.button == 5:  # Scroll down to decrease cyan line length
                x_dampening -= 0.1
                if x_dampening < 0:  # Ensure there's a minimum length
                    x_dampening = 0

    # Clear the screen with the background color
    screen.fill(DARK_BLUE)

    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate distance and prevent overlap
    touching = False
    for pin_x, pin_y in pins:
        # dist_sq = (ball[0] - pin_x) ** 2 + (ball[1] - pin_y) ** 2
        dist = math.sqrt((pin_x - mouse_x)**2 + (pin_y - mouse_y)**2)
        min_dist = CIRCLE1_RADIUS + CIRCLE2_RADIUS
        if dist <= min_dist:
            touching = True
            touching_x, touching_y = pin_x, pin_y
            break

    # Adjust position if touching
    if touching:
        angle = math.atan2(mouse_y - touching_y, mouse_x - touching_x)
        mouse_x = touching_x + (min_dist * math.cos(angle))
        mouse_y = touching_y + (min_dist * math.sin(angle))
    
    # Calculate the vector direction based on touching
    angle = math.atan2(touching_y - mouse_y, touching_x - mouse_x)
    if touching:
        ARROW_LENGTH = 150 * ratio
        ARROW_THICKNESS = 8 * ratio
        # Reverse direction if touching
        angle += math.pi
    else:
        ARROW_LENGTH = 0
        ARROW_THICKNESS = 0

    # Calculate the end point of the cyan line
    cyan_end_x = mouse_x + ARROW_LENGTH * math.cos(angle)
    cyan_end_y = mouse_y + ARROW_LENGTH * math.sin(angle)

    # Draw the pins
    for pin_x, pin_y in pins:
        pygame.draw.circle(screen, WHITE, (int(pin_x), int(pin_y)), CIRCLE1_RADIUS)

    # Draw the main cyan vector with arrowhead
    draw_vector_with_arrowhead(mouse_x, mouse_y, cyan_end_x, cyan_end_y, DARK_RED, ARROW_THICKNESS)
    draw_vector_with_arrowhead(mouse_x, mouse_y, cyan_end_x, cyan_end_y, RED, ARROW_THICKNESS, x_dampening)

    # Draw component vectors if toggled on
    if show_components:
        # X-component vector (horizontal)
        draw_vector_with_arrowhead(mouse_x, mouse_y, cyan_end_x, mouse_y, DARK_CYAN, ARROW_THICKNESS)
        draw_vector_with_arrowhead(mouse_x, mouse_y, cyan_end_x, mouse_y, CYAN, ARROW_THICKNESS, x_dampening)
        # Y-component vector (vertical)
        draw_vector_with_arrowhead(mouse_x, mouse_y, mouse_x, cyan_end_y, GREEN, ARROW_THICKNESS)

    pygame.draw.circle(screen, RED, (int(mouse_x), int(mouse_y)), CIRCLE2_RADIUS)

    # Draw sliders and their labels
    for key, slider in sliders.items():
        header_text = header0.render(f"{key.replace('_', ' ').title()}", True, WHITE)
        header_rect = header_text.get_rect(topleft=(slider['pos'][0], slider['pos'][1] - 40 * ratio))
        screen.blit(header_text, header_rect)
        draw_rounded_rect(screen, slider['rect'], GRAY, 2 * ratio)
        slider['handle'].x = slider['pos'][0] + int((x_dampening - sliders[key]['min']) / (sliders[key]['max'] - sliders[key]['min']) * 200 * ratio)
        draw_rounded_rect(screen, slider['handle'], WHITE, 2 * ratio)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
