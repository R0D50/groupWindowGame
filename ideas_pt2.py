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

    new_window.bind("<ButtonPress-1>", lambda e, w=new_window: on_window_press(e, w))
    new_window.bind("<B1-Motion>", lambda e, w=new_window: on_window_drag(e, w))
    new_window.bind("<ButtonRelease-1>", lambda e, w=new_window: on_window_release(e, w))

    if title == "Ice Cube":
        start_melting(block)

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

        vy += 1.5  # Gravity effect
        x += vx
        y += vy

        block['support'] = None
        grounded = False
        friction = 0.7  # Default friction

        # Handle object-to-object collisions
        for other in open_windows:
            if other == block:
                continue
            ox, oy = other['x'], other['y']
            ow, oh = other['width'], other['height']

            if (x < ox + ow and x + width > ox and
                y + height > oy and y < oy + oh):
                if vy > 0 and y < oy:
                    y = oy - height
                    if is_bouncy and abs(vy) > 3:
                        vy = -vy * 0.6  # Bounce effect
                    else:
                        vy = 0
                    block['support'] = other
                    grounded = True
                    friction = 0.98 if other['slippery'] else 0.7
                    if not block['grounded'] and block['type'] != "Ice Cube":
                        SHOP_POINTS += 5
                        update_shop_ui()
                elif vx > 0:
                    vx = -vx * 0.6 if is_bouncy else 0
                elif vx < 0:
                    vx = -vx * 0.6 if is_bouncy else 0
                break

        # Boundary collisions (confining to the 1920x1080 screen)
        ground_y = SCREEN_HEIGHT - height - FLOAT_ABOVE_BOTTOM
        right_x = SCREEN_WIDTH - width
        left_x = 0
        top_y = 0

        if y >= ground_y:
            y = ground_y
            if is_bouncy and abs(vy) > 3:
                vy = -vy * 0.6  # Bounce effect
            else:
                vy = 0
            grounded = True
            friction = 0.95 if is_slippery else 0.7

        if x <= left_x:  # Left boundary
            x = left_x
            if is_bouncy and abs(vx) > 3:
                vx = -vx * 0.6  # Bounce effect
            else:
                vx = 0
        elif x >= right_x:  # Right boundary
            x = right_x
            if is_bouncy and abs(vx) > 3:
                vx = -vx * 0.6  # Bounce effect
            else:
                vx = 0

        if y <= top_y:  # Top boundary (optional, could be removed if no top bound needed)
            y = top_y
            vy = 0  # No bounce on top

        if grounded:
            vx *= friction
            if abs(vx) < 0.1:
                vx = 0

        # Update block position and velocities
        block['grounded'] = grounded
        block.update({'x': x, 'y': y, 'vx': vx, 'vy': vy})
        win.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    # Recursively call the physics function every 30ms
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
        super().__init__(master, bg='white')
        self.setup_shop()

    def setup_shop(self):
        for row in range(6):
            self.rowconfigure(row, weight=1)
        for col in range(5):
            self.columnconfigure(col, weight=1)

        self.block_shop_img = ImageTk.PhotoImage(Image.open(image_path_block_shop))
        self.ball_shop_img = ImageTk.PhotoImage(Image.open(image_path_ball_shop))
        self.ice_shop_img = ImageTk.PhotoImage(Image.open(image_path_ice_shop))

        shop_buttons["Wooden Block"] = tk.Button(self, text="Wooden Block ($10)", image=self.block_shop_img, compound="bottom", command=open_wood_window)
        shop_buttons["Wooden Block"].grid(row=1, column=0, sticky="nsew")

        shop_buttons["Bouncy Ball"] = tk.Button(self, text="Bouncy Ball ($20)", image=self.ball_shop_img, compound="bottom", command=open_ball_window)
        shop_buttons["Bouncy Ball"].grid(row=1, column=1, sticky="nsew")

        shop_buttons["Ice Cube"] = tk.Button(self, text="Ice Cube ($15)", image=self.ice_shop_img, compound="bottom", command=open_ice_window)
        shop_buttons["Ice Cube"].grid(row=1, column=2, sticky="nsew")

        self.pack(expand=1)

if __name__ == "__main__":
    shop_buttons = {}
    shop_window = tk.Tk()
    shop_window.title(f"Window Shop: Your Points = {SHOP_POINTS}")
    shop_window.geometry(f"{SHOP_WIDTH}x{SHOP_HEIGHT}")
    ShopGUI(shop_window)
    update_shop_ui()
    apply_physics()
    shop_window.mainloop()
