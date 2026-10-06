import tkinter as tk

#--------------#
#---Settings---#
#--------------#
WIDTH, HEIGHT = 800, 600
GROUND_Y = 340 # Top of the ground (a bit lower than half of 600)
PLAYER_SIZE = 30
MOVE_SPEED = 5
GRAVITY = 0.8
JUMP_SPEED = -14
FPS_MS = 16 # ~60 frames per second

BG = "darkorange"
FG = "black"

#------------#
#---Levels---#
#------------#
# Each level is a dictionary:
#   "start_x" : where the player starts (x of the left edge)
#   "goal_x"  : x of the exit door (touch it to finish the level)
#   "hazards" : list of (x, width, height) blocks standing on the ground
# Keep every x between 0 and WIDTH so the level is never wider than the window.
LEVELS = [
    {
        "start_x": 30,
        "goal_x": 740,
        "hazards": [(250, 40, 40), (450, 40, 60), (600, 60, 40)],
    },
    {
        "start_x": 30,
        "goal_x": 740,
        "hazards": [(150, 30, 40), (230, 30, 50), (310, 30, 60),
                    (450, 100, 45), (620, 30, 70)],
    },
    {
        "start_x": 30,
        "goal_x": 740,
        "hazards": [(120, 25, 35), (190, 25, 35), (260, 25, 35),
                    (360, 60, 70), (480, 25, 40), (540, 25, 40),
                    (650, 50, 60)],
    },
    {
        "start_x": 30,
        "goal_x": 740,
        "hazards": [(120, 25, 40), (200, 45, 35), (250, 25, 25),
                    (360, 60, 70), (480, 25, 40), (540, 25, 40),
                    (650, 50, 60), (655, 5, 5),],
    },
]

#-----------------#
#---Game engine---#
#-----------------#
class Game:
    def __init__(self, root):
        self.root = root
        root.title("LVL-Devil")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.keys = set()
        self.state = "menu" # "menu", "playing" or "message"
        self.level_index = 0
        self.deaths = 0

        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)

        self.show_menu()
        self.tick()

    #----------#
    #---Menu---#
    #----------#
    def show_menu(self):
        self.state = "menu"
        self.canvas.delete("all")
        self.canvas.create_text(WIDTH // 2, 130, text="LVL-Devil",
                                font=("Helvetica", 34, "bold"), fill=FG)

        self.menu_button("Start Game", 260, self.start_game)
        self.menu_button("Options", 340, self.show_options)
        self.menu_button("Exit", 420, self.root.destroy)

    def menu_button(self, text, y, command):
        btn = tk.Button(self.root, text=text, command=command,
                        font=("Helvetica", 18), width=14,
                        bg=FG, fg=BG, activebackground=BG,
                        activeforeground=FG, relief="flat")
        self.canvas.create_window(WIDTH // 2, y, window=btn, tags="menu_btn")

    def show_options(self):
        # Placeholder - not implemented yet.
        self.canvas.delete("options_msg")
        self.canvas.create_text(WIDTH // 2, 500, text="Options: coming soon",
                                font=("Helvetica", 16), fill=FG,
                                tags="options_msg")

    #----------#
    #---Game---#
    #----------#
    def start_game(self):
        self.level_index = 0
        self.deaths = 0
        self.load_level()

    def load_level(self):
        level = LEVELS[self.level_index]
        self.hazards = level["hazards"]
        self.goal_x = level["goal_x"]
        self.px = level["start_x"]
        self.py = GROUND_Y - PLAYER_SIZE
        self.vy = 0
        self.on_ground = True
        self.keys.clear()
        self.state = "playing"
        self.canvas.delete("all") # Also removes the menu buttons

    def restart_level(self):
        self.deaths += 1
        self.show_message("Ouch!", 600, self.load_level)

    def next_level(self):
        self.level_index += 1
        if self.level_index >= len(LEVELS):
            self.show_message("You won! Deaths: %d" % self.deaths,
                              2000, self.show_menu)
        else:
            self.show_message("Level complete!", 900, self.load_level)

    def show_message(self, text, delay_ms, then):
        self.state = "message"
        self.canvas.create_text(WIDTH // 2, 120, text=text,
                                font=("Helvetica", 32, "bold"), fill=FG)
        self.root.after(delay_ms, then)

    #-----------#
    #---Input---#
    #-----------#
    def on_key_press(self, event):
        if event.keysym == "Escape":
            if self.state != "menu":
                self.show_menu()
            return
        self.keys.add(event.keysym.lower())

    def on_key_release(self, event):
        self.keys.discard(event.keysym.lower())

    #---------------#
    #---Main loop---#
    #---------------#
    def tick(self):
        if self.state == "playing":
            self.update()
            self.draw()
        self.root.after(FPS_MS, self.tick)

    def update(self):
        # Horizontal movement
        if "left" in self.keys or "a" in self.keys:
            self.px -= MOVE_SPEED
        if "right" in self.keys or "d" in self.keys:
            self.px += MOVE_SPEED
        self.px = max(0, min(WIDTH - PLAYER_SIZE, self.px))

        # Jump
        if "space" in self.keys and self.on_ground:
            self.vy = JUMP_SPEED
            self.on_ground = False

        # Gravity
        self.vy += GRAVITY
        self.py += self.vy
        if self.py >= GROUND_Y - PLAYER_SIZE:
            self.py = GROUND_Y - PLAYER_SIZE
            self.vy = 0
            self.on_ground = True

        # Hazards
        for (hx, hw, hh) in self.hazards:
            if (self.px < hx + hw and self.px + PLAYER_SIZE > hx and
                    self.py < GROUND_Y and self.py + PLAYER_SIZE > GROUND_Y - hh):
                self.restart_level()
                return

        # Goal
        if self.px + PLAYER_SIZE >= self.goal_x:
            self.next_level()

    def draw(self):
        c = self.canvas
        c.delete("all")

        # Ground
        c.create_rectangle(0, GROUND_Y, WIDTH, HEIGHT, fill=FG, outline=FG)

        # Hazards
        for (hx, hw, hh) in self.hazards:
            c.create_rectangle(hx, GROUND_Y - hh, hx + hw, GROUND_Y,
                               fill=FG, outline=FG)

        # Goal (an outlined door so it is distinguishable)
        c.create_rectangle(self.goal_x, GROUND_Y - 60, WIDTH, GROUND_Y,
                           fill=BG, outline=FG, width=3)

        # Player
        c.create_rectangle(self.px, self.py,
                           self.px + PLAYER_SIZE, self.py + PLAYER_SIZE,
                           fill=FG, outline=FG)

        # HUD
        c.create_text(10, 10, anchor="nw", fill=FG, font=("Helvetica", 12),
                      text="Level %d/%d   Deaths: %d   (Esc = menu)"
                           % (self.level_index + 1, len(LEVELS), self.deaths))


if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
