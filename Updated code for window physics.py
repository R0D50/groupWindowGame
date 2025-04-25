import tkinter as tk
from PIL import Image, ImageTk

# Constants
WIDTH = 250
HEIGHT = 100
MARGIN = 0
FLOAT_ABOVE_BOTTOM = 25
SHOP_POINTS = 0
SHOP_WIDTH = 400
SHOP_HEIGHT = 200

# Temporary root to get screen dimensions, then destroy
_temp_root = tk.Tk()
SCREEN_WIDTH = _temp_root.winfo_screenwidth()
SCREEN_HEIGHT = _temp_root.winfo_screenheight()
_temp_root.destroy()

# List to store all windows and their physics info
open_windows = []

# Load image paths
image_path_block = "C:\\Users\\markm\\OneDrive\\Desktop\\Screenshot 2025-03-31 091325.png"
image_path_ball = "C:\\Users\\markm\\OneDrive\\Desktop\\download-removebg-preview.png"

# Function to spawn a new wooden block window
def open_new_window(event=None):
    spawn_x = len(open_windows) * (WIDTH + MARGIN) % SCREEN_WIDTH
    spawn_y = 50
    try:
        image = Image.open(image_path_block)
        photo_image = ImageTk.PhotoImage(image)
        img_width, img_height = image.size
    except Exception as e:
        print(f"Error loading image: {e}")
        photo_image = None
        img_width, img_height = WIDTH, HEIGHT

    new_window = tk.Toplevel()
    new_window.title("Wooden Block")
    new_window.geometry(f"{img_width}x{img_height}+{spawn_x}+{spawn_y}")
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
        'bouncy': False,
        'width': img_width,
        'height': img_height
    })

    new_window.bind("<ButtonPress-1>", lambda e, w=new_window: on_window_press(e, w))
    new_window.bind("<B1-Motion>", lambda e, w=new_window: on_window_drag(e, w))
    new_window.bind("<ButtonRelease-1>", lambda e, w=new_window: on_window_release(e, w))

# Function to spawn a resized bouncy ball window
def open_bouncy_ball_window(event=None):
    spawn_x = len(open_windows) * (WIDTH + MARGIN) % SCREEN_WIDTH
    spawn_y = 50
    try:
        image = Image.open(image_path_ball)

        # Resize the image to be smaller (e.g., 50% of original size)
        scale_factor = 0.5
        img_width, img_height = image.size
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        
        # Use LANCZOS resampling (which is the best quality resampling)
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(resized_image)

    except Exception as e:
        print(f"Error loading image: {e}")
        photo_image = None
        new_width, new_height = WIDTH, HEIGHT  # fallback

    new_window = tk.Toplevel()
    new_window.title("Bouncy Ball")
    new_window.geometry(f"{new_width}x{new_height}+{spawn_x}+{spawn_y}")
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
        'bouncy': True,
        'width': new_width,
        'height': new_height
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
        width = block.get('width', WIDTH)
        height = block.get('height', HEIGHT)

        bottom_y = SCREEN_HEIGHT - height - FLOAT_ABOVE_BOTTOM
        touching_block = False

        for other in open_windows:
            if other == block:
                continue
            ox = other['x']
            oy = other['y']
            o_width = other.get('width', WIDTH)
            o_height = other.get('height', HEIGHT)

            # Adjust collision detection to account for the updated size of the bouncy ball
            if (abs((x + width / 2) - (ox + o_width / 2)) < width and
                y + height + velocity >= oy and
                y < oy):
                touching_block = True
                y = oy - height
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

        win.geometry(f"{width}x{height}+{x}+{y}")

    shop_window.after(50, apply_gravity)

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

# Create the shop window (main window)
shop_window = tk.Tk()
shop_window.title(f"Window Shop: Your Points = {SHOP_POINTS}")
shop_window.geometry(f"{SHOP_WIDTH}x{SHOP_HEIGHT}")
shop = ShopGUI(shop_window)

# Start the gravity simulation
apply_gravity()

# Main loop (only for the shop window now)
shop_window.mainloop()
