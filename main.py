import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

root = tk.Tk()
root.title("Restaurant Simulator")
root.attributes("-fullscreen", True)
root.configure(bg="black")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

def load_image(filename):
    path = os.path.join(ASSETS_DIR, filename)
    return Image.open(path).convert("RGBA")

canvas = tk.Canvas(root, width=screen_width, height=screen_height, borderwidth=0, highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)

background_pil = load_image("background.png")
background_pil = background_pil.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
background = ImageTk.PhotoImage(background_pil)
canvas.create_image(0, 0, image=background, anchor="nw")

button_width = int(screen_width * 0.20)
button_height = int(screen_height * 0.075)
hover_scale = 1.08

def play_game():
    print("PLAY GAME")

def how_to_play():
    print("HOW TO PLAY")

def vocabulary():
    print("VOCABULARY")

def exit_game():
    root.destroy()

def create_button(filename, command, y):
    original = load_image(filename)
    state = {"scale": 1.0, "target": 1.0, "hovered": False, "pressed": False, "after_id": None, "photo": None}
    first_image = original.resize((button_width, button_height), Image.Resampling.LANCZOS)
    state["photo"] = ImageTk.PhotoImage(first_image)
    x = screen_width / 2
    y_position = screen_height * y
    item = canvas.create_image(x, y_position, image=state["photo"], anchor="center")

    def update():
        scale = state["scale"]
        width = int(button_width * scale)
        height = int(button_height * scale)
        image = original.resize((width, height), Image.Resampling.LANCZOS)
        if state["pressed"]:
            image = ImageEnhance.Brightness(image).enhance(0.60)
        state["photo"] = ImageTk.PhotoImage(image)
        canvas.itemconfig(item, image=state["photo"])

    def animate():
        state["after_id"] = None
        current = state["scale"]
        target = state["target"]
        if abs(current - target) < 0.01:
            state["scale"] = target
            update()
            return
        if current < target:
            state["scale"] += 0.015
            if state["scale"] > target:
                state["scale"] = target
        else:
            state["scale"] -= 0.015
            if state["scale"] < target:
                state["scale"] = target
        update()
        state["after_id"] = root.after(16, animate)

    def set_target(target):
        state["target"] = target
        if state["after_id"] is None:
            animate()

    def enter(event):
        state["hovered"] = True
        canvas.config(cursor="hand2")
        set_target(hover_scale)

    def leave(event):
        state["hovered"] = False
        state["pressed"] = False
        canvas.config(cursor="")
        set_target(1.0)

    def press(event):
        state["pressed"] = True
        update()

    def release(event):
        state["pressed"] = False
        update()
        if state["hovered"]:
            set_target(hover_scale)
        else:
            set_target(1.0)
        command()

    canvas.tag_bind(item, "<Enter>", enter)
    canvas.tag_bind(item, "<Leave>", leave)
    canvas.tag_bind(item, "<ButtonPress-1>", press)
    canvas.tag_bind(item, "<ButtonRelease-1>", release)
    return item

play_button = create_button("play_game.png", play_game, 0.60)
how_to_play_button = create_button("how_to_play.png", how_to_play, 0.685)
vocabulary_button = create_button("vocabulary.png", vocabulary, 0.77)
exit_button = create_button("exit.png", exit_game, 0.855)

root.bind("<Escape>", lambda event: root.destroy())

root.mainloop()