import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path

# Constants
WIDTH = 250
HEIGHT = 100
MARGIN = 0
FLOAT_ABOVE_BOTTOM = 25
SHOP_POINTS = 0
SHOP_WIDTH = 400
SHOP_HEIGHT = 200

_temp_root = tk.Tk()
SCREEN_WIDTH = _temp_root.winfo_screenwidth()
SCREEN_HEIGHT = _temp_root.winfo_screenheight()
_temp_root.destroy()

open_windows = []

# Relative pathing setup
root_dir = Path(__file__).resolve().parent
image_path_block = root_dir / "Window_Images" / "WB.png"
image_path_ball = root_dir / "Window_Images" / "BB.png"
image_path_block_shop = root_dir / "Shop_Images" / "WBs.png"

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
        'vx': 0,
        'vy': 0,
        'falling': True,
        'bouncy': False,
        'width': img_width,
        'height': img_height,
        'support': None
    })

    new_window.bind("<ButtonPress-1>", lambda e, w=new_window: on_window_press(e, w))
    new_window.bind("<B1-Motion>", lambda e, w=new_window: on_window_drag(e, w))
    new_window.bind("<ButtonRelease-1>", lambda e, w=new_window: on_window_release(e, w))

def open_bouncy_ball_window(event=None):
    spawn_x = len(open_windows) * (WIDTH + MARGIN) % SCREEN_WIDTH
    spawn_y = 50
    try:
        image = Image.open(image_path_ball)
        scale_factor = 0.5
        img_width, img_height = image.size
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(resized_image)
    except Exception as e:
        print(f"Error loading image: {e}")
        photo_image = None
        new_width, new_height = WIDTH, HEIGHT

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
        'vx': 0,
        'vy': 0,
        'falling': True,
        'bouncy': True,
        'width': new_width,
        'height': new_height,
        'support': None
    })

    new_window.bind("<ButtonPress-1>", lambda e, w=new_window: on_window_press(e, w))
    new_window.bind("<B1-Motion>", lambda e, w=new_window: on_window_drag(e, w))
    new_window.bind("<ButtonRelease-1>", lambda e, w=new_window: on_window_release(e, w))

class ShopGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg='white')
        self.setupShop()

    def setupShop(self):
        # Configure the grid layout
        for row in range(6):
            tk.Grid.rowconfigure(self, row, weight=1)
        for col in range(5):
            tk.Grid.columnconfigure(self, col, weight=1)

        # Load and keep a reference to the images to prevent garbage collection
        self.block_image = Image.open(image_path_block_shop)

        # Convert images to Tkinter compatible format
        self.block_shop_img = ImageTk.PhotoImage(self.block_image)

        # Add buttons with images
        block_button = tk.Button(self, text="Wooden Block", image=self.block_shop_img, compound="left", borderwidth=1, command=open_new_window)
        block_button.grid(row=1, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

        self.pack(expand=1)

shop_window = tk.Tk()
shop_window.title(f"Window Shop: Your Points = {SHOP_POINTS}")
shop_window.geometry(f"{SHOP_WIDTH}x{SHOP_HEIGHT}")
shop = ShopGUI(shop_window)

shop_window.mainloop()
