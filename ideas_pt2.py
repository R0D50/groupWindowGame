import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path

# Constants
WIDTH = 250
HEIGHT = 100
MARGIN = 0
FLOAT_ABOVE_BOTTOM = 25
SHOP_POINTS = 100
SHOP_WIDTH = 400
SHOP_HEIGHT = 200

ITEM_PRICES = {
    "Wooden Block": 10,
    "Bouncy Ball": 20,
    "Ice Cube": 15
}

_temp_root = tk.Tk()
SCREEN_WIDTH = _temp_root.winfo_screenwidth()
SCREEN_HEIGHT = _temp_root.winfo_screenheight()
_temp_root.destroy()

open_windows = []
root_dir = Path(__file__).resolve().parent

# Image Paths
image_path_block = root_dir / "Window_Images" / "WB.png"
image_path_ball = root_dir / "Window_Images" / "BB.png"
image_path_ice = root_dir / "Window_Images" / "IC.png"

image_path_block_shop = root_dir / "Shop_Images" / "WBs.png"
image_path_ball_shop = root_dir / "Shop_Images" / "BBs.png"
image_path_ice_shop = root_dir / "Shop_Images" / "ICs.png"
image_path_background_shop = root_dir / "Shop_Images" / "Shop_bg.png"

def load_image(path, scale=1.0):
    try:
        image = Image.open(path)
        if scale != 1.0:
            w, h = image.size
            image = image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image), image.size
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return None, (WIDTH, HEIGHT)

def create_window(title, image_path, is_bouncy=False, is_slippery=False, scale=1.0):
    global SHOP_POINTS
    spawn_x = len(open_windows) * (WIDTH + MARGIN) % SCREEN_WIDTH
    spawn_y = 50
    photo_image, (img_width, img_height) = load_image(image_path, scale)

    new_window = tk.Toplevel()
    new_window.title(title)
    new_window.geometry(f"{img_width}x{img_height}+{spawn_x}+{spawn_y}")
    new_window.resizable(False, False)

    if photo_image:
        label = tk.Label(new_window, image=photo_image)
        label.pack()
        new_window.photo_image = photo_image

    block = {
        'window': new_window,
        'x': spawn_x,
        'y': spawn_y,
        'vx': 0,
        'vy': 0,
        'falling': True,
        'bouncy': is_bouncy,
        'slippery': is_slippery,
        'width': img_width,
        'height': img_height,
        'support': None,
        'type': title,
        'grounded': False
    }

    open_windows.append(block)
    new_window.protocol("WM_DELETE_WINDOW", lambda w=new_window: close_window(w))
    new_window.bind("<ButtonPress-1>", lambda e, w=new_window: on_window_press(e, w))
    new_window.bind("<B1-Motion>", lambda e, w=new_window: on_window_drag(e, w))
    new_window.bind("<ButtonRelease-1>", lambda e, w=new_window: on_window_release(e, w))

    if title == "Ice Cube":
        start_melting(block)

def close_window(window):
    global open_windows
    open_windows = [block for block in open_windows if block['window'] != window]
    window.destroy()

def try_purchase(item_name, creation_func):
    global SHOP_POINTS
    cost = ITEM_PRICES[item_name]
    if SHOP_POINTS >= cost:
        SHOP_POINTS -= cost
        creation_func()
        update_shop_ui()

def open_wood_window(event=None):
    try_purchase("Wooden Block", lambda: create_window("Wooden Block", image_path_block))

def open_ball_window(event=None):
    try_purchase("Bouncy Ball", lambda: create_window("Bouncy Ball", image_path_ball, is_bouncy=True, scale=0.5))

def open_ice_window(event=None):
    try_purchase("Ice Cube", lambda: create_window("Ice Cube", image_path_ice, is_slippery=True, scale=0.5))

def apply_physics():
    global SHOP_POINTS
    for block in open_windows[:]:
        win = block['window']
        x, y = block['x'], block['y']
        vx, vy = block['vx'], block['vy']
        width, height = block['width'], block['height']
        is_bouncy, is_slippery = block['bouncy'], block['slippery']

        vy += 1.5  # Gravity
        x += vx
        y += vy
        block['support'] = None
        grounded = False
        friction = 0.7

        # Check for collisions with other blocks
        for other in open_windows:
            if other == block:
                continue
            ox, oy = other['x'], other['y']
            ow, oh = other['width'], other['height']

            overlap_x = (x < ox + ow) and (x + width > ox)
            overlap_y = (y + height > oy) and (y < oy + oh)

            if overlap_x and overlap_y:
                if vy > 0 and y + height - vy <= oy:
                    y = oy - height
                    if is_bouncy and abs(vy) > 3:
                        vy = -vy * 0.6  # Bounce vertically
                        if block['type'] == "Ice Cube":  # Points for Ice Cube bounce
                            SHOP_POINTS += 10
                            update_shop_ui()
                    else:
                        vy = 0
                    grounded = True
                    block['support'] = other
                    friction = 0.98 if other['slippery'] else 0.7
                    if not block['grounded'] and block['type'] != "Ice Cube":
                        SHOP_POINTS += 5
                        update_shop_ui()

                # Handle horizontal collision
                if vx > 0:  # Colliding with left side of the other object
                    x = ox - width
                    if block['type'] == "Ice Cube":
                        vx = -vx * 1.1  # Ice cube bounces with more velocity
                        SHOP_POINTS += 10  # Points for bounce off other objects
                        update_shop_ui()
                    else:
                        vx = 0  # Regular object stops at the wall
                elif vx < 0:  # Colliding with right side of the other object
                    x = ox + ow
                    if block['type'] == "Ice Cube":
                        vx = -vx * 1.1  # Ice cube bounces with more velocity
                        SHOP_POINTS += 10  # Points for bounce off other objects
                        update_shop_ui()
                    else:
                        vx = 0  # Regular object stops at the wall

        # Screen bottom boundary check
        if y + height >= SCREEN_HEIGHT - FLOAT_ABOVE_BOTTOM:
            y = SCREEN_HEIGHT - FLOAT_ABOVE_BOTTOM - height
            if is_bouncy and abs(vy) > 3:
                vy = -vy * 0.6  # Bounce vertically
            else:
                vy = 0
                grounded = True
                friction = 0.7
            if not block['grounded'] and block['type'] != "Ice Cube":
                SHOP_POINTS += 5
                update_shop_ui()

        # Wall collision: Bounce or stop movement for objects hitting the walls
        if x <= 0:  # Left wall
            x = 0
            if block['type'] == "Ice Cube":
                vx = -vx * 1.1  # Ice cubes bounce with more velocity
                SHOP_POINTS += 10  # Points for bounce off wall
                update_shop_ui()
            else:
                vx = 0  # Regular objects stop at the wall
        elif x + width >= SCREEN_WIDTH:  # Right wall
            x = SCREEN_WIDTH - width
            if block['type'] == "Ice Cube":
                vx = -vx * 1.1  # Ice cubes bounce with more velocity
                SHOP_POINTS += 10  # Points for bounce off wall
                update_shop_ui()
            else:
                vx = 0  # Regular objects stop at the wall

        # Apply a bit less friction to ice cubes (slower slowdown)
        if block['type'] == "Ice Cube" and grounded:
            vx *= 0.97  # Less friction for ice cubes to slow down more slowly

        # Apply friction for non-ice objects (objects on the ground)
        if grounded and not is_slippery and block['type'] != "Ice Cube":
            vx *= friction  # Friction slows down the object

        # Update block state
        block.update({'x': x, 'y': y, 'vx': vx, 'vy': vy})
        win.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

        # Mark as grounded
        block['grounded'] = grounded

    shop_window.after(30, apply_physics)

def start_melting(block):
    def melt():
        if block not in open_windows:
            return
        window = block['window']
        w, h = block['width'], block['height']
        if w <= 10 or h <= 10:
            open_windows.remove(block)
            window.destroy()
            return

        block['width'] = int(w * 0.98)
        block['height'] = int(h * 0.98)
        block['x'] = min(max(0, block['x']), SCREEN_WIDTH - block['width'])
        block['y'] = min(max(0, block['y']), SCREEN_HEIGHT - block['height'] - FLOAT_ABOVE_BOTTOM)
        window.geometry(f"{block['width']}x{block['height']}+{int(block['x'])}+{int(block['y'])}")
        window.after(300, melt)

    melt()

def on_window_press(event, window):
    window.drag_data = {'x': event.x, 'y': event.y}
    window.last_mouse_x = event.x_root
    window.last_mouse_y = event.y_root

def on_window_drag(event, window):
    x = window.winfo_x() + event.x - window.drag_data['x']
    y = window.winfo_y() + event.y - window.drag_data['y']
    dx = event.x_root - window.last_mouse_x
    dy = event.y_root - window.last_mouse_y
    window.geometry(f"+{x}+{y}")

    for block in open_windows:
        if block['window'] == window:
            block['x'], block['y'] = x, y
            block['vx'], block['vy'] = dx, dy
            for other in open_windows:
                if other.get('support') == block:
                    other['x'] += dx
                    other['y'] += dy
                    other['vx'], other['vy'] = dx, dy
                    other['window'].geometry(
                        f"{other['width']}x{other['height']}+{int(other['x'])}+{int(other['y'])}"
                    )
            break

    window.last_mouse_x = event.x_root
    window.last_mouse_y = event.y_root

def on_window_release(event, window):
    for block in open_windows:
        if block['window'] == window:
            block['x'] = window.winfo_x()
            block['y'] = window.winfo_y()
            block['vx'] = max(-30, min(block['vx'], 30))
            block['vy'] = max(-30, min(block['vy'], 30))
            block['falling'] = True
            break

def update_shop_ui():
    shop_window.title(f"Window Shop: Your Points = {SHOP_POINTS}")
    for item, button in shop_buttons.items():
        cost = ITEM_PRICES[item]
        button.config(state=tk.NORMAL if SHOP_POINTS >= cost else tk.DISABLED)

class ShopGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)
        self.bg_image_orig = Image.open(image_path_background_shop)
        self.bg_image_tk = None
        self.bg_image_id = None

        # Load item images
        self.block_shop_img = ImageTk.PhotoImage(Image.open(image_path_block_shop))
        self.ball_shop_img = ImageTk.PhotoImage(Image.open(image_path_ball_shop))
        self.ice_shop_img = ImageTk.PhotoImage(Image.open(image_path_ice_shop))

        # Create buttons
        shop_buttons["Wooden Block"] = tk.Button(self, text="Wooden Block ($10)", image=self.block_shop_img, compound="bottom", command=open_wood_window)
        shop_buttons["Bouncy Ball"] = tk.Button(self, text="Bouncy Ball ($20)", image=self.ball_shop_img, compound="bottom", command=open_ball_window)
        shop_buttons["Ice Cube"] = tk.Button(self, text="Ice Cube ($15)", image=self.ice_shop_img, compound="bottom", command=open_ice_window)

        # Place buttons
        self.canvas.create_window(10, 10, anchor="nw", window=shop_buttons["Wooden Block"])
        self.canvas.create_window(140, 10, anchor="nw", window=shop_buttons["Bouncy Ball"])
        self.canvas.create_window(270, 10, anchor="nw", window=shop_buttons["Ice Cube"])

        self.pack(fill="both", expand=True)
        self.master.bind("<Configure>", self.on_resize)
        self.on_resize()

    def on_resize(self, event=None):
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        resized = self.bg_image_orig.resize((width, height), Image.Resampling.LANCZOS)
        self.bg_image_tk = ImageTk.PhotoImage(resized)
        if self.bg_image_id:
            self.canvas.delete(self.bg_image_id)
        self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw")
        self.canvas.tag_lower(self.bg_image_id)

# Run the application
if __name__ == "__main__":
    shop_buttons = {}
    shop_window = tk.Tk()
    shop_window.title(f"Window Shop: Your Points = {SHOP_POINTS}")
    shop_window.geometry(f"{SHOP_WIDTH}x{SHOP_HEIGHT}")
    ShopGUI(shop_window)
    update_shop_ui()
    apply_physics()
    shop_window.mainloop()
