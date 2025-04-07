import tkinter as tk
from PIL import Image, ImageTk

# Constants
WIDTH = 250
HEIGHT = 100
MARGIN = 0  # Margin between windows to avoid overlap
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FLOAT_ABOVE_BOTTOM = 25  # Float slightly above the bottom edge of the screen

# Create main window                                                                                                                                      without changing too much of the code i want to make it to where i can stack as many blocks as i want and the possibility of stacking two blocks on a single block 
window = tk.Tk()
window.title("Wooden Block")
window.geometry(f"{WIDTH}x{HEIGHT}")

# List to store the positions of all open windows
open_windows = []

# Function to open a new window with the image each time 'n' is pressed
def open_new_window(event=None):
    image_path = "C:\\Users\\markm\\OneDrive\\Desktop\\Screenshot 2025-03-31 091325.png"
    
    # Open and prepare the image
    image = Image.open(image_path)
    photo_image = ImageTk.PhotoImage(image)

    # Calculate the position for the new window
    new_x, new_y = get_stacking_position()

    # Create a new window and display the image
    new_window = tk.Toplevel()
    new_window.title("Wooden Block")
    new_window.geometry(f"{WIDTH}x{HEIGHT}+{new_x}+{new_y}")  # Set position of the new window
    
    # Create a label to show the image
    label = tk.Label(new_window, image=photo_image)
    label.pack()

    # Keep a reference to the photo_image to prevent garbage collection
    new_window.photo_image = photo_image

    # Store the new window's position in the open_windows list
    open_windows.append((new_window, new_x, new_y))

    # Bind the movement of the window to detect collision when the window is dropped
    new_window.bind("<ButtonPress-1>", lambda event, window=new_window: on_window_press(event, window))
    new_window.bind("<B1-Motion>", lambda event, window=new_window: on_window_drag(event, window))
    new_window.bind("<ButtonRelease-1>", lambda event, window=new_window: on_window_release(event, window))

# Function to get the position for the new window, stacking it from the bottom
def get_stacking_position():
    # Calculate the available space
    max_columns = (SCREEN_WIDTH // (WIDTH + MARGIN))
    max_rows = (SCREEN_HEIGHT // (HEIGHT + MARGIN))

    # Find the next available position in the grid (row by row, left to right)
    row = len(open_windows) // max_columns
    column = len(open_windows) % max_columns

    # Start slightly above the bottom, moving upwards as new windows are created
    new_x = column * (WIDTH + MARGIN)
    new_y = SCREEN_HEIGHT - HEIGHT - FLOAT_ABOVE_BOTTOM - ((row) * (HEIGHT + MARGIN))  # Float just above the bottom

    # Check if we exceed the screen height (wrap to top if needed)
    if new_y < 0:
        new_y = SCREEN_HEIGHT - HEIGHT - FLOAT_ABOVE_BOTTOM  # Start a new row at the bottom again

    return new_x, new_y

# Function to handle when the user presses the window
def on_window_press(event, window):
    # Record the initial position when the user clicks on the window
    window.initial_x = window.winfo_x()  # Initial x position of the window
    window.initial_y = window.winfo_y()  # Initial y position of the window
    window.drag_data = {'x': event.x, 'y': event.y}  # Store initial mouse position

# Function to handle window dragging
def on_window_drag(event, window):
    # Calculate the distance moved
    delta_x = event.x - window.drag_data['x']
    delta_y = event.y - window.drag_data['y']
    
    # Move the window to the new position
    new_x = window.initial_x + delta_x
    new_y = window.initial_y + delta_y
    window.geometry(f"{WIDTH}x{HEIGHT}+{new_x}+{new_y}")

# Function to handle when the user releases the window (drop)
def on_window_release(event, window):
    # Get the current position of the window when the user releases the mouse
    window_x = window.winfo_x()
    window_y = window.winfo_y()

    # Check for overlap with other windows and handle collision
    for other_window, other_x, other_y in open_windows:
        if other_window != window:  # Ignore the current window itself
            if (window_x < other_x + WIDTH + MARGIN and window_x + WIDTH + MARGIN > other_x and
                window_y < other_y + HEIGHT + MARGIN and window_y + HEIGHT + MARGIN > other_y):
                print("Collision detected!")

                # Determine the direction to move the window
                move_direction = determine_move_direction(window_x, window_y, other_x, other_y)

                if move_direction == 'top':  # Stack on top of the other window
                    new_x, new_y = other_x, other_y - HEIGHT - MARGIN  # Move window on top
                elif move_direction == 'left':  # Move to the left of the other window
                    new_x, new_y = other_x - WIDTH - MARGIN, other_y  # Move window to the left
                elif move_direction == 'right':  # Move to the right of the other window
                    new_x, new_y = other_x + WIDTH + MARGIN, other_y  # Move window to the right

                # Now ensure the window maintains its relative position from where the user started
                window.geometry(f"{WIDTH}x{HEIGHT}+{new_x}+{new_y}")
                
                # Update the position in open_windows
                for idx, (win, _, _) in enumerate(open_windows):
                    if win == window:
                        open_windows[idx] = (window, new_x, new_y)
                break

    # Check if the window is not at the bottom and move it if there is no block below
    move_to_bottom_or_on_top(window)

# Function to determine the best position (top, left, or right) for the moved window
def determine_move_direction(window_x, window_y, other_x, other_y):
    # Determine the available space based on horizontal or vertical distance
    distance_to_top = window_y - (other_y + HEIGHT + MARGIN)
    distance_to_left = window_x - (other_x + WIDTH + MARGIN)
    distance_to_right = (other_x + WIDTH + MARGIN) - window_x

    # Choose the direction based on proximity
    if abs(distance_to_top) < abs(distance_to_left) and abs(distance_to_top) < abs(distance_to_right):
        return 'top'
    elif abs(distance_to_left) < abs(distance_to_top) and abs(distance_to_left) < abs(distance_to_right):
        return 'left'
    else:
        return 'right'

# Function to move the window to the bottom if possible (or on top of another block)
def move_to_bottom_or_on_top(window):
    window_x = window.winfo_x()
    window_y = window.winfo_y()

    # Check if the window is in the air (not at the bottom)
    bottom_y = SCREEN_HEIGHT - HEIGHT - FLOAT_ABOVE_BOTTOM

    if window_y != bottom_y:  # Window is not at the bottom
        # Check if there's any window below the current one
        is_clear_below = True
        for other_window, other_x, other_y in open_windows:
            if other_window != window:  # Skip checking against itself
                if window_x < other_x + WIDTH + MARGIN and window_x + WIDTH + MARGIN > other_x:
                    if window_y + HEIGHT + MARGIN < other_y:  # There's a block below
                        is_clear_below = False
                        break

        # If there's no block below and it's not at the bottom, move it to the bottom
        if is_clear_below:
            window.geometry(f"{WIDTH}x{HEIGHT}+{window_x}+{bottom_y}")
            
            # Update the position in open_windows
            for idx, (win, _, _) in enumerate(open_windows):
                if win == window:
                    open_windows[idx] = (window, window_x, bottom_y)
        else:
            # If there's a block below, move the window on top of the block
            for other_window, other_x, other_y in open_windows:
                if other_window != window:  # Skip the window itself
                    if window_x < other_x + WIDTH + MARGIN and window_x + WIDTH + MARGIN > other_x:
                        if window_y + HEIGHT + MARGIN < other_y:  # Block is below
                            new_y = other_y - HEIGHT - MARGIN
                            window.geometry(f"{WIDTH}x{HEIGHT}+{window_x}+{new_y}")
                            

                            # Update the position in open_windows
                            for idx, (win, _, _) in enumerate(open_windows):
                                if win == window:
                                    open_windows[idx] = (window, window_x, new_y)
                            break

# Load the image for the main window (optional, it can be omitted if not needed)
image_path = "C:\\Users\\markm\\OneDrive\\Desktop\\Screenshot 2025-03-31 091325.png"
image = Image.open(image_path)
photo_image = ImageTk.PhotoImage(image)

# Display the image in the main window (optional, it can be omitted if not needed)
image_label = tk.Label(window, image=photo_image)
image_label.pack()

# Keep a reference to the photo_image to prevent garbage collection
window.photo_image = photo_image

# Bind the 'n' key to open a new window every time it is pressed
window.bind('n', open_new_window)

# Inform the user to press 'n'
tk.Label(window, text="Press 'n' to open a new window").pack()

window.mainloop()
