# === Imports ===
import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
import random
import math


# === Configuration ===
class GameConfig:
    WIDTH = 250
    HEIGHT = 100
    MARGIN = 0
    FLOAT_ABOVE_BOTTOM = 0
    SHOP_POINTS = 500
    SHOP_WIDTH = 600
    SHOP_HEIGHT = 300
    GRAVITY = 1.5
    ITEM_PRICES = {
        "Wooden Block": 10,
        "Bouncy Ball": 20,
        "Super Bouncy Ball": 75,
        "Ice Cube": 15,
        "Slot Machine": 75,
        "Play Slot Machine": 25,
        "Spin Slot Machine": 25,
        "Impulse Grenade": 30,  # New item
        "Implosion Grenade": 30,
        "Coin": 0
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
    "Super Bouncy Ball": root_dir / "Window_Images" / "SBB.png",
    "Ice Cube": root_dir / "Window_Images" / "IC.png",
    "Implosion": root_dir / "Window_Images" / "VG.png",
    "WBs": root_dir / "Shop_Images" / "WBs.png",
    "BBs": root_dir / "Shop_Images" / "BBs.png",
    "SBBs": root_dir / "Shop_Images" / "SBBs.png",
    "ICs": root_dir / "Shop_Images" / "ICs.png",
    "IGs": root_dir / "Shop_Images" / "IGs.png",
    "VGs": root_dir / "Shop_Images" / "VGs.png",
    "SMs": root_dir / "Shop_Images" / "SMs.png",
    "Shop_bg": root_dir / "Shop_Images" / "Shop_bg.png",
    "Apple": root_dir / "Slot_Images" / "AP.png",
    "Bell": root_dir / "Slot_Images" / "BL.png",
    "Bar": root_dir / "Slot_Images" / "BR.png",
    "Cherry": root_dir / "Slot_Images" / "CR.png",
    "Melon": root_dir / "Slot_Images" / "ML.png",
    "Orange": root_dir / "Slot_Images" / "OR.png",
    "Strawberry": root_dir / "Slot_Images" / "SB.png",
    "Coin": root_dir / "Slot_Images" / "CN.png",
    "Slot_bg": root_dir / "Slot_Images" / "SlotMachine.png",
    "Imp_gren": root_dir / "Window_Images" / "IG.png"
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
def create_window(title, image_path, is_bouncy=False, is_slippery=False, is_super_bouncy = False, scale=1.0, floating=False):
    spawn_x = len(open_windows) * (GameConfig.WIDTH + GameConfig.MARGIN) % SCREEN_WIDTH
    spawn_y = 50
    photo_image, (img_width, img_height) = load_image(image_path, scale)

    new_window = tk.Toplevel()
    new_window.title(title)
    new_window.geometry(f"{img_width}x{img_height}+{spawn_x}+{spawn_y}")
    new_window.resizable(False, False)
    new_window.overrideredirect(True)

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
        'super_bouncy': is_super_bouncy,
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

# === Purchasing Functions ===
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

def open_super_ball_window(event=None):
    try_purchase("Super Bouncy Ball", lambda: create_window("Super Bouncy Ball", image_paths["Super Bouncy Ball"], is_super_bouncy=True, scale=0.5))

def open_ice_window(event=None):
    try_purchase("Ice Cube", lambda: create_window("Ice Cube", image_paths["Ice Cube"], is_slippery=True, scale=0.5))

# === NEW: Impulse Grenade ===
def open_impulse_grenade(event=None):
    try_purchase("Impulse Grenade", create_impulse_grenade)

def open_implosion_grenade(event=None):
    try_purchase("Implosion Grenade", create_implosion_grenade)

def create_impulse_grenade():
    def on_explode(grenade_block):
        if grenade_block not in open_windows:
            return

        gx = grenade_block['x'] + grenade_block['width'] / 2
        gy = grenade_block['y'] + grenade_block['height'] / 2
        radius = 500
        max_force = 150

        for other in open_windows:
            if other == grenade_block or other.get('floating'):
                continue

            ox = other['x'] + other['width'] / 2
            oy = other['y'] + other['height'] / 2
            dx = ox - gx
            dy = oy - gy
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < radius and dist > 0:
                angle = math.atan2(dy, dx)
                force = max_force * (1 - dist / radius)
                other['vx'] += math.cos(angle) * force
                other['vy'] += math.sin(angle) * force

        close_window(grenade_block['window'])

    # Create the grenade window like a block
    create_window(
        title="Impulse Grenade",
        image_path= root_dir / "Window_Images" / "IG.png",
        scale=.25,
        floating=False
    )

    grenade_block = open_windows[-1]  # The most recently created block
    label = tk.Label(grenade_block['window'], text="IMPULSE\nGRENADE", bg="gray", fg="white")
    label.pack(fill="both", expand=True)

    # Schedule explosion
    grenade_block['window'].after(3000, lambda: on_explode(grenade_block))

def create_implosion_grenade():
    def on_explode(void_grenade_block):
        if void_grenade_block not in open_windows:
            return

        gx = void_grenade_block['x'] + void_grenade_block['width'] / 2
        gy = void_grenade_block['y'] + void_grenade_block['height'] / 2
        radius = 500
        max_force = -200

        for other in open_windows:
            if other == void_grenade_block or other.get('floating'):
                continue

            ox = other['x'] + other['width'] / 2
            oy = other['y'] + other['height'] / 2
            dx = ox - gx
            dy = oy - gy
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < radius and dist > 0:
                angle = math.atan2(dy, dx)
                force = max_force * (1 - dist / radius)
                other['vx'] += math.cos(angle) * force
                other['vy'] += math.sin(angle) * force

        close_window(void_grenade_block['window'])

    # Create the grenade window like a block
    create_window(
        title="Implosion Grenade",
        image_path= root_dir / "Window_Images" / "VG.png",
        scale=.25,
        floating=False
    )

    void_grenade_block = open_windows[-1]  # The most recently created block
    #label = tk.Label(void_grenade_block['window'], text="IMPULSE\nGRENADE", bg="gray", fg="white")
    #label.pack(fill="both", expand=True)

    # Schedule explosion
    void_grenade_block['window'].after(3000, lambda: on_explode(void_grenade_block))

# === Coin ===
def open_coin_window(event=None):
    try_purchase("Coin", lambda: create_coin_window())

def give_points():
    reward = random.randint(1, 6)
    GameConfig.SHOP_POINTS += reward
    update_shop_ui()
    close_window("Coin")

def create_coin_window():
    coin_image = ImageTk.PhotoImage(Image.open(image_paths["Coin"]))

    coin_window = tk.Toplevel()
    coin_window.geometry(f"50x50")
    coin_window.resizable(False,False)
    coin_window.overrideredirect(True)

    coin_button = tk.Button(coin_window, image = coin_image, command = give_points())
    coin_button.pack(fill="both", expand=True)
    
# === Slot Machine ===
def open_slot_machine(event=None):
    try_purchase("Slot Machine", lambda: create_slot_machine_window())

def create_slot_machine_window():
    slot_machine_window = tk.Toplevel()
    slot_machine_window.title("Slot Machine")
    slot_machine_window.geometry(f"400x300+{SCREEN_WIDTH//2-200}+{SCREEN_HEIGHT//2-150}")
    slot_machine_window.resizable(False, False)

    bg_img = Image.open(image_paths["Slot_bg"]).resize((400, 300), Image.Resampling.LANCZOS)
    bg_tk = ImageTk.PhotoImage(bg_img)

    canvas = tk.Canvas(slot_machine_window, width=400, height=300, highlightthickness=0, bd=0)
    canvas.pack()
    canvas.bg_img = bg_tk
    canvas.create_image(0, 0, image=bg_tk, anchor="nw")

    slot_positions = [(100, 135), (185, 135), (270, 135)]
    fruit_image_ids = [None, None, None]  # Start with empty slots

    fruits = ["Apple", "Cherry", "Melon", "Orange", "Strawberry", "Bell", "Bar"]
    fruit_weights = [5, 5, 5, 5, 5, 2, 1]
    spin_result = random.choices(fruits, weights=fruit_weights, k=3)
    fruit_imgs = {}
    for fruit in fruits:
        img = Image.open(image_paths[fruit]).resize((75, 75), Image.Resampling.LANCZOS)
        fruit_imgs[fruit] = ImageTk.PhotoImage(img)

    # Create placeholder image slots (invisible until spin starts)
    for i, (x, y) in enumerate(slot_positions):
        fruit_image_ids[i] = canvas.create_image(x, y, image=None)

    # Create 5 text layers for outline
    text_positions = [(200 + dx, 200 + dy) for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]]
    result_text_ids = [
        canvas.create_text(x, y, text="", font=("Arial", 16, "bold"),
                           fill="black" if (x, y) != (200, 200) else "white")
        for (x, y) in text_positions
    ]

    def on_click():
        play_slot_machine_canvas(canvas, fruit_image_ids, result_text_ids, fruit_imgs, play_button)

    play_button = tk.Button(canvas, text="Play Slot Machine ($25)", command=on_click,
                            bg="gray20", fg="white", bd=0, highlightthickness=0)
    canvas.create_window(200, 260, window=play_button)

def play_slot_machine_canvas(canvas, fruit_image_ids, result_text_ids, fruit_imgs, play_button):
    if GameConfig.SHOP_POINTS < GameConfig.ITEM_PRICES["Play Slot Machine"]:
        return

    GameConfig.SHOP_POINTS -= GameConfig.ITEM_PRICES["Play Slot Machine"]
    update_shop_ui()
    play_button.config(state=tk.DISABLED)

    # Clear previous text
    for tid in result_text_ids:
        canvas.itemconfig(tid, text="")

    fruits = list(fruit_imgs.keys())
    spin_cycles = 20
    fruit_weights = [5, 5, 5, 5, 5, 2, 1]
    final_result = random.choices(fruits, weights=fruit_weights, k=3)

    def spin_cycle(count=0):
        if count < spin_cycles:
            spin_result = random.choices(fruits, k=3)
            for i, fruit in enumerate(spin_result):
                canvas.itemconfig(fruit_image_ids[i], image=fruit_imgs[fruit])
            canvas.after(100, lambda: spin_cycle(count + 1))
        else:
            for i, fruit in enumerate(final_result):
                canvas.itemconfig(fruit_image_ids[i], image=fruit_imgs[fruit])

            reward = 0
            if final_result[0] == final_result[1] == final_result[2]:
                reward = random.randint(8, 12) if final_result[0] == "Bar" else \
                         random.randint(3, 8) if final_result[0] == "Bell" else \
                         random.randint(1, 5)
            elif final_result[0] == final_result[1] or final_result[1] == final_result[2] or final_result[0] == final_result[2]:
                reward = 2
            else:
                reward = 1

            #GameConfig.SHOP_POINTS += reward
            #update_shop_ui()

            for i in range(reward):
                open_coin_window()


            # Set bordered text
            #if reward != 1:
                #result_text = f"You won {reward} points!"
            #if reward == 1:
                #result_text = f"You won {reward} point!"
            #for tid in result_text_ids[:-1]:
                #canvas.itemconfig(tid, text=result_text)
            #canvas.itemconfig(result_text_ids[-1], text=result_text)  # White top text

            # Cleanup after delay
            def cleanup():
                for img_id in fruit_image_ids:
                    canvas.itemconfig(img_id, image=None)
                #for tid in result_text_ids:
                    #canvas.itemconfig(tid, text="")
                play_button.config(state=tk.NORMAL)

            canvas.after(2000, cleanup)

    spin_cycle()

    update_shop_ui()

def apply_physics():
    for block in open_windows[:]:
        if block.get('floating'):
            continue

        x, y = block['x'], block['y']
        vx, vy = block['vx'], block['vy']
        width, height = block['width'], block['height']
        bouncy, slippery, super_bouncy = block['bouncy'], block['slippery'], block['super_bouncy']
        is_grounded = block['grounded']
        vy += GameConfig.GRAVITY
        x += vx
        y += vy
        grounded = False
        friction = 0.7

        # Check if it's an ice cube
        if block['type'] == "Ice Cube" and 'bounced' not in block:
            block['bounced'] = False

        if block['stacked_on']:
            stack_block = block['stacked_on']
            block['x'] = stack_block['x']
            block['y'] = stack_block['y'] - block['height']
            continue

        # Walls
        if x <= 0 or x + width >= SCREEN_WIDTH:
            x = max(0, min(SCREEN_WIDTH - width, x))
            if bouncy or super_bouncy or block['type'] == "Ice Cube":
                # Ice Cube behavior: Slide along the wall
                if block['type'] == "Ice Cube" and not block['bounced'] and not block['grounded']:
                    # Only bounce when grounded
                    if is_grounded:
                        GameConfig.SHOP_POINTS += 10
                        block['bounced'] = True  # Mark that the Ice Cube has bounced off the wall
                        update_shop_ui()

                # Sliding effect: Apply velocity reduction when the ice cube slides along the wall
                vx = -vx * 1 if super_bouncy else -vx * 0.9  # Slightly reverse the horizontal velocity
                vx *= 1 if super_bouncy else 0.9  # Reduce speed as it slides down
            else:
                vx = 0

        # Collisions with other objects
        for other in open_windows:
            if other == block or other.get('floating'):
                continue
            ox, oy, ow, oh = other['x'], other['y'], other['width'], other['height']
            if (x < ox + ow and x + width > ox and y + height > oy and y < oy + oh):
                if vy > 0 and y + height - vy <= oy:
                    y = oy - height
                    vy = -vy * 0.6 if bouncy and abs(vy) > 3 else -vy * 1.1 if super_bouncy and abs(vy) > 3 else -vy * 0
                    grounded = True
                elif vx > 0:
                    x = ox - width
                    vx = -vx * 0.9 if bouncy else 0.9 if slippery else -vx * 1.1 if super_bouncy else -vx * 0
                    vx *= 1 if super_bouncy else 0.9
                elif vx < 0:
                    x = ox + ow
                    vx = -vx * 0.9 if bouncy else 0.9 if slippery else -vx * 1.1 if super_bouncy else -vx * 0
                    vx *= 1 if super_bouncy else 0.9

        # Ground check for ice cube and other objects
        ground_y = SCREEN_HEIGHT - height - GameConfig.FLOAT_ABOVE_BOTTOM
        if y >= ground_y:
            y = ground_y
            vy = -vy * 0.6 if bouncy and abs(vy) > 3 else -vy * 1 if super_bouncy and abs(vy) > 3 else -vy * 0
            grounded = True
            friction = 0.995 if slippery else 1 if super_bouncy else 0.7

        if grounded:
            vx *= 0.995 if slippery else 1 if super_bouncy else friction
            if abs(vx) < 0.1:
                vx = 0

        # When ice cube is grounded, apply extra physics (bounce/slide on impact)
        if grounded and not is_grounded:
            if block['type'] == "Bouncy Ball":
                GameConfig.SHOP_POINTS += 5
            if block['type'] == "Wooden Block":
                GameConfig.SHOP_POINTS += 2
            if block['type'] == "Super Bouncy Ball":
                GameConfig.SHOP_POINTS += 1
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
            block['vx'] = max(-300, min(block['vx'], 300))
            block['vy'] = max(-300, min(block['vy'], 300))
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


# === Shop GUI Update ===
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
        self.super_ball_shop_img = ImageTk.PhotoImage(Image.open(image_paths["SBBs"]))
        self.ice_shop_img = ImageTk.PhotoImage(Image.open(image_paths["ICs"]))
        self.impulse_shop_img = ImageTk.PhotoImage(Image.open(image_paths["IGs"]))
        self.slots_shop_img = ImageTk.PhotoImage(Image.open(image_paths["SMs"]))
        self.implosion_shop_img = ImageTk.PhotoImage(Image.open(image_paths["VGs"]))

        shop_buttons["Wooden Block"] = tk.Button(self, image=self.block_shop_img, compound="bottom", command=open_wood_window)
        shop_buttons["Bouncy Ball"] = tk.Button(self, image=self.ball_shop_img, compound="bottom", command=open_ball_window)
        shop_buttons["Super Bouncy Ball"] = tk.Button(self, image=self.super_ball_shop_img, compound="bottom", command=open_super_ball_window)
        shop_buttons["Ice Cube"] = tk.Button(self, image=self.ice_shop_img, compound="bottom", command=open_ice_window)
        shop_buttons["Slot Machine"] = tk.Button(self, text="Slot Machine", image = self.slots_shop_img, compound= "bottom", command=open_slot_machine)
        shop_buttons["Impulse Grenade"] = tk.Button(self, text="Impulse Grenade", image = self.impulse_shop_img, compound= "bottom", command=open_impulse_grenade)  # NEW BUTTON
        shop_buttons["Implosion Grenade"] = tk.Button(self, text="Implosion Grenade", image = self.implosion_shop_img, compound= "bottom", command=open_implosion_grenade)

        self.canvas.create_window(10, 10, anchor="nw", window=shop_buttons["Wooden Block"])
        self.canvas.create_window(140, 10, anchor="nw", window=shop_buttons["Bouncy Ball"])
        self.canvas.create_window(270, 10, anchor="nw", window=shop_buttons["Ice Cube"])
        self.canvas.create_window(400, 10, anchor="nw", window=shop_buttons["Super Bouncy Ball"])
        self.canvas.create_window(10, 100, anchor="nw", window=shop_buttons["Slot Machine"])
        self.canvas.create_window(140, 100, anchor="nw", window=shop_buttons["Impulse Grenade"])  # BUTTON POSITION
        self.canvas.create_window(270, 100, anchor="nw", window=shop_buttons["Implosion Grenade"]) 

        self.refund_button = tk.Button(self, text="Refund All", command=self.refund_all)
        self.canvas.create_window(10, 190, anchor="nw", window=self.refund_button)

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

    def refund_all(self):
        global open_windows
        total_refund = 0
        for block in open_windows[:]:
            block_type = block['type']
            if block_type == "Ice Cube":
                original_width = block['window'].winfo_width()
                melted_pct = 1 - (original_width / GameConfig.WIDTH)
                refund = max(1, (GameConfig.ITEM_PRICES["Ice Cube"] * (1 - melted_pct)))
            else:
                refund = (GameConfig.ITEM_PRICES.get(block_type, 0) /2)
            total_refund += int(refund)
            close_window(block['window'])
        open_windows.clear()
        GameConfig.SHOP_POINTS += total_refund
        update_shop_ui()

def update_shop_ui():
    shop_window.title(f"Window Shop: Your Points = {GameConfig.SHOP_POINTS}")
    for item, button in shop_buttons.items():
        price = GameConfig.ITEM_PRICES.get(item, 'N/A')
        button.config(text=f"{item} (${price})")
        button.config(state=tk.NORMAL if GameConfig.SHOP_POINTS >= price else tk.DISABLED)

# === Main ===
if __name__ == "__main__":
    shop_window = tk.Tk()
    shop_window.title(f"Window Shop: Your Points = {GameConfig.SHOP_POINTS}")
    shop_window.geometry(f"{GameConfig.SHOP_WIDTH}x{GameConfig.SHOP_HEIGHT}")
    ShopGUI(shop_window)
    update_shop_ui()
    apply_physics()
    shop_window.mainloop()
