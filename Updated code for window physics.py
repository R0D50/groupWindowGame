import tkinter as tk
from PIL import Image, ImageTk
import threading
import time

# Constants
WIDTH = 250
HEIGHT = 100
MARGIN = 0
FLOAT_ABOVE_BOTTOM = 25
SHOP_POINTS = 0
SHOP_WIDTH = 400
SHOP_HEIGHT = 200

# Main window dimensions (dynamic based on screen size)
window = tk.Tk()
SCREEN_WIDTH = window.winfo_screenwidth()
SCREEN_HEIGHT = window.winfo_screenheight()

# Main window setup
window.title("Wooden Block")
window.geometry(f"{WIDTH}x{HEIGHT}")
window.resizable(True, True)

# List to store all windows and their physics info
open_windows = []

# Load image once
image_path_block = "C:\\Users\\markm\\OneDrive\\Desktop\\Screenshot 2025-03-31 091325.png"
image_path_ball = "C:\\Users\\markm\\OneDrive\\Desktop\\download-removebg-preview.png"


# Function to spawn a new wooden block window
def open_new_window(event=None):
    spawn_x = len(open_windows) * (WIDTH + MARGIN) % SCREEN_WIDTH
    spawn_y = 50
    try:
        image = Image.open(image_path_block)
        photo_image = ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error loading image: {e}")
        photo_image = None

    new_window = tk.Toplevel()
    new_window.title("Wooden Block")
    new_window.geometry(f"{WIDTH}x{HEIGHT}+{spawn_x}+{spawn_y}")
    new_window.resizable(False, False)

    if photo_image:
        label = tk.Label(new_window, image=photo_image)
        label.pack()
        new_window.photo_image = photo_image

    open_windows.append({
        'window': new_window,
        'x': spawn_x,
        'y': spawn_y,
        'velocity': 0,
        'falling': True,
        'bouncy': False
    })

    new_window.bind("<ButtonPress-1>", lambda e, w=new_window: on_window_press(e, w))
    new_window.bind("<B1-Motion>", lambda e, w=new_window: on_window_drag(e, w))
    new_window.bind("<ButtonRelease-1>", lambda e, w=new_window: on_window_release(e, w))

# Function to spawn a bouncy ball window
def open_bouncy_ball_window(event=None):
    spawn_x = len(open_windows) * (WIDTH + MARGIN) % SCREEN_WIDTH
    spawn_y = 50
    try:
        image = Image.open(image_path_ball)
        photo_image = ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error loading image: {e}")
        photo_image = None
    new_window = tk.Toplevel()
    new_window.title("Bouncy Ball")
    new_window.geometry(f"{WIDTH}x{HEIGHT}+{spawn_x}+{spawn_y}")
    new_window.resizable(False, False)

    if photo_image:
        label = tk.Label(new_window, image=photo_image)
        label.pack()
        new_window.photo_image = photo_image

    open_windows.append({
        'window': new_window,
        'x': spawn_x,
        'y': spawn_y,
        'velocity': 0,
        'falling': True,
        'bouncy': True
    })

    new_window.bind("<ButtonPress-1>", lambda e, w=new_window: on_window_press(e, w))
    new_window.bind("<B1-Motion>", lambda e, w=new_window: on_window_drag(e, w))
    new_window.bind("<ButtonRelease-1>", lambda e, w=new_window: on_window_release(e, w))

# Apply gravity and handle collisions
def apply_gravity():
    for block in open_windows:
        if not block['falling']:
            continue

        win = block['window']
        x = block['x']
        y = block['y']
        velocity = block['velocity']

        bottom_y = SCREEN_HEIGHT - HEIGHT - FLOAT_ABOVE_BOTTOM
        touching_block = False

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
                if block.get('bouncy'):
                    velocity = -int(velocity * 0.6)
                    if abs(velocity) < 2:
                        velocity = 0
                        block['falling'] = False
                    else:
                        block['falling'] = True
                else:
                    velocity = 0
                    block['falling'] = False
                break

        if not touching_block and y < bottom_y:
            block['falling'] = True
            velocity += 2
            y += velocity

            if y >= bottom_y:
                y = bottom_y
                if block.get('bouncy'):
                    velocity = -int(velocity * 0.6)
                    if abs(velocity) < 2:
                        velocity = 0
                        block['falling'] = False
                    else:
                        block['falling'] = True
                        y += velocity  # Bounce up immediately
                else:
                    velocity = 0
                    block['falling'] = False

        block['x'] = x
        block['y'] = y
        block['velocity'] = velocity

        win.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

    window.after(50, apply_gravity)

# Drag event handlers
def on_window_press(event, window):
    window.drag_data = {'x': event.x, 'y': event.y}

def on_window_drag(event, window):
    x = window.winfo_x() + event.x - window.drag_data['x']
    y = window.winfo_y() + event.y - window.drag_data['y']
    window.geometry(f"+{x}+{y}")

    for block in open_windows:
        if block['window'] == window:
            block['x'] = x
            block['y'] = y
            block['falling'] = False
            break

def on_window_release(event, window):
    for block in open_windows:
        if block['window'] == window:
            block['x'] = window.winfo_x()
            block['y'] = window.winfo_y()
            window.after(100, lambda: setFalling(block))
            break

def setFalling(block):
    block['falling'] = True

'''# Main image (optional)
if photo_image:
    image_label = tk.Label(window, image=photo_image)
    image_label.pack()
window.photo_image = photo_image'''

# Shop GUI class
class ShopGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg='white')
        self.setupShop()

    def setupShop(self):
        for row in range(6):
            tk.Grid.rowconfigure(self, row, weight=1)
        for col in range(5):
            tk.Grid.columnconfigure(self, col, weight=1)

        # Wooden Block Button
        block_button = tk.Button(self, bg='white', text="Wooden Block",
            borderwidth=1, highlightthickness=0, activebackground='white', command=open_new_window)
        block_button.grid(row=1, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

        # Bouncy Ball Button
        ball_button = tk.Button(self, bg='white', text="Bouncy Ball",
            borderwidth=1, highlightthickness=0, activebackground='white', command=open_bouncy_ball_window)
        ball_button.grid(row=1, column=1, sticky=tk.E + tk.W + tk.N + tk.S)

        self.pack(expand=1)

# Create the shop window
shop_window = tk.Tk()
shop_window.title(f"Window Shop: Your Points = {SHOP_POINTS}")
shop_window.geometry(f"{SHOP_WIDTH}x{SHOP_HEIGHT}")
shop = ShopGUI(shop_window)

# Start the gravity simulation
apply_gravity()
window.mainloop()
