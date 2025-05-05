# Place this at the top with your other imports
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
    SHOP_POINTS = 500
    SHOP_WIDTH = 400
    SHOP_HEIGHT = 400
    GRAVITY = 1.5
    ITEM_PRICES = {
        "Wooden Block": 10,
        "Bouncy Ball": 20,
        "Ice Cube": 15,
        "Slot Machine": 75,
        "Play Slot Machine": 25,
        "Spin Slot Machine": 25
    }

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
    "Shop_bg": root_dir / "Shop_Images" / "Shop_bg.png",
    "Apple": root_dir / "Slot_Images" / "AP.png",
    "Bell": root_dir / "Slot_Images" / "BL.png",
    "Bar": root_dir / "Slot_Images" / "BR.png",
    "Cherry": root_dir / "Slot_Images" / "CR.png",
    "Melon": root_dir / "Slot_Images" / "ML.png",
    "Orange": root_dir / "Slot_Images" / "OR.png",
    "Strawberry": root_dir / "Slot_Images" / "SB.png",
    "Coin": root_dir / "Slot_Images" / "CN.png"
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
def create_window(title, image_path, is_bouncy=False, is_slippery=False, scale=1.0, floating=False):
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
        'stacked_on': None,
        'floating': floating
    }

    open_windows.append(block)
    new_window.protocol("WM_DELETE_WINDOW", lambda w=new_window: close_window(w))
    new_window.bind("<ButtonPress-1>", lambda e, w=new_window: on_window_press(e, w))
    new_window.bind("<B1-Motion>", lambda e, w=new_window: on_window_drag(e, w))
    new_window.bind("<ButtonRelease-1>", lambda e, w=new_window: on_window_release(e, w))

    if title == "Ice Cube":
        start_melting(block)

    if floating:
        new_window.after(3000, lambda: close_window(new_window))

def close_window(window):
    global open_windows
    open_windows = [b for b in open_windows if b['window'] != window]
    window.destroy()

# === Purchasing ===
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

# === Slot Machine ===
def open_slot_machine(event=None):
    try_purchase("Slot Machine", lambda: create_slot_machine_window())

def create_slot_machine_window():
    slot_machine_window = tk.Toplevel()
    slot_machine_window.title("Slot Machine")
    slot_machine_window.geometry(f"400x300+{SCREEN_WIDTH//2-200}+{SCREEN_HEIGHT//2-150}")
    play_button = tk.Button(slot_machine_window, text="Play Slot Machine ($25)", command=play_slot_machine)
    play_button.pack(pady=20)

def play_slot_machine():
    cost = GameConfig.ITEM_PRICES["Play Slot Machine"]
    if GameConfig.SHOP_POINTS >= cost:
        GameConfig.SHOP_POINTS -= cost
        update_shop_ui()

        fruits = ["Apple", "Bell", "Bar", "Cherry", "Melon", "Orange", "Strawberry"]
        fruit1, fruit2, fruit3 = random.choices(fruits, k=3)

        # Create floating fruit windows
        create_window(fruit1, image_paths[fruit1], scale=0.5, floating=True)
        create_window(fruit2, image_paths[fruit2], scale=0.5, floating=True)
        create_window(fruit3, image_paths[fruit3], scale=0.5, floating=True)

        if fruit1 == fruit2 == fruit3:
            if fruit1 == "Bell":
                GameConfig.SHOP_POINTS += random.randint(5, 20)
            elif fruit1 == "Bar":
                GameConfig.SHOP_POINTS += random.randint(10, 30)
            else:
                GameConfig.SHOP_POINTS += random.randint(1, 10)
        elif fruit1 == fruit2 or fruit2 == fruit3 or fruit1 == fruit3:
            GameConfig.SHOP_POINTS += random.randint(3, 8)
        else:
            GameConfig.SHOP_POINTS += random.randint(1, 5)

        update_shop_ui()

# === Physics ===
def apply_physics():
    for block in open_windows[:]:
        if block.get('floating'):
            continue

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

        if block['stacked_on']:
            stack_block = block['stacked_on']
            block['x'] = stack_block['x']
            block['y'] = stack_block['y'] - block['height']
            continue

        # Walls
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

        # Collisions
        for other in open_windows:
            if other == block or other.get('floating'):
                continue
            ox, oy, ow, oh = other['x'], other['y'], other['width'], other['height']
            if (x < ox + ow and x + width > ox and y + height > oy and y < oy + oh):
                if vy > 0 and y + height - vy <= oy:
                    y = oy - height
                    vy = -vy * 0.6 if bouncy and abs(vy) > 3 else 0
                    grounded = True
                elif vx > 0:
                    x = ox - width
                    vx = -vx * 1.1 if bouncy else 0
                    vx *= 0.9
                elif vx < 0:
                    x = ox + ow
                    vx = -vx * 1.1 if bouncy else 0
                    vx *= 0.9

        # Ground
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
            if block['type'] == "Bouncy Ball":
                GameConfig.SHOP_POINTS += 10
            elif block['type'] == "Ice Cube":
                GameConfig.SHOP_POINTS += 1
            update_shop_ui()

        block.update({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'grounded': grounded})
        block['window'].geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    shop_window.after(30, apply_physics)

# === Dragging ===
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

# === Melting ===
def start_melting(block):
    def melt():
        if block not in open_windows:
            return

        w, h = block['width'], block['height']
        if w <= 10 or h <= 10:
            open_windows.remove(block)
            block['window'].destroy()
            return

        block['width'] = int(w * 0.98)
        block['height'] = int(h * 0.98)
        block['x'] = min(block['x'], SCREEN_WIDTH - block['width'])
        block['y'] = min(block['y'], SCREEN_HEIGHT - block['height'])

        w, h, x, y = int(block['width']), int(block['height']), int(block['x']), int(block['y'])
        block['window'].geometry(f"{w}x{h}+{x}+{y}")
        block['window'].after(1000, melt)

    melt()

# === Delete All Objects ===
def delete_all_objects():
    global open_windows
    total_spent = sum(GameConfig.ITEM_PRICES.get(block['type'], 0) for block in open_windows)
    refund = total_spent // 2
    GameConfig.SHOP_POINTS += refund

    for block in open_windows[:]:
        close_window(block['window'])

    update_shop_ui()

# === Update UI ===
def update_shop_ui():
    shop_window.title(f"Window Shop: Your Points = {GameConfig.SHOP_POINTS}")
    for item, button in shop_buttons.items():
        price = GameConfig.ITEM_PRICES.get(item, 'N/A')
        button.config(text=f"{item} (${price})")
        button.config(state=tk.NORMAL if GameConfig.SHOP_POINTS >= price else tk.DISABLED)

# === GUI ===
class ShopGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.bg_image_orig = Image.open(image_paths["Shop_bg"])
        self.bg_image_tk = None
        self.bg_image_id = None

        self.block_shop_img = ImageTk.PhotoImage(Image.open(image_paths["WBs"]))
        self.ball_shop_img = ImageTk.PhotoImage(Image.open(image_paths["BBs"]))
        self.ice_shop_img = ImageTk.PhotoImage(Image.open(image_paths["ICs"]))

        shop_buttons["Wooden Block"] = tk.Button(self, image=self.block_shop_img, compound="bottom", command=open_wood_window)
        shop_buttons["Bouncy Ball"] = tk.Button(self, image=self.ball_shop_img, compound="bottom", command=open_ball_window)
        shop_buttons["Ice Cube"] = tk.Button(self, image=self.ice_shop_img, compound="bottom", command=open_ice_window)
        shop_buttons["Slot Machine"] = tk.Button(self, text="Slot Machine", command=open_slot_machine)
        
        self.canvas.create_window(10, 10, anchor="nw", window=shop_buttons["Wooden Block"])
        self.canvas.create_window(140, 10, anchor="nw", window=shop_buttons["Bouncy Ball"])
        self.canvas.create_window(270, 10, anchor="nw", window=shop_buttons["Ice Cube"])
        self.canvas.create_window(10, 100, anchor="nw", window=shop_buttons["Slot Machine"])
        
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

# === Main ===
if __name__ == "__main__":
    shop_window = tk.Tk()
    shop_window.title(f"Window Shop: Your Points = {GameConfig.SHOP_POINTS}")
    shop_window.geometry(f"{GameConfig.SHOP_WIDTH}x{GameConfig.SHOP_HEIGHT}")
    ShopGUI(shop_window)
    update_shop_ui()
    apply_physics()
    shop_window.mainloop()
