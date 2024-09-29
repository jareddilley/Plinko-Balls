import sys
import io
import random
import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np

# Initialize Pygame
pygame.init()

score_sound = pygame.mixer.Sound('sounds/score.wav')
score_sound.set_volume(0.3)
click_sound = pygame.mixer.Sound('sounds/click.wav')
click_sound.set_volume(0.4)
error_sound = pygame.mixer.Sound('sounds/error.wav')
error_sound.set_volume(0.2)

# Set up display
#width, height = 1280, 720
width, height = 1920, 1080
ratio = width / 1280
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Plinko Game")

# Frame counter
frame_counter = 0

# Pin settings
pins = []
pin_radius = int(5 * ratio)
pin_spacing = int(40 * ratio)
pin_rows = 16
pin_start = 0

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
create_pins()

# Define colors
def convert_color(rgb_color):
    return tuple([x / 255 for x in rgb_color])

background = (19, 33, 45)
red = (250, 1, 62)
yellow = (252, 192, 2)
dark_red = (146, 0, 7)
dark_yellow = (155, 120, 0)
plt_background = convert_color(background)
plt_red = convert_color(red)
plt_yellow = convert_color(yellow)
white = (255, 255, 255)
gray = (128, 128, 128)
opaque_white = (255, 255, 255, 150)
black = (0, 0, 0)
green = (32, 250, 32)
plt_green = convert_color(green)
hover_green = (24, 200, 24)
dark_green = (16, 150, 16)
button_color_states = (green, hover_green, dark_green)

def create_rgb_gradient(start_color, end_color, steps):
    """Generate a list of RGB colors forming a gradient between two given RGB colors."""
    # Calculate the difference per step
    step_red = (end_color[0] - start_color[0]) / (steps - 1)
    step_green = (end_color[1] - start_color[1]) / (steps - 1)
    step_blue = (end_color[2] - start_color[2]) / (steps - 1)

    # Generate the gradient list
    gradient = [
        (
            int(start_color[0] + step_red * i),
            int(start_color[1] + step_green * i),
            int(start_color[2] + step_blue * i)
        )
        for i in range(steps)
    ]
    return gradient

# Fonts for the headers
font = 'Gill Sans'
header0 = pygame.font.SysFont(font, int(24 * ratio), True)
header1 = pygame.font.SysFont(font, int(22 * ratio), True)
header2 = pygame.font.SysFont(font, int(14 * ratio), True)
header_money = pygame.font.SysFont(font, int(36 * ratio), True)

# Bin settings
rgb_gradient = create_rgb_gradient(red, yellow, (pin_rows+2) // 2)
rgb_gradient_rev = rgb_gradient[::-1]
rgb_gradient.extend(rgb_gradient_rev[1:])
dark_rgb_gradient = create_rgb_gradient(dark_red, dark_yellow, (pin_rows+2) // 2)
dark_rgb_gradient_rev = dark_rgb_gradient[::-1]
dark_rgb_gradient.extend(dark_rgb_gradient_rev[1:])
bin_texts = ['1000', '130', '26x', '9x', '4x', '2x', '0.2x', '0.2x', '0.2x','0.2x','0.2x','2x','4x','9x','26x', '130', '1000']
low_bin_texts = ['1', '1', '1', '9x', '5x', '2x', '1x', '0.5x', '0.2x', '0.5x', '1x', '2x', '5x', '9x', '1', '1', '1']
bin_width = pin_spacing * 0.8
recent_bins = [bin_texts[7],bin_texts[8],bin_texts[9],bin_texts[10]]
recent_bin_colors = [rgb_gradient[7],rgb_gradient[8],rgb_gradient[9],rgb_gradient[10]]

def create_bin_text_surfaces():
    global pin_rows
    """Pre-render all bin texts."""
    bin_text_surfaces = []
    texts = bin_texts
    if pin_rows < 10: texts = low_bin_texts
    for text in texts:
        rendered_text = header2.render(text, True, black)
        bin_text_surfaces.append(rendered_text)
    return bin_text_surfaces

# Pre-render bin texts
hit_bins=[7,8,9,10]

def render_bins():
    global hit_bins
    bin_text_surfaces = create_bin_text_surfaces()
    click_offset = 4 * ratio
    bin_start_offset = width // 2 - (pin_rows // 2 + 0.5) * pin_spacing
    base_y = pin_rows * pin_spacing + pin_start + pin_spacing // 2
    for bin in range(pin_rows + 1):
        animate = True if bin in hit_bins else False # if hit

        offset_x = bin * pin_spacing + (not pin_rows % 2) * pin_spacing // 2
        index = bin + 8 - pin_rows//2
        if pin_rows % 2 and bin <= pin_rows//2: index -= 1

        bin_text_surface = bin_text_surfaces[index]

        base_x = bin_start_offset - bin_width // 2 + offset_x

        if animate:
            # Configure Rects for drawing  
            light_rect_right = pygame.Rect(base_x, base_y + click_offset, bin_width, bin_width)
            text_rect = bin_text_surface.get_rect(center=(base_x + bin_width // 2, base_y + bin_width // 2 + click_offset))

            # Remove animated bin
            hit_bins = list(filter(lambda x: x != bin, hit_bins))
        else:
            # Configure Rects for drawing  
            dark_rect_right = pygame.Rect(base_x, base_y + click_offset, bin_width, bin_width)       
            light_rect_right = pygame.Rect(base_x, base_y, bin_width, bin_width)
            text_rect = bin_text_surface.get_rect(center=(base_x + bin_width // 2, base_y + bin_width // 2))

            # Draw dark rectangle
            draw_rounded_rect(screen, dark_rect_right, dark_rgb_gradient[index], int(4 * ratio) + (ratio > 1))            
        
        # Draw light rectangle and text
        draw_rounded_rect(screen, light_rect_right, rgb_gradient[index], int(4 * ratio) + (ratio > 1))
        screen.blit(bin_text_surface, text_rect)

def display_last_bins(recent_bins, recent_bin_colors):
    num_bins = len(recent_bins)
    display_size = int(70 * ratio)
    curve = int(12 * ratio)
    display_start_x = width * 0.91
    display_start_y = 0.9 * height - 0.75 * display_size - (4 - num_bins) * display_size
    # [top_left, top_right, bottom_left, bottom_right]
    four_corners = [[False, False, False, False]] * num_bins
    if num_bins == 1: four_corners[0] = [True, True, True, True]
    elif num_bins > 1:
        four_corners[0] = [False, False, True, True]
        four_corners[-1] = [True, True, False, False]
    for bin in range(num_bins): 
        base_y = display_start_y - bin * display_size
        # Display rectangle     
        rect = pygame.Rect(display_start_x, base_y, display_size, display_size)
        draw_rounded_rect(screen, rect, recent_bin_colors[bin], curve, four_corners[bin])

        # Text rendering
        rendered_text = header1.render(recent_bins[bin], True, black)
        text_rect = rendered_text.get_rect(center=(display_start_x + display_size // 2, base_y + display_size // 2))
        screen.blit(rendered_text, text_rect)

# Ball settings
ball_radius = int(9 * ratio) 
balls = []
del_balls_x = []
fall_speed_increment = 0.6 * ratio
balls_at_once = 1

# Set Plot defaults
plot_update = False
plt.switch_backend('Agg') 
plt.rcParams['xtick.color'] = plt_background 
plt.rcParams['axes.linewidth'] = 2
plt.rcParams['figure.facecolor'] = plt_background 
plt.rcParams['axes.facecolor'] = plt_background
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.left'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['figure.subplot.left'] = 0
plt.rcParams['figure.subplot.right'] = 1 
plt.rcParams['figure.subplot.top'] = 1
# plt.rcParams['figure.figsize'] = [2.2 * ratio, 1.3 * ratio]
#plt.rcParams['figure.figsize'] = [2.8 * ratio, 1.5 * ratio]
fig = plt.figure()
canvas = FigureCanvas(fig)

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

# Histogram plot updater
plt_gradient = rgb_gradient[::-1]
plt_gradient.extend(rgb_gradient[1:])
for idx,color in enumerate(plt_gradient.copy()):
    plt_gradient[idx] = tuple([x/255 for x in color])

def custom_hist(data, bins, color_scheme=None, **kwargs):
    # Create the histogram normally
    fig.clear()
    counts, bin_edges, patches = plt.hist(data, bins=bins, **kwargs)
    
    # Apply the color scheme if provided
    if color_scheme is not None:
        # Check if the color list is long enough
        if len(color_scheme) < len(patches):
            raise ValueError("Color scheme list has fewer elements than the number of bins")
        for patch, color in zip(patches, color_scheme):
            patch.set_facecolor(color)

def update_prob_plot(del_balls_x):
    """Updates the histogram plot of ball locations."""
    fig.set_size_inches(2.2 * ratio, 1.3 * ratio)
    plt.rcParams['axes.edgecolor'] = 'gray'
    bins = np.arange(0, pin_rows + 2, 1)
    if not pin_rows % 2: plt_gradient_new = plt_gradient[8 - pin_rows//2:]
    else:
        plt_gradient_new = plt_gradient[:8] + plt_gradient[9:]
        plt_gradient_new = plt_gradient_new[8 - pin_rows//2 - 1:]
    custom_hist(del_balls_x, bins, color_scheme=plt_gradient_new, edgecolor=plt_background)
    # Save to a BytesIO object instead of disk
    buf = io.BytesIO()
    canvas.print_png(buf)
    buf.seek(0)
    image = pygame.image.load(buf)
    buf.close()
    return image
hist_image = update_prob_plot(np.random.normal(8, 2.8, 10000))

# Slider settings
bias = 1
sliders = {
    'rows': {'pos': (50 * ratio, 50 * ratio), 'min': 5, 'max': 16, 'value': pin_rows},
    'balls_at_once': {'pos': (50 * ratio, 115 * ratio), 'min': 1, 'max': 50, 'value': balls_at_once},
    'center_bias': {'pos': (50 * ratio, 180 * ratio), 'min': 1, 'max': 20, 'value': bias},
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
                    update_prob_plot(del_balls_x)
                    plot_update = True
                elif key == 'center_bias':
                    global bias
                    bias = value
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

# Button settings
button_y = height // 2 - 50 * ratio
button_rect = pygame.Rect(50 * ratio, button_y, 210 * ratio, 50 * ratio)
button_under_rect = pygame.Rect(50 * ratio, (button_y + 7), 210 * ratio, 50 * ratio)
button_clicked = False

def render_button(button_clicked):
    """Handle button states and actions."""
    mouse = pygame.mouse.get_pos()
    # Only change color on hover; clicking is handled via event loop
    button_text = header1.render("Drop", True, black)
    if button_clicked:
        draw_rounded_rect(screen, button_under_rect, button_color_states[1], 10)
        text_rect = button_text.get_rect(center=(160 * ratio, (button_y + button_rect.height // 2 + 7)))
    else:
        text_rect = button_text.get_rect(center=(160 * ratio, (button_y + button_rect.height // 2)))
        draw_rounded_rect(screen, button_under_rect, button_color_states[2], int(10 * ratio))
        if button_rect.collidepoint(mouse):
            draw_rounded_rect(screen, button_rect, button_color_states[1], int(10 * ratio))
        else:
            draw_rounded_rect(screen, button_rect, button_color_states[0], int(10 * ratio))
    screen.blit(button_text, text_rect)
    return button_rect.collidepoint(mouse)

# Render and keep track of money
START_MONEY = 5000.0
money = START_MONEY
bet = 50.0
pl = 0
pl_idx = 0
pl_x_data = [pl_idx]
pl_y_data = [pl]
input_box = pygame.Rect(50 * ratio, button_y - 1.2*button_rect.height, 210 * ratio, 40 * ratio)
inner_gap = 2 * ratio
inner_input_box = pygame.Rect(50 * ratio + inner_gap, button_y - 1.2*button_rect.height + inner_gap, 210 * ratio - 2 * inner_gap, 40 * ratio - 2 * inner_gap)
text = f'${float(bet):.2f}' 
text_active = False  # State of the input box
started_typing = False
print_error = False
err_surface = header2.render("INVALID", True, red)

def render_text_box():
    global input_box, text, text_active
    text_box_color = white if text_active else gray
    txt_surface = header1.render(text, True, white)
    draw_rounded_rect(screen, input_box, text_box_color, 10 * ratio)
    draw_rounded_rect(screen, inner_input_box, background, (10 - inner_gap) * ratio)
    #pygame.draw.rect(screen, text_box_color, input_box, 2)
    screen.blit(txt_surface, (input_box.x + 8 * ratio, input_box.y + (input_box.height - txt_surface.height)//2))
    txt_surface = header0.render('Bet Amount', True, white)
    screen.blit(txt_surface, (input_box.x, input_box.y + 5 - 36 * ratio))
    

def handle_text_input(event):
    global print_error, bet, text, text_active, started_typing, money
    if event.type == pygame.MOUSEBUTTONDOWN and len(balls) <= 0:
        # If the user clicked on the input_box rect.
        if input_box.collidepoint(event.pos):
            if not text_active:
                started_typing = True
            text_active = not text_active
        else:
            text_active = False
    elif event.type == pygame.KEYDOWN and text_active:
        if event.key == pygame.K_RETURN:
            text_active = False
            try: 
                bet = float(text.replace('$', ''))
                if bet > money: bet = money
                text = f'${bet:.2f}'
                print_error = False
            except ValueError:
                text = f'${bet:.2f}'
                print_error = True
        elif event.key == pygame.K_BACKSPACE:
            text = text[:-1]  # Remove the last character
        else:
            if started_typing:
                text = ''
            if len(text) <= 10:
                text += event.unicode  # Add the character typed
                started_typing = False

def render_money(money):
    if pl == 0: color = white
    elif pl > 0: color = green
    else: color = red
    sign_text = header_money.render(f"$", True, color)
    header_rect = sign_text.get_rect(topleft=(60 * ratio, (button_y + 7) + sign_text.height + button_rect.height//2))
    screen.blit(sign_text, header_rect) 
    money_text = header_money.render(f"{money:.2f}", True, white)
    header_rect = money_text.get_rect(topleft=(60 * ratio + sign_text.width, (button_y + 7) + money_text.height + button_rect.height//2))
    screen.blit(money_text, header_rect)

    '''bet_text = header2.render(f" Bet: ${bet:.2f}", True, white)
    header_rect = bet_text.get_rect(topleft=(60 * ratio, (button_y + 7) + 2.25 * money_text.height + button_rect.height//2))
    screen.blit(bet_text, header_rect) ''' 

def update_P_L_plot(pl_x_data, pl_y_data):
    """Updates the P/L money."""
    fig.clear()
    fig.set_size_inches(2.8 * ratio, 1.5 * ratio)
    pl_y_data = np.array(pl_y_data)
    plt.rcParams['axes.edgecolor'] = plt_background
    plt.plot(pl_x_data, pl_y_data, color='white', linewidth=2, alpha=0)  # Alpha set to 0 to make the line invisible
    # Fill area y < 0 = Red, y > 0 Green
    plt.fill_between(pl_x_data, pl_y_data, 0, where=(pl_y_data >= 0), color=plt_green, alpha=0.3, interpolate=True, linewidth=2, edgecolor=plt_green)
    plt.fill_between(pl_x_data, pl_y_data, 0, where=(pl_y_data <= 0), color=plt_red, alpha=0.3, interpolate=True, linewidth=2, edgecolor=plt_red)
    plt.axhline(0, color='gray', linewidth=2)
    # Save to a BytesIO object instead of disk
    buf = io.BytesIO()
    canvas.print_png(buf)
    buf.seek(0)
    image = pygame.image.load(buf)
    buf.close()
    return image
line_image = update_P_L_plot(list(range(0,200)), 15 + np.cumsum(np.random.normal(loc=0.01, scale=5, size=200)))

# Complete board reset
def reset_board():
    global pin_rows, balls_at_once, ball_radius, balls, hit_bins, del_balls_x, hist_image, money, pl, pl_idx, pl_x_data, pl_y_data, bet, line_image, text
    pin_rows = 16
    money = START_MONEY
    bet = 50.0
    text = f'${bet:.2f}'
    pl = 0
    pl_idx = 0
    pl_x_data = [pl_idx]
    pl_y_data = [pl]
    create_pins()
    balls_at_once = 1
    ball_radius = int(9 * ratio)
    balls.clear()
    hit_bins.clear()
    del_balls_x.clear()
    hist_image = update_prob_plot(np.random.normal(8, 2.8, 10000))
    line_image = update_P_L_plot(list(range(0,200)), 15 + np.cumsum(np.random.normal(loc=0.01, scale=5, size=200)))
    reset_sliders()

# Game loop
running = True
while running:
    # Fill the screen with the background color
    screen.fill(background)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if render_button(button_clicked) and not button_clicked:
                button_clicked = True
                for idx in range(balls_at_once):
                    if money - bet < 0: 
                        error_sound.play()
                        break
                    # Drop a ball between the top pins
                    start_x = random.randint(width // 2 - pin_spacing + pin_radius, width // 2 + pin_spacing - pin_radius)
                    balls.append([start_x, random.randint(-2*ball_radius,-ball_radius), 0, 0])  # [x_position, y_position, x_speed, y_speed]
                    money -= bet
                click_sound.play()
        elif event.type == pygame.MOUSEBUTTONUP:
            button_clicked = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                for idx in range(balls_at_once):
                    if money - bet < 0: 
                        error_sound.play()
                        break
                    # Drop a ball between the top pins
                    start_x = random.randint(width // 2 - pin_spacing + pin_radius, width // 2 + pin_spacing - pin_radius)
                    balls.append([start_x, random.randint(-2*ball_radius,-ball_radius), 0, 0])  # [x_position, y_position, x_speed, y_speed]
                    money -= bet
                click_sound.play()
            elif event.key == pygame.K_r:
                reset_board()
        handle_sliders(event)
        handle_text_input(event)
    frame_counter += 1

    # Render catch bins and display recent hit bins
    render_bins()
    display_last_bins(recent_bins, recent_bin_colors)

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
                # Animation
                pygame.draw.circle(screen, opaque_white, (int(pin_x), int(pin_y)), pin_radius*1.5)
                
                # Calulate ball trajectory
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
                random_factor = 0.5  # Random damping factor

                # Apply randomness and dampening
                ball[2], ball[3] = reflected_velocity * random_factor
                ball[2] *= 0.5 # more bouce in the y

                # After calculating the reflected velocity
                if ball[0] > width / 2 + pin_spacing:
                    ball[2] -= bias / 20  # Push left if on the right side
                elif ball[0] < width / 2 - pin_spacing:
                    ball[2] += bias /20  # Push right if on the left side

                # bias ball toward center
                bias_list = [-1, 1]
                direction_change = random.choice(bias_list)                 
                ball[0] += direction_change

        # Remove the ball at the bottom
        if ball[1] > (pin_rows+0.5) * pin_spacing + pin_start:
            ball[1] = height - ball_radius
            bin = int(((ball[0] - (width // 2) + (not pin_rows%2) * pin_spacing//2) + (pin_spacing * ((pin_rows + 1) // 2))) // pin_spacing)
            del_balls_x.append(bin)
            hit_bins.append(bin)
            balls.remove(ball)
            pl_x_data.append(pl_idx)
            plot_update = True
            score_sound.play()
            if bin < len(bin_texts) and bin >= 0:
                index = bin + 8 - pin_rows//2
                if pin_rows % 2 and bin <= pin_rows//2: index -= 1
                texts = bin_texts
                if pin_rows < 10: texts = low_bin_texts
                recent_bins.append(texts[index])
                recent_bins = recent_bins[-4:]
                recent_bin_colors.append(rgb_gradient[index])
                recent_bin_colors = recent_bin_colors[-4:]
                return_money = bet * float(texts[index].replace('x',''))
                money += return_money
                pl_idx += 1
                pl = pl_y_data[-1] + return_money - bet
                pl_y_data.append(pl)

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
        draw_rounded_rect(screen, slider['rect'], gray, 2 * ratio)
        slider['handle'].x = slider['pos'][0] + int((slider['value'] - sliders[key]['min']) / (sliders[key]['max'] - sliders[key]['min']) * 200 * ratio)
        draw_rounded_rect(screen, slider['handle'], white, 2 * ratio)

    # Render the button
    render_button(button_clicked)

    # Display Plot
    if hist_image and line_image:
        screen.blit(hist_image, (width - hist_image.width - 20 * ratio, 40 + line_image.height))
        screen.blit(line_image, (width - line_image.width - 20 * ratio, 20))
        if frame_counter >= 30 and plot_update:
            hist_image = update_prob_plot(del_balls_x) # slow function
            line_image = update_P_L_plot(pl_x_data, pl_y_data) # slow function
            frame_counter = 0
            plot_update = False

    render_money(money)
    render_text_box()

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)
