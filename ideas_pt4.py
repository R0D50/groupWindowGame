import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
import random

# === Configuration ===
class GameConfig:
    WIDTH = 250
    HEIGHT = 100
    MARGIN = 0
    FLOAT_ABOVE_BOTTOM = 25
    SHOP_POINTS = 100
    SHOP_WIDTH = 400
    SHOP_HEIGHT = 200
    GRAVITY = 1.5
    ITEM_PRICES = {
        "Wooden Block": 10,
        "Bouncy Ball": 20,
        "Ice Cube": 15
    }
    # Define upgrades with cost and unlock behavior
    SHOP_UPGRADES = {
        "Upgrade 1": {"cost": 50, "new_items": ["Wooden Block", "Bouncy Ball"]},
        "Upgrade 2": {"cost": 150, "new_items": ["Ice Cube"]},
        # Add more upgrades here
    }
    PURCHASED_UPGRADES = []  # Track purchased upgrades

# === Screen Setup ===
TEMP_ROOT = tk.Tk()
SCREEN_WIDTH = TEMP_ROOT.winfo_screenwidth()
SCREEN_HEIGHT = TEMP_ROOT.winfo_screenheight()
TEMP_ROOT.destroy()

# === Globals ===
open_windows = []
shop_buttons = {}
shop_window = None
root_dir = Path(__file__).resolve().parent

# === Image Paths ===
image_paths = {
    "Wooden Block": root_dir / "Window_Images" / "WB.png",
    "Bouncy Ball": root_dir / "Window_Images" / "BB.png",
    "Ice Cube": root_dir / "Window_Images" / "IC.png",
    "WBs": root_dir / "Shop_Images" / "WBs.png",
    "BBs": root_dir / "Shop_Images" / "BBs.png",
    "ICs": root_dir / "Shop_Images" / "ICs.png",
    "Shop_bg": root_dir / "Shop_Images" / "Shop_bg.png"
}

# === Utilities ===
def load_image(path, scale=1.0):
    try:
        image = Image.open(path)
        if scale != 1.0:
            w, h = image.size
            image = image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image), image.size
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return None, (GameConfig.WIDTH, GameConfig.HEIGHT)

# === Window Creation ===
def create_window(title, image_path, is_bouncy=False, is_slippery=False, scale=1.0):
    spawn_x = len(open_windows) * (GameConfig.WIDTH + GameConfig.MARGIN) % SCREEN_WIDTH
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
        'type': title,
        'grounded': False,
        'stacked_on': None  # Tracking the block it's stacked on (if any)
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
    open_windows = [b for b in open_windows if b['window'] != window]
    window.destroy()

# === Purchasing and Events ===
def try_purchase(item_name, creation_func):
    cost = GameConfig.ITEM_PRICES[item_name]
    if GameConfig.SHOP_POINTS >= cost:
        GameConfig.SHOP_POINTS -= cost
        creation_func()
        update_shop_ui()

def open_wood_window(event=None):
    try_purchase("Wooden Block", lambda: create_window("Wooden Block", image_paths["Wooden Block"]))

def open_ball_window(event=None):
    try_purchase("Bouncy Ball", lambda: create_window("Bouncy Ball", image_paths["Bouncy Ball"], is_bouncy=True, scale=0.5))

def open_ice_window(event=None):
    try_purchase("Ice Cube", lambda: create_window("Ice Cube", image_paths["Ice Cube"], is_slippery=True, scale=0.5))

# === Physics Engine ===
def apply_physics():
    for block in open_windows[:]:
        x, y = block['x'], block['y']
        vx, vy = block['vx'], block['vy']
        width, height = block['width'], block['height']
        bouncy, slippery = block['bouncy'], block['slippery']
        is_grounded = block['grounded']
        vy += GameConfig.GRAVITY
        x += vx
        y += vy
        grounded = False
        friction = 0.7

        # Handle stacked blocks: Update top block's position based on the bottom block's position
        if block['stacked_on']:
            stack_block = block['stacked_on']
            stack_x, stack_y = stack_block['x'], stack_block['y']
            block['x'] = stack_x
            block['y'] = stack_y - block['height']
            continue  # Skip the rest of the physics for the top block since it's following the bottom block

        # Wall collisions
        if x <= 0 or x + width >= SCREEN_WIDTH:
            x = max(0, min(SCREEN_WIDTH - width, x))
            if bouncy or block['type'] == "Ice Cube":
                vx = -vx * 1.1
                vx *= 0.9
                GameConfig.SHOP_POINTS += 10
                update_shop_ui()
            else:
                vx = 0

        if y <= 0:
            y = 0
            vy = -vy * 0.6 if bouncy else 0

        # Block collisions
        for other in open_windows:
            if other == block: continue
            ox, oy, ow, oh = other['x'], other['y'], other['width'], other['height']
            if (x < ox + ow and x + width > ox and y + height > oy and y < oy + oh):
                if vy > 0 and y + height - vy <= oy:
                    y = oy - height
                    vy = -vy * 0.6 if bouncy and abs(vy) > 3 else 0
                    grounded = True
                    if block['type'] == "Wooden Block" and not (x <= ox or x + width >= ox): 
                        GameConfig.SHOP_POINTS += 10
                        update_shop_ui()

                elif vx > 0:
                    x = ox - width
                    vx = -vx * 1.1 if bouncy or block['type'] == "Ice Cube" else 0
                    vx *= 0.9
                    if block['type'] == "Wooden Block" and not (y + height > oy): 
                        GameConfig.SHOP_POINTS += 10
                        update_shop_ui()
                elif vx < 0:
                    x = ox + ow
                    vx = -vx * 1.1 if bouncy or block['type'] == "Ice Cube" else 0
                    vx *= 0.9
                    if block['type'] == "Wooden Block" and not (y + height > oy):
                        GameConfig.SHOP_POINTS += 10
                        update_shop_ui()

        ground_y = SCREEN_HEIGHT - height - GameConfig.FLOAT_ABOVE_BOTTOM
        if y >= ground_y:
            y = ground_y
            vy = -vy * 0.6 if bouncy and abs(vy) > 3 else 0
            grounded = True
            friction = 0.95 if slippery else 0.7

        if grounded:
            vx *= 0.99999 if slippery else friction
            if abs(vx) < 0.1:
                vx = 0

        if grounded and not is_grounded:
            if block['type'] in ("Bouncy Ball", "Ice Cube"):
                GameConfig.SHOP_POINTS += 10
                update_shop_ui()

        block.update({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'grounded': grounded})
        block['window'].geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    shop_window.after(30, apply_physics)

# === Window Dragging ===
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
            block['x'], block['y'], block['vx'], block['vy'] = x, y, dx, dy
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

def start_melting(block):
    def melt():
        # Ensure that the block is still in the game (in the open_windows list)
        if block not in open_windows:
            return

        w, h = block['width'], block['height']

        # Stop melting if the block reaches the minimum size (e.g., 10px)
        if w <= 10 or h <= 10:
            open_windows.remove(block)  # Remove the block from the list
            block['window'].destroy()   # Close the window
            return

        # Shrink the width and height gradually to simulate melting
        block['width'] = int(w * 0.98)  # Shrink by 2%
        block['height'] = int(h * 0.98)  # Shrink by 2%

        # Keep the block within the screen bounds
        block['x'] = min(block['x'], SCREEN_WIDTH - block['width'])
        block['y'] = min(block['y'], SCREEN_HEIGHT - block['height'])

        # Convert values to integers for geometry string
        w = int(block['width'])
        h = int(block['height'])
        x = int(block['x'])
        y = int(block['y'])

        # Update the window geometry
        block['window'].geometry(f"{w}x{h}+{x}+{y}")

        # Repeat the melting process after 1 second (1000 ms)
        block['window'].after(1000, melt)

    melt()

# === Delete All Objects and Refund Half Points ===
def delete_all_objects():
    global open_windows
    total_spent = sum(GameConfig.ITEM_PRICES[block['type']] for block in open_windows)
    refund = total_spent // 2  # Give back half the points spent
    GameConfig.SHOP_POINTS += refund

    for block in open_windows[:]:
        close_window(block['window'])

    update_shop_ui()  # Update the shop UI after deletion

# === Update the Shop UI ===
def update_shop_ui():
    shop_window.title(f"Window Shop: Your Points = {GameConfig.SHOP_POINTS}")
    
    # Enable/disable item buttons based on whether you can afford the items
    for item, button in shop_buttons.items():
        price_text = f"{item} (${GameConfig.ITEM_PRICES[item]})"
        button.config(text=price_text)
        button.config(state=tk.NORMAL if GameConfig.SHOP_POINTS >= GameConfig.ITEM_PRICES[item] else tk.DISABLED)
    
# === Shop GUI ===
class ShopGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)

        # Load and store background image
        self.bg_image_orig = Image.open(image_paths["Shop_bg"])
        self.bg_image_tk = None
        self.bg_image_id = None

        # ✅ Load and store button images as attributes to prevent garbage collection
        self.block_shop_img = ImageTk.PhotoImage(Image.open(image_paths["WBs"]))
        self.ball_shop_img = ImageTk.PhotoImage(Image.open(image_paths["BBs"]))
        self.ice_shop_img = ImageTk.PhotoImage(Image.open(image_paths["ICs"]))

        # ✅ Assign stored images to buttons
        shop_buttons["Wooden Block"] = tk.Button(
            self, text="Wooden Block ($10)", image=self.block_shop_img,
            compound="bottom", command=open_wood_window
        )
        shop_buttons["Bouncy Ball"] = tk.Button(
            self, text="Bouncy Ball ($20)", image=self.ball_shop_img,
            compound="bottom", command=open_ball_window
        )
        shop_buttons["Ice Cube"] = tk.Button(
            self, text="Ice Cube ($15)", image=self.ice_shop_img,
            compound="bottom", command=open_ice_window
        )

        # Place buttons on the canvas
        self.canvas.create_window(10, 10, anchor="nw", window=shop_buttons["Wooden Block"])
        self.canvas.create_window(140, 10, anchor="nw", window=shop_buttons["Bouncy Ball"])
        self.canvas.create_window(270, 10, anchor="nw", window=shop_buttons["Ice Cube"])

        # Add a button to delete all objects and refund half points
        delete_button = tk.Button(self, text="Delete All Objects", command=delete_all_objects)
        self.canvas.create_window(10, 100, anchor="nw", window=delete_button)

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

# === Main Execution ===
if __name__ == "__main__":
    shop_window = tk.Tk()
    shop_window.title(f"Window Shop: Your Points = {GameConfig.SHOP_POINTS}")
    shop_window.geometry(f"{GameConfig.SHOP_WIDTH}x{GameConfig.SHOP_HEIGHT}")
    ShopGUI(shop_window)
    update_shop_ui()
    apply_physics()

    shop_window.mainloop()
