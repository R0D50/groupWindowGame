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

_temp_root = tk.Tk()
SCREEN_WIDTH = _temp_root.winfo_screenwidth()
SCREEN_HEIGHT = _temp_root.winfo_screenheight()
_temp_root.destroy()

open_windows = []

image_path_block = "C:\\Users\\markm\\OneDrive\\Desktop\\Screenshot 2025-03-31 091325.png"
image_path_ball = "C:\\Users\\markm\\OneDrive\\Desktop\\download-removebg-preview.png"

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

def apply_gravity():
    for block in open_windows:
        win = block['window']
        x, y = block['x'], block['y']
        vx, vy = block.get('vx', 0), block.get('vy', 0)
        width, height = block['width'], block['height']
        is_bouncy = block.get('bouncy', False)

        if block['falling']:
            vy += 1.5
        else:
            vx *= 0.98
            vy *= 0.98

        x += vx
        y += vy

        if x <= 0:
            x = 0
            vx = -vx * 0.6 if is_bouncy else 0
        elif x + width >= SCREEN_WIDTH:
            x = SCREEN_WIDTH - width
            vx = -vx * 0.6 if is_bouncy else 0

        if y <= 0:
            y = 0
            vy = -vy * 0.6 if is_bouncy else 0

        collided = False
        block['support'] = None

        for other in open_windows:
            if other == block:
                continue
            ox, oy = other['x'], other['y']
            ow, oh = other['width'], other['height']

            if (x < ox + ow and x + width > ox and
                y + height > oy and y < oy + oh):
                collided = True

                if vy > 0 and y < oy:
                    y = oy - height
                    vy = -vy * 0.6 if is_bouncy else 0
                    block['falling'] = is_bouncy and abs(vy) > 2
                    block['support'] = other

                elif vx > 0 and x + width > ox and x < ox + ow:
                    vx = -vx * 0.6 if is_bouncy else 0
                elif vx < 0 and x < ox + ow and x + width > ox:
                    vx = -vx * 0.6 if is_bouncy else 0

                if vy == 0 and not block['falling']:
                    vy = 1.5
                break

        ground_y = SCREEN_HEIGHT - height - FLOAT_ABOVE_BOTTOM
        if y >= ground_y:
            y = ground_y
            if is_bouncy:
                if abs(vy) > 2:
                    vy = -vy * 0.6
                    block['falling'] = True
                else:
                    vy = 0
                    block['falling'] = False
            else:
                vy = 0
                block['falling'] = False

        # Friction logic for all objects
        if not block['falling']:
            vy = 0
            friction = 0.9 if is_bouncy else 0.8
            vx *= friction
            if abs(vx) < 0.2:
                vx = 0

        block.update({'x': x, 'y': y, 'vx': vx, 'vy': vy})
        win.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    shop_window.after(30, apply_gravity)

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
            block['x'] = x
            block['y'] = y
            block['falling'] = False
            block['vx'] = dx
            block['vy'] = dy

            for other in open_windows:
                if other.get('support') == block:
                    other['x'] += dx
                    other['y'] += dy
                    other['falling'] = False
                    other['vx'] = dx
                    other['vy'] = dy
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

            # Flick momentum for all objects
            max_flick_velocity = 30
            block['vx'] = max(-max_flick_velocity, min(block['vx'], max_flick_velocity))
            block['vy'] = max(-max_flick_velocity, min(block['vy'], max_flick_velocity))
            block['falling'] = True

            window.after(100, lambda: setFalling(block))
            break

def setFalling(block):
    if block['y'] < SCREEN_HEIGHT:
        block['falling'] = True

class ShopGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg='white')
        self.setupShop()

    def setupShop(self):
        for row in range(6):
            tk.Grid.rowconfigure(self, row, weight=1)
        for col in range(5):
            tk.Grid.columnconfigure(self, col, weight=1)

        block_button = tk.Button(self, bg='white', text="Wooden Block",
            borderwidth=1, highlightthickness=0, activebackground='white', command=open_new_window)
        block_button.grid(row=1, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

        ball_button = tk.Button(self, bg='white', text="Bouncy Ball",
            borderwidth=1, highlightthickness=0, activebackground='white', command=open_bouncy_ball_window)
        ball_button.grid(row=1, column=1, sticky=tk.E + tk.W + tk.N + tk.S)

        self.pack(expand=1)

shop_window = tk.Tk()
shop_window.title(f"Window Shop: Your Points = {SHOP_POINTS}")
shop_window.geometry(f"{SHOP_WIDTH}x{SHOP_HEIGHT}")
shop = ShopGUI(shop_window)

apply_gravity()
shop_window.mainloop()
