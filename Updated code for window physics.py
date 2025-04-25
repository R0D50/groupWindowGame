
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
#import pymunk

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
image_path = "THIS NEEDS TO BE FIXED TO A RELATIVE PATH"
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

    open_windows.append({
        'window': new_window,
        'x': spawn_x,
        'y': spawn_y,
        'velocity': 0,
        'falling': True
    })


    new_window.bind("<ButtonPress-1>", lambda e, w=new_window: on_window_press(e, w))
    new_window.bind("<B1-Motion>", lambda e, w=new_window: on_window_drag(e, w))
    new_window.bind("<ButtonRelease-1>", lambda e, w=new_window: on_window_release(e, w))



 

def apply_gravity():
    for block in open_windows:
        if not block['falling']:
            continue  # Skip blocks that are not falling

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
                velocity = 0
                block['falling'] = False
                break

        if not touching_block and y < bottom_y:
            block['falling'] = True
            velocity += 2
            y += velocity

            if y > bottom_y:
                y = bottom_y
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

# Update the block's position in the open_windows list
    for block in open_windows:
        if block['window'] == window:
            block['x'] = x
            block['y'] = y
            block['falling'] = False  # Stop gravity while dragging
            break

'''
    for block in open_windows:
        if block['window'] == window:
            block['x'] = window.winfo_x()
            block['y'] = window.winfo_y()
            break
'''

def on_window_release(event, window):
    for block in open_windows:
        if block['window'] == window:
            block['x'] = window.winfo_x()
            block['y'] = window.winfo_y()
           # block['falling'] = False
            window.after(100, lambda: setFalling(block))
            break

def setFalling(block):
    block['falling'] = True






# Main image (optional)
if photo_image:
    image_label = tk.Label(window, image=photo_image)
    image_label.pack()
window.photo_image = photo_image

# Instructions
#tk.Label(window, text="Press 'n' to open a new falling block").pack()
#window.bind('n', open_new_window)

#WIP, should work for the time being though
class ShopGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg = 'white')
        self.setupShop()

    #Shop button layout setup
    def setupShop(self):
            #self.display = tk.Label(self, text = f'Points: {SHOP_POINTS}', anchor = tk.NE, \
                #bg = 'white', height = 1, font = ("TkDefaultFont", 12))
            #self.display.grid(row = 0, column = 0, columnspan = 5, sticky = tk.E+tk.W+tk.N+tk.S)
            
            #configures the rows and columns of the shop
            for row in range(6):
                tk.Grid.rowconfigure(self, row, weight = 1)
            for col in range(5):
                tk.Grid.columnconfigure(self, col, weight = 1)            
            
            #Config the shop's buttons, each will be set to its own button, page system maybe?
                #Wooden Block Button
                    #Standard item, no real special properties
            button = tk.Button(self, bg = 'white', text = "Wooden Block",
                borderwidth = 1, highlightthickness = 0, activebackground = 'white', command = open_new_window)
            #set button in the shop's grid properly
            button.grid(row = 1, column = 0, sticky = tk.E+tk.W+tk.N+tk.S)

                #New Item goes here:
                    #Item description
                    #Should just have to change the "command" tag to what the function for creating the new window type will be for this to work
            '''
            button = tk.Button(self, bg = 'white', text = "Wooden Block",
                borderwidth = 1, highlightthickness = 0, activebackground = 'white', command = open_new_window)
            #set button in the shop's grid properly
            button.grid(row = 1, column = 1, sticky = tk.E+tk.W+tk.N+tk.S)
            '''
            
            #pack the GUI
            self.pack(expand = 1)

# Create the shop 
window = tk.Tk()
window.title(f"Window Shop: Your Points = {SHOP_POINTS}")
window.geometry(f"{SHOP_WIDTH}x{SHOP_HEIGHT}")
shop = ShopGUI(window)

#updating the shop's title to show the players points
'''
def pointUpdater():
    threading.Timer(0.5, pointUpdater).start()
    if (SHOP_POINTS != 0):
        window.title(f"Window Shop: Your Points = {SHOP_POINTS}")
pointUpdater()
'''


# Start
apply_gravity()
window.mainloop()