import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os


# ============================================================
# CONFIGURATION
# ============================================================

SCORE_FILE = "guessing_game_scores.json"

# Game variables
secret_number = 0
attempts = 0
max_attempts = 10
score = 0

min_number = 1
max_number = 100

time_left = 60
timer_id = None

game_active = False

statistics = {
    "games": 0,
    "wins": 0,
    "losses": 0,
    "best_score": 0,
    "total_attempts": 0
}


# ============================================================
# LOAD STATISTICS
# ============================================================

def load_statistics():
    global statistics

    if not os.path.exists(SCORE_FILE):
        return

    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            statistics.update(data)

    except (json.JSONDecodeError, OSError):
        statistics = {
            "games": 0,
            "wins": 0,
            "losses": 0,
            "best_score": 0,
            "total_attempts": 0
        }


# ============================================================
# SAVE STATISTICS
# ============================================================

def save_statistics():
    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as file:
            json.dump(statistics, file, indent=4)

    except OSError:
        pass


# ============================================================
# SET DIFFICULTY
# ============================================================

def set_difficulty():

    global min_number
    global max_number
    global max_attempts
    global time_left

    level = difficulty_box.get()

    if level == "Easy":

        min_number = 1
        max_number = 50
        max_attempts = 10
        time_left = 60

    elif level == "Medium":

        min_number = 1
        max_number = 100
        max_attempts = 7
        time_left = 45

    elif level == "Hard":

        min_number = 1
        max_number = 500
        max_attempts = 5
        time_left = 30

    else:

        min_number = 1
        max_number = 100
        max_attempts = 10
        time_left = 60


# ============================================================
# NEW GAME
# ============================================================

def new_game():

    global secret_number
    global attempts
    global score
    global game_active
    global time_left
    global timer_id
    global min_number
    global max_number

    # Stop previous timer
    if timer_id is not None:

        try:
            root.after_cancel(timer_id)
        except:
            pass

        timer_id = None

    # Set difficulty
    set_difficulty()

    # Custom range
    if custom_var.get():

        try:

            custom_min = int(
                min_entry.get().strip()
            )

            custom_max = int(
                max_entry.get().strip()
            )

        except ValueError:

            messagebox.showerror(
                "Invalid Range",
                "Please enter valid numbers."
            )

            return

        if custom_min >= custom_max:

            messagebox.showerror(
                "Invalid Range",
                "Minimum value must be smaller than maximum value."
            )

            return

        min_number = custom_min
        max_number = custom_max

    # Generate random number
    secret_number = random.randint(
        min_number,
        max_number
    )

    # Reset game
    attempts = 0
    score = 0
    game_active = True

    # Reset display
    guess_entry.delete(
        0,
        tk.END
    )

    result_label.config(
        text=f"Guess a number between "
             f"{min_number} and {max_number}."
    )

    hint_label.config(
        text="💡 Hint will appear here."
    )

    attempts_label.config(
        text=f"Attempts: 0 / {max_attempts}"
    )

    score_label.config(
        text="Score: 0"
    )

    timer_label.config(
        text=f"Time: {time_left}s"
    )

    guess_entry.focus()

    # Start timer
    start_timer()


# ============================================================
# START TIMER
# ============================================================

def start_timer():

    global timer_id

    if not game_active:
        return

    timer_id = root.after(
        1000,
        update_timer
    )


# ============================================================
# UPDATE TIMER
# ============================================================

def update_timer():

    global time_left
    global timer_id

    if not game_active:
        return

    time_left -= 1

    timer_label.config(
        text=f"Time: {time_left}s"
    )

    if time_left <= 0:

        timer_id = None

        game_over(
            f"⏰ Time's up!\n"
            f"The number was {secret_number}."
        )

        return

    timer_id = root.after(
        1000,
        update_timer
    )


# ============================================================
# CHECK GUESS
# ============================================================

def check_guess():

    global attempts
    global score

    if not game_active:

        messagebox.showwarning(
            "Game",
            "Please click 'New Game' first."
        )

        return

    value = guess_entry.get().strip()

    if value == "":

        messagebox.showwarning(
            "Input Error",
            "Please enter a number."
        )

        return

    try:

        guess = int(value)

    except ValueError:

        messagebox.showerror(
            "Input Error",
            "Please enter a valid whole number."
        )

        return

    # Range validation
    if guess < min_number or guess > max_number:

        messagebox.showwarning(
            "Invalid Number",
            f"Enter a number between "
            f"{min_number} and {max_number}."
        )

        return

    attempts += 1

    statistics["total_attempts"] += 1

    attempts_label.config(
        text=f"Attempts: {attempts} / {max_attempts}"
    )

    # --------------------------------------------------------
    # CORRECT
    # --------------------------------------------------------

    if guess == secret_number:

        score = calculate_score()

        result_label.config(
            text=f"🎉 Correct!\n"
                 f"The number was {secret_number}."
        )

        score_label.config(
            text=f"Score: {score}"
        )

        statistics["games"] += 1
        statistics["wins"] += 1

        if score > statistics["best_score"]:

            statistics["best_score"] = score

        save_statistics()

        end_game()

        messagebox.showinfo(
            "Congratulations!",
            f"You guessed the number correctly!\n\n"
            f"Number: {secret_number}\n"
            f"Attempts: {attempts}\n"
            f"Score: {score}"
        )

        return

    # --------------------------------------------------------
    # TOO LOW
    # --------------------------------------------------------

    if guess < secret_number:

        result_label.config(
            text="📈 Too Low!\nTry a higher number."
        )

    # --------------------------------------------------------
    # TOO HIGH
    # --------------------------------------------------------

    else:

        result_label.config(
            text="📉 Too High!\nTry a lower number."
        )

    # Show hint
    show_hint(guess)

    # Clear entry
    guess_entry.delete(
        0,
        tk.END
    )

    guess_entry.focus()

    # --------------------------------------------------------
    # MAX ATTEMPTS
    # --------------------------------------------------------

    if attempts >= max_attempts:

        game_over(
            f"❌ Game Over!\n"
            f"The number was {secret_number}."
        )


# ============================================================
# HINT SYSTEM
# ============================================================

def show_hint(guess):

    difference = abs(
        secret_number - guess
    )

    if difference <= 5:

        hint_label.config(
            text="💡 Very close!"
        )

    elif difference <= 15:

        hint_label.config(
            text="💡 You are close!"
        )

    elif secret_number % 2 == 0:

        hint_label.config(
            text="💡 Hint: The number is EVEN."
        )

    else:

        hint_label.config(
            text="💡 Hint: The number is ODD."
        )


# ============================================================
# CALCULATE SCORE
# ============================================================

def calculate_score():

    difficulty = difficulty_box.get()

    difficulty_multiplier = {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3
    }

    multiplier = difficulty_multiplier.get(
        difficulty,
        1
    )

    # Attempt points
    attempt_points = (
        max_attempts - attempts + 1
    ) * 10

    # Time points
    time_points = time_left

    # Difficulty bonus
    difficulty_bonus = (
        20 * multiplier
    )

    final_score = (
        attempt_points
        + time_points
        + difficulty_bonus
    )

    return final_score


# ============================================================
# GAME OVER
# ============================================================

def game_over(message):

    global score

    score = 0

    score_label.config(
        text="Score: 0"
    )

    result_label.config(
        text=message
    )

    statistics["games"] += 1
    statistics["losses"] += 1

    save_statistics()

    end_game()

    messagebox.showinfo(
        "Game Over",
        message
    )


# ============================================================
# END GAME
# ============================================================

def end_game():

    global game_active
    global timer_id

    game_active = False

    if timer_id is not None:

        try:
            root.after_cancel(timer_id)
        except:
            pass

        timer_id = None


# ============================================================
# SHOW STATISTICS
# ============================================================

def show_statistics():

    games = statistics["games"]

    if games > 0:

        win_rate = (
            statistics["wins"] / games
        ) * 100

    else:

        win_rate = 0

    messagebox.showinfo(
        "📊 Game Statistics",

        f"Total Games: {statistics['games']}\n\n"
        f"Wins: {statistics['wins']}\n"
        f"Losses: {statistics['losses']}\n\n"
        f"Win Rate: {win_rate:.1f}%\n\n"
        f"Best Score: {statistics['best_score']}\n"
        f"Total Attempts: {statistics['total_attempts']}"
    )


# ============================================================
# RESET STATISTICS
# ============================================================

def reset_statistics():

    global statistics

    answer = messagebox.askyesno(
        "Reset Statistics",
        "Are you sure you want to reset all statistics?"
    )

    if not answer:
        return

    statistics = {
        "games": 0,
        "wins": 0,
        "losses": 0,
        "best_score": 0,
        "total_attempts": 0
    }

    save_statistics()

    messagebox.showinfo(
        "Statistics",
        "Statistics have been reset successfully."
    )


# ============================================================
# CUSTOM RANGE
# ============================================================

def toggle_custom():

    if custom_var.get():

        min_entry.config(
            state="normal"
        )

        max_entry.config(
            state="normal"
        )

    else:

        min_entry.config(
            state="disabled"
        )

        max_entry.config(
            state="disabled"
        )


# ============================================================
# EXIT
# ============================================================

def exit_game():

    end_game()

    root.destroy()


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "Number Guessing Game"
)

root.geometry(
    "680x720"
)

root.resizable(
    False,
    False
)

root.configure(
    bg="#f2f2f2"
)


# ============================================================
# TITLE
# ============================================================

tk.Label(
    root,
    text="🎯 NUMBER GUESSING GAME",
    font=("Arial", 26, "bold"),
    bg="#f2f2f2"
).pack(
    pady=(25, 8)
)


tk.Label(
    root,
    text="Guess the hidden number before your attempts or time run out!",
    font=("Arial", 11),
    bg="#f2f2f2"
).pack()


# ============================================================
# DIFFICULTY FRAME
# ============================================================

difficulty_frame = tk.Frame(
    root,
    bg="#f2f2f2"
)

difficulty_frame.pack(
    pady=20
)


tk.Label(
    difficulty_frame,
    text="Difficulty:",
    font=("Arial", 11),
    bg="#f2f2f2"
).grid(
    row=0,
    column=0,
    padx=5
)


difficulty_box = ttk.Combobox(
    difficulty_frame,
    values=[
        "Easy",
        "Medium",
        "Hard"
    ],
    state="readonly",
    width=12
)

difficulty_box.set(
    "Medium"
)

difficulty_box.grid(
    row=0,
    column=1,
    padx=5
)


# ============================================================
# CUSTOM RANGE
# ============================================================

custom_var = tk.BooleanVar(
    value=False
)


tk.Checkbutton(
    difficulty_frame,
    text="Custom Range",
    variable=custom_var,
    command=toggle_custom,
    bg="#f2f2f2"
).grid(
    row=0,
    column=2,
    padx=15
)


tk.Label(
    difficulty_frame,
    text="Min:",
    bg="#f2f2f2"
).grid(
    row=1,
    column=0,
    pady=10
)


min_entry = tk.Entry(
    difficulty_frame,
    width=8,
    state="disabled"
)

min_entry.grid(
    row=1,
    column=1
)


tk.Label(
    difficulty_frame,
    text="Max:",
    bg="#f2f2f2"
).grid(
    row=1,
    column=2
)


max_entry = tk.Entry(
    difficulty_frame,
    width=8,
    state="disabled"
)

max_entry.grid(
    row=1,
    column=3
)


# ============================================================
# GUESS
# ============================================================

tk.Label(
    root,
    text="Enter your guess:",
    font=("Arial", 13),
    bg="#f2f2f2"
).pack(
    pady=5
)


guess_entry = tk.Entry(
    root,
    font=("Arial", 22),
    justify="center",
    width=12
)

guess_entry.pack(
    pady=10
)


# Press ENTER to check guess
guess_entry.bind(
    "<Return>",
    lambda event: check_guess()
)


# ============================================================
# CHECK BUTTON
# ============================================================

tk.Button(
    root,
    text="CHECK GUESS",
    font=("Arial", 12, "bold"),
    width=20,
    command=check_guess
).pack(
    pady=10
)


# ============================================================
# RESULT
# ============================================================

result_label = tk.Label(
    root,
    text="Click 'New Game' to start!",
    font=("Arial", 14, "bold"),
    bg="#f2f2f2",
    wraplength=600
)

result_label.pack(
    pady=15
)


# ============================================================
# HINT
# ============================================================

hint_label = tk.Label(
    root,
    text="💡 Hint will appear here.",
    font=("Arial", 11),
    bg="#f2f2f2"
)

hint_label.pack(
    pady=5
)


# ============================================================
# INFORMATION
# ============================================================

attempts_label = tk.Label(
    root,
    text="Attempts: 0",
    font=("Arial", 11),
    bg="#f2f2f2"
)

attempts_label.pack(
    pady=3
)


score_label = tk.Label(
    root,
    text="Score: 0",
    font=("Arial", 11, "bold"),
    bg="#f2f2f2"
)

score_label.pack(
    pady=3
)


timer_label = tk.Label(
    root,
    text="Time: 0s",
    font=("Arial", 11, "bold"),
    bg="#f2f2f2"
)

timer_label.pack(
    pady=3
)


# ============================================================
# BUTTONS
# ============================================================

button_frame = tk.Frame(
    root,
    bg="#f2f2f2"
)

button_frame.pack(
    pady=25
)


tk.Button(
    button_frame,
    text="🎮 New Game",
    width=14,
    command=new_game
).grid(
    row=0,
    column=0,
    padx=5,
    pady=5
)


tk.Button(
    button_frame,
    text="📊 Statistics",
    width=14,
    command=show_statistics
).grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)


tk.Button(
    button_frame,
    text="🔄 Reset Stats",
    width=14,
    command=reset_statistics
).grid(
    row=0,
    column=2,
    padx=5,
    pady=5
)


tk.Button(
    button_frame,
    text="❌ Exit",
    width=14,
    command=exit_game
).grid(
    row=0,
    column=3,
    padx=5,
    pady=5
)


# ============================================================
# LOAD DATA AND START GUI
# ============================================================

load_statistics()

guess_entry.focus()

root.mainloop()