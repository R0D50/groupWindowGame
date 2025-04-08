import tkinter as tk
from PIL import Image, ImageTk
import pymunk

# Constants
WIDTH = 250
HEIGHT = 100
MARGIN = 0
FLOAT_ABOVE_BOTTOM = 25

# Main window dimensions (dynamic based on screen size)
window = tk.Tk()
SCREEN_WIDTH = window.winfo_screenwidth()
SCREEN_HEIGHT = window.winfo_screenheight()

# Main window setup
window.title("Wooden Block")
window.geometry(f"{WIDTH}x{HEIGHT}")
window.resizable(False, False)

# List to store all windows and their physics info
open_windows = []

# Load image once
image_path = "C:/Users/roder/OneDrive/Desktop/Code/Screenshot 2025-03-31 091325.png"
try:
    image = Image.open(image_path)
    photo_image = ImageTk.PhotoImage(image)
except Exception as e:
    print(f"Error loading image: {e}")
    photo_image = None

# Function to spawn a new window
def open_new_window(event=None):
    spawn_x = len(open_windows) * (WIDTH + MARGIN) % SCREEN_WIDTH
    spawn_y = 50  # Start near the top of the screen

    new_window = tk.Toplevel()
    new_window.title("Wooden Block")
    new_window.geometry(f"{WIDTH}x{HEIGHT}+{spawn_x}+{spawn_y}")
    new_window.resizable(False, False)

    if photo_image:
        label = tk.Label(new_window, image=photo_image)
        label.pack()
        new_window.photo_image = photo_image

    # Add the new window to the list with its physics properties
    open_windows.append({
        'window': new_window,
        'x': spawn_x,
        'y': spawn_y,
        'velocity': 0,
        'falling': True
    })

    # Bind events for dragging windows
    new_window.bind("<ButtonPress-1>", lambda e, w=new_window: on_window_press(e, w))
    new_window.bind("<B1-Motion>", lambda e, w=new_window: on_window_drag(e, w))
    new_window.bind("<ButtonRelease-1>", lambda e, w=new_window: on_window_release(e, w))

# Event handlers for dragging windows
def on_window_press(event, window):
    window.initial_x = window.winfo_x()
    window.initial_y = window.winfo_y()
    window.drag_data = {'x': event.x, 'y': event.y}

def on_window_drag(event, window):
    delta_x = event.x - window.drag_data['x']
    delta_y = event.y - window.drag_data['y']
    new_x = max(0, min(SCREEN_WIDTH - WIDTH, window.initial_x + delta_x))
    new_y = max(0, min(SCREEN_HEIGHT - HEIGHT, window.initial_y + delta_y))
    window.geometry(f"{WIDTH}x{HEIGHT}+{new_x}+{new_y}")

def on_window_release(event, window):
    for block in open_windows:
        if block['window'] == window:
            block['falling'] = True  # Enable gravity after releasing the block
            break

# Function to apply gravity to all windows
def apply_gravity():
    for block in open_windows:
        win = block['window']
        x = block['x']
        y = block['y']
        velocity = block['velocity']

        bottom_y = SCREEN_HEIGHT - HEIGHT - FLOAT_ABOVE_BOTTOM
        touching_block = False

        # Check for collision with other blocks
        for other in open_windows:
            if other == block:
                continue
            ox = other['x']
            oy = other['y']
            if (abs((x + WIDTH / 2) - (ox + WIDTH / 2)) < WIDTH and
                y + HEIGHT + velocity >= oy and
                y < oy):
                touching_block = True
                y = oy - HEIGHT
                velocity = 0
                block['falling'] = False
                break

        # Apply gravity if not touching anything and not at the bottom of the screen
        if not touching_block and y < bottom_y:
            block['falling'] = True
            velocity += 2  # Gravity acceleration (pixels per frame)
            y += velocity

            # Stop falling if it reaches the bottom of the screen
            if y > bottom_y:
                y = bottom_y
                velocity = 0
                block['falling'] = False

        # Update block's position and velocity
        block['x'] = x
        block['y'] = y
        block['velocity'] = velocity

        win.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

    # Schedule the next frame of gravity application
    window.after(30, apply_gravity)

# Main window image (optional)
if photo_image:
    image_label = tk.Label(window, image=photo_image)
    image_label.pack()
window.photo_image = photo_image

# Instructions label and key binding to spawn blocks
tk.Label(window, text="Press 'n' to open a new falling block").pack()
window.bind('n', open_new_window)

# Start gravity simulation and main loop
apply_gravity()
window.mainloop()