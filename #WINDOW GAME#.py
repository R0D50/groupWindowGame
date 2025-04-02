import tkinter as tk
import pygame, sys, pymunk

from PIL import Image, ImageTk
WIDTH = 250
HEIGHT = 100

window = tk.Tk()
window.title("Wooden Block")
window.geometry(f"{WIDTH}x{HEIGHT}")

image_path = "C:\\Users\\markm\\OneDrive\\Desktop\\Screenshot 2025-03-31 091325.png"
image = Image.open(image_path)
photo_image = ImageTk.PhotoImage(image)

image_label = tk.Label(window, image=photo_image)
image_label.pack()

window.mainloop()

