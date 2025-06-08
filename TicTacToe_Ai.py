import tkinter as tk
from tkinter import messagebox
import mysql.connector
import datetime
import random


# Create the main window
window = tk.Tk()
window.title("Tic Tac Toe")
window.configure(bg='lightblue')  # Set background color for better UI contrast

# Frames (defined globally so they can be referenced anywhere)
# These frames represent different screens or sections of the game
start_frame = None  # The starting screen frame where players input their name and choose settings
game_frame = None  # The frame used during the game, displaying the Tic Tac Toe board and controls
results_frame = None  # The frame that displays the results after the game ends
leaderboard_frame = None  # The frame showing the leaderboard with the top player scores

# Player name entry field (defined globally for easy access across functions)
player_name_entry = None  # Input field where the player enters their name

# Difficulty selection buttons (defined globally for easy access and modification)
easy_button = None  # Button for selecting 'Easy' difficulty level
impossible_button = None  # Button for selecting 'Impossible' difficulty level

# Starting player selection buttons (defined globally for easy access and modification)
player_button = None  # Button for allowing the player to start the game
ai_button = None  # Button for allowing the AI to start the game

def hide_all_frames():
    """
    Hide all frames in the main window to ensure that only the desired frame is visible.
    
    This function is used to switch between different screens in the application. For example, 
    when navigating from the start screen to the game screen, all other frames need to be hidden 
    to provide a clean and user-friendly interface.
    
    By hiding all frames initially, the application can then display the correct frame depending 
    on the current state of the game.
    
    The function also uses conditionals to verify if the frames have been initialized before attempting to hide them. 
    This prevents potential errors due to uninitialized frames, ensuring smoother navigation between screens.
    """
    # Check if start_frame exists and hide it if it does
    if start_frame:
        start_frame.pack_forget()  # Hides the start frame to make room for other frames
    # Check if game_frame exists and hide it if it does
    if game_frame:
        game_frame.pack_forget()  # Hides the game frame, ensuring other frames can be displayed
    # Check if results_frame exists and hide it if it does
    if results_frame:
        results_frame.pack_forget()  # Hides the results frame to prepare for another frame
    # Check if leaderboard_frame exists and hide it if it does
    if leaderboard_frame:
        leaderboard_frame.pack_forget()  # Hides the leaderboard frame, allowing another frame to take focus

        
# Global variable to keep track of the current player
current_player_name = None  # Stores the name of the player currently using the game

# Flag to indicate whether the user is logged out or logged in
logged_out = True  # Default to logged out state initially. True means no player is logged in.

def show_leaderboard():  
    """
This function displays the leaderboard screen in the application. It hides all other frames first,
then creates and packs the leaderboard UI components, including a header with navigation buttons, 
a list of top players, and optionally the rank of the currently logged-in player.

It interacts with the database to fetch leaderboard data, and ensures that the information is presented
in a user-friendly way, with features such as scrollability for easy navigation.
"""
    global leaderboard_frame, current_player_name, logged_out

    # Hide all other frames before showing the leaderboard
    hide_all_frames()

    # Create a new frame for the leaderboard
    leaderboard_frame = tk.Frame(window, bg='#2C1D4A')
    leaderboard_frame.pack(expand=True, fill='both')

    # Header setup for navigation buttons
    header_frame = tk.Frame(leaderboard_frame, bg='#53257F', pady=10)
    header_frame.pack(fill='x')

    # Back button to return to the homepage
    back_button = tk.Button(header_frame, text="Back to Homepage", font=('Arial', 16),
                            command=show_start_screen, bg='#FF5A5F', fg='white', padx=10, pady=5)
    back_button.pack(side='left', padx=10)

    # Logout button to log the user out
    logout_button = tk.Button(header_frame, text="Logout", font=('Arial', 16),
                              command=log_out, bg='red', fg='white', padx=10, pady=5)
    logout_button.pack(side='right', padx=10)

    # Title label for the leaderboard
    title_label = tk.Label(header_frame, text="🏆 Leaderboard 🏆", font=('Arial', 28, 'bold'), bg='#53257F', fg='white')
    title_label.pack(side='left', expand=True)

    # Create a canvas for the leaderboard to enable scrolling if needed
    leaderboard_canvas = tk.Canvas(leaderboard_frame, bg='#2C1D4A', highlightthickness=0)
    leaderboard_canvas.pack(expand=True, fill="both")

    # Create a frame centered in the canvas for content
    centered_frame = tk.Frame(leaderboard_canvas, bg='#2C1D4A')
    leaderboard_canvas.create_window((window.winfo_screenwidth() // 2, 0), window=centered_frame, anchor="n")

    # Container for the leaderboard list
    leaderboard_list = tk.Frame(centered_frame, bg='#2C1D4A')
    leaderboard_list.pack(pady=20, padx=50)  # Padding to center horizontally

    # Scrollbar for the leaderboard
    scrollbar = tk.Scrollbar(leaderboard_frame, orient="vertical", command=leaderboard_canvas.yview)
    leaderboard_canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Add headers to the leaderboard table
    headers = ["Rank", "Name", "Time Taken"]
    for col, header in enumerate(headers):
        tk.Label(leaderboard_list, text=header, font=('Arial', 18, 'bold'),
                 bg='#4A3F6E', fg='white', padx=20, pady=10).grid(row=0, column=col, sticky='nsew', padx=5, pady=5)

    try:
        # Establish a connection to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mohamed@123",
            database="tictactoe"
        )
        cursor = conn.cursor()

        # Fetch the top 5 players based on the lowest time taken
        cursor.execute("""
            SELECT 
                player_name, 
                time_taken, 
                (SELECT COUNT(*) + 1 
                 FROM leaderboard AS t2 
                 WHERE t2.time_taken < t1.time_taken) AS player_rank
            FROM leaderboard AS t1
            ORDER BY time_taken ASC
            LIMIT 5;
        """)
        top_5_rows = cursor.fetchall()

        # Define colors for the top 3 ranks (gold, silver, bronze) and white for others
        colors = ['#FFD700', '#C0C0C0', '#CD7F32'] + ['white'] * (len(top_5_rows) - 3)

        # Display each player in the leaderboard
        for i, (name, time_taken, rank) in enumerate(top_5_rows):
            # Format rank with appropriate suffix (st, nd, rd, th)
            rank_text = f"{rank}{'st' if rank == 1 else 'nd' if rank == 2 else 'rd' if rank == 3 else 'th'}"
            font_color = colors[i]

            # Add rank, player name, and time taken to the table
            tk.Label(leaderboard_list, text=rank_text, font=('Arial', 18),
                     bg='#2C1D4A', fg=font_color, padx=10, pady=10).grid(row=i + 1, column=0, sticky='nsew', padx=5, pady=5)

            tk.Label(leaderboard_list, text=name, font=('Arial', 18),
                     bg='#2C1D4A', fg=font_color, padx=10, pady=10).grid(row=i + 1, column=1, sticky='nsew', padx=5, pady=5)

            tk.Label(leaderboard_list, text=f"{time_taken} seconds", font=('Arial', 18),
                     bg='#2C1D4A', fg=font_color, padx=10, pady=10).grid(row=i + 1, column=2, sticky='nsew', padx=5, pady=5)

        # Show "Your Rank" section if the user is logged in and has recent data
        if current_player_name and not logged_out:
            cursor.execute("""
                SELECT 
                    player_name, 
                    time_taken, 
                    (SELECT COUNT(*) + 1 
                     FROM leaderboard AS t2 
                     WHERE t2.time_taken < t1.time_taken) AS player_rank
                FROM leaderboard AS t1
                WHERE player_name = %s
            """, (current_player_name,))
            recent_player = cursor.fetchone()
            
            if recent_player:
                name, time_taken, rank = recent_player

                # Display a label indicating the user's rank
                tk.Label(leaderboard_list, text="Your Rank", font=('Arial', 18, 'bold'), bg='#FF5A5F', fg='white').grid(
                    row=len(top_5_rows) + 2, column=0, columnspan=3, pady=10)
                
                # Display user's rank, name, and time taken
                rank_text = f"{rank}{'st' if rank == 1 else 'nd' if rank == 2 else 'rd' if rank == 3 else 'th'}"
                tk.Label(leaderboard_list, text=rank_text, font=('Arial', 18),
                         bg='#2C1D4A', fg='green', padx=10, pady=10).grid(row=len(top_5_rows) + 3, column=0, sticky='nsew', padx=5, pady=5)

                tk.Label(leaderboard_list, text=name, font=('Arial', 18),
                         bg='#2C1D4A', fg='green', padx=10, pady=10).grid(row=len(top_5_rows) + 3, column=1, sticky='nsew', padx=5, pady=5)

                tk.Label(leaderboard_list, text=f"{time_taken} seconds", font=('Arial', 18),
                         bg='#2C1D4A', fg='green', padx=10, pady=10).grid(row=len(top_5_rows) + 3, column=2, sticky='nsew', padx=5, pady=5)

    except mysql.connector.Error as err:
        # Show an error message if there's an issue with the database
        messagebox.showerror("Database Error", f"Error fetching leaderboard data: {err}")

    finally:
        # Close the cursor and connection to the database
        cursor.close()
        conn.close()

        # Update the scrollable region of the leaderboard canvas
        leaderboard_list.update_idletasks()
        leaderboard_canvas.config(scrollregion=leaderboard_canvas.bbox("all"))

# Function to handle logout and hide the recent rank from the leaderboard
def logout_and_hide_rank():
    """
    This function is responsible for handling user logout actions. It sets the logged_out flag to True, 
    indicating that no player is currently logged in. This is used to update the UI accordingly, such as 
    hiding the player's recent rank from the leaderboard.

    After logging out, it refreshes the leaderboard to reflect that the user is no longer logged in, 
    thereby hiding personalized ranking information.
    """
    global logged_out
    logged_out = True  # Set logged out status to true
    show_leaderboard()  # Refresh leaderboard to hide the recent player's rank


# Constants for players
PLAYER = 'X'  # Constant to represent the human player in the game (usually 'X')
AI = 'O'      # Constant to represent the AI opponent in the game (usually 'O')

# Variables to track the start time of the game, number of games played, and game timer label
game_start_time = None  # Variable to store the time when the game starts for tracking game duration
games_played = 0        # Counter to track the total number of games played
total_time = 0          # Tracks total time spent across all games to help calculate average playtime

# Initialize the board as a list of empty strings
board = ['' for _ in range(9)]  # Initialize a 3x3 board with empty strings to represent an empty game board

# Variables to store player choices and game difficulty
difficulty = None      # Variable to hold the current difficulty setting chosen by the player (e.g., easy, medium, hard)
player_starts = None   # Boolean or flag to indicate if the player starts first in the game
player_name = "Player" # Default player name to "Player" in case no specific name is provided

# Variables to track scores
player_score = 0  # Score counter for the human player
ai_score = 0      # Score counter for the AI opponent

# Start screen frame function
def reset_homepage_fields():
    """
    Resets selections and the name entry on the homepage.

    This function is used to reset all fields on the homepage of the game. This includes:
    - Clearing the player name entry field.
    - Resetting the difficulty level selection.
    - Resetting who starts the game (either the player or the AI).
    
    It ensures that when the player navigates back to the start screen or restarts, all previous
    selections are cleared, providing a fresh and consistent user experience.
    """

    global difficulty, player_starts

    # Reset the player name entry field
    if player_name_entry:
        player_name_entry.delete(0, tk.END)  # Clear any text in the player name entry box

    # Reset difficulty selection buttons if they exist
    if easy_button:
        easy_button.config(bg='SystemButtonFace')  # Reset the background color to default (unselected)
    if impossible_button:
        impossible_button.config(bg='SystemButtonFace')  # Reset the background color to default (unselected)

    # Reset starting player selection buttons if they exist
    if player_button:
        player_button.config(bg='SystemButtonFace')  # Reset the background color to default (unselected)
    if ai_button:
        ai_button.config(bg='SystemButtonFace')  # Reset the background color to default (unselected)

    # Reset difficulty and player start choice variables
    difficulty = None  # Clear the difficulty selection
    player_starts = None  # Clear the starting player selection

def show_start_screen():
    """
    Displays the start screen of the game.

    This function is responsible for creating and showing the start screen of the game. It initializes
    various components such as the player name entry field, difficulty selection buttons, and buttons 
    for selecting who starts the game. It also provides options to start the game or view the leaderboard.

    The function ensures that the homepage is reset every time it is displayed to give the player a fresh
    experience, and only creates the start frame if it does not already exist, to avoid redundant UI creation.
    """

    global start_frame, easy_button, impossible_button, player_button, ai_button, player_name_entry

    # Hide all other frames to ensure only the start screen is visible
    hide_all_frames()

    # Reset all fields (e.g., player name, difficulty, and starter options) to default state
    reset_homepage_fields()

    # Create and pack the start screen frame if not already created
    if not start_frame:
        # Main start screen frame setup
        start_frame = tk.Frame(window, bg='lightblue')
        
        # Player Name Entry Section
        # Frame for the player name input
        name_frame = tk.Frame(start_frame, bg='lightblue')
        name_frame.pack(pady=10)
        
        # Label prompting the player to enter their name
        tk.Label(name_frame, text="Enter Player Name:", font=('Arial', 16), bg='lightblue').pack()
        
        # Entry field for player name input
        player_name_entry = tk.Entry(name_frame, font=('Arial', 16))
        player_name_entry.pack(pady=5)

        # Difficulty Selection Section
        # Frame for difficulty selection buttons
        difficulty_frame = tk.Frame(start_frame, bg='lightblue')
        difficulty_frame.pack(pady=20)
        
        # Label prompting player to choose the game difficulty level
        tk.Label(difficulty_frame, text="Select Difficulty:", font=('Arial', 16), bg='lightblue').pack()
        
        # Button to select "Easy" difficulty level
        easy_button = tk.Button(difficulty_frame, text="Easy", font=('Arial', 14), width=10, command=lambda: set_difficulty('easy'))
        easy_button.pack(pady=5)
        
        # Button to select "Impossible" difficulty level
        impossible_button = tk.Button(difficulty_frame, text="Impossible", font=('Arial', 14), width=10, command=lambda: set_difficulty('impossible'))
        impossible_button.pack(pady=5)

        # Starting Player Section
        # Frame for choosing who starts the game (Player or AI)
        start_choice_frame = tk.Frame(start_frame, bg='lightblue')
        start_choice_frame.pack(pady=20)
        
        # Label prompting player to select who starts first
        tk.Label(start_choice_frame, text="Who Starts?", font=('Arial', 16), bg='lightblue').pack()
        
        # Button to select the player as the starter
        player_button = tk.Button(start_choice_frame, text="Player", font=('Arial', 14), width=10, command=lambda: set_start_options(True))
        player_button.pack(pady=5)
        
        # Button to select the AI as the starter
        ai_button = tk.Button(start_choice_frame, text="AI", font=('Arial', 14), width=10, command=lambda: set_start_options(False))
        ai_button.pack(pady=5)

        # Start Game Button
        # Button to start the game after all selections are made
        start_game_button = tk.Button(start_frame, text="Start Game", font=('Arial', 16), width=12, command=save_player_name)
        start_game_button.pack(pady=20)

        # Leaderboard Button
        # Button to navigate to the leaderboard screen
        leaderboard_button = tk.Button(start_frame, text="Leaderboard", font=('Arial', 16), width=12, command=show_leaderboard)
        leaderboard_button.pack(pady=10)

        # Close Game Instruction
        # Label displaying instructions on how to exit the game
        close_instruction = tk.Label(start_frame, text="Press ESC to close the game", font=('Arial', 12), bg='lightblue')
        close_instruction.pack(pady=10)

    # Pack the start_frame to make it visible
    start_frame.pack(expand=True, fill='both')

def set_difficulty(selected_difficulty):
    """
    Sets the difficulty for the game and visually highlights the selected button.

    Args:
        selected_difficulty (str): The difficulty level chosen by the player, either 'easy' or 'impossible'.
    
    This function updates the global difficulty variable with the player's selection and provides
    a visual indication of the selected difficulty by changing the button color. The selected
    button's background color is changed to green to show it is active, while the unselected button
    reverts to its default state.
    """
    global difficulty, easy_button, impossible_button

    # Set the global difficulty variable to the selected value
    difficulty = selected_difficulty

    # Highlight the selected button by changing its background color to green
    if selected_difficulty == 'easy':
        easy_button.config(bg='green')  # Mark 'Easy' button as selected
        impossible_button.config(bg='SystemButtonFace')  # Reset 'Impossible' button to default color
    elif selected_difficulty == 'impossible':
        impossible_button.config(bg='red')  # Mark 'Impossible' button as selected
        easy_button.config(bg='SystemButtonFace')  # Reset 'Easy' button to default color


def set_start_options(player_starts_choice):
    """
    Sets who starts the game (player or AI) and visually highlights the selected button.

    Args:
        player_starts_choice (bool): Boolean value indicating who starts the game. 
                                     True if the player starts, False if the AI starts.

    This function updates the global player_starts variable based on the player's selection and 
    highlights the selected button. The button representing the starting player is highlighted in green, 
    while the other button is reset to its default color.
    """
    global player_starts, player_button, ai_button

    # Set the global player_starts variable to indicate whether the player starts or not
    player_starts = player_starts_choice

    # Highlight the selected button by changing its background color to green
    if player_starts_choice:
        player_button.config(bg='Orange')  # Mark 'Player' button as selected
        ai_button.config(bg='SystemButtonFace')  # Reset 'AI' button to default color
    else:
        ai_button.config(bg='yellow')  # Mark 'AI' button as selected
        player_button.config(bg='SystemButtonFace')  # Reset 'Player' button to default color

def save_player_name():
    """
    Saves the player's name, ensuring it is unique, and sets it for the current game session.

    This function handles saving the player's name for the game, ensuring that the name is unique by 
    checking against existing names in the database. If the entered name is not unique, a suffix is appended 
    to create a unique identifier. It then stores this unique name and initiates the game.

    It interacts with the database to check for name uniqueness and updates global variables to track the current 
    player throughout the game session.
    """
    global player_name, player_name_entry, current_player_name, logged_out

    # Retrieve the player's name from the entry field or default to "Player" if none is entered
    entered_name = player_name_entry.get().strip() or "Player"  # Default to "Player" if no name is provided

    # Connect to the database to ensure uniqueness of the player's name
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mohamed@123",
            database="tictactoe"
        )
        cursor = conn.cursor()

        # Check if the entered name already exists in the leaderboard and create a unique name if necessary
        unique_name = entered_name
        count = 1
        while True:
            cursor.execute("SELECT player_name FROM leaderboard WHERE player_name = %s", (unique_name,))
            results = cursor.fetchall()

            if results:  # If the name already exists, append a number to make it unique
                unique_name = f"{entered_name}_{count}"
                count += 1
            else:
                break

        # Set the unique player name for the session
        player_name = unique_name  # Assign the final unique name to the global player_name variable
        current_player_name = player_name  # Update the global current_player_name for tracking purposes
        logged_out = False  # Set logged_out to False to indicate that the player is now logged in

    except mysql.connector.Error as err:
        # Show an error message if there is an issue with connecting to the database or checking the name
        messagebox.showerror("Database Error", f"Error checking player name uniqueness: {err}")

    finally:
        # Always close the cursor and connection to prevent database locks or resource leaks
        cursor.close()
        conn.close()

    # Start the game with the unique player name
    start_game()

def log_out():
    """
    Logs the user out, automatically saves progress only if a game was played, waits 10 milliseconds, and then returns to the homepage.

    This function checks if any game has been played before logging out. If so, it automatically saves the player's progress
    to the leaderboard. Then it resets all player-related data, updates the UI labels to reflect these changes, and navigates
    back to the homepage.
    """
    global player_name, player_score, ai_score, games_played, total_time, logged_out, current_player_name

    # Check if the player name is set and at least one game has been played
    if player_name != "Player" and games_played > 0:
        # Automatically save the player's progress to the leaderboard
        time_taken = calculate_game_time()  # Calculate the time taken for the current session
        save_to_leaderboard(player_name, player_score, time_taken, games_played)  # Save progress to the leaderboard

    # Reset player-related data
    player_name = "Player"  # Set the player name to the default value ("Player")
    player_score = 0  # Reset the player's score to zero
    ai_score = 0  # Reset the AI's score to zero
    games_played = 0  # Reset the number of games played to zero
    total_time = 0  # Reset the total time spent on games
    current_player_name = None  # Clear the current player name for tracking purposes
    logged_out = True  # Mark the player as logged out

    # Update displayed labels to reflect the reset values
    player_score_label.config(text=f"{player_name}: {player_score}")  # Update player score label
    ai_score_label.config(text="AI: 0")  # Update AI score label to show zero
    games_played_label.config(text="Games Played: 0/3")  # Update games played label to reset count
    timer_label.config(text="Total Time: 00:00")  # Reset the timer label to show zero time spent

    # Redirect to the leaderboard screen first
    show_leaderboard()

    # After 10 milliseconds, go back to the start screen
    window.after(10, show_start_screen)



# Bind ESC key to close the game
# - Allows the user to close the game by pressing the ESC key.
# - Enhances convenience for exiting the application quickly.
window.bind('<Escape>', lambda event: window.destroy())

# Set the window to fullscreen
# - Provides an immersive experience by setting the window to fullscreen mode.
window.attributes('-fullscreen', True)

# Button list to access buttons by index
# - Initializes an empty list to store the buttons representing the game board.
# - This makes it easier to access buttons by index.
buttons = []

# Main game frame
# - Creates the main frame to hold all sub-frames of the game interface.
# - Background color is set to 'lightblue' for a cohesive look.
game_frame = tk.Frame(window, bg='lightblue')

# Separate frames for different sections of the game interface
# - Frame for the game board (9 buttons representing the grid)
board_frame = tk.Frame(game_frame, bg='lightblue') 

# - Frame for control buttons like "Back" and "Log Out"
control_frame = tk.Frame(game_frame, bg='lightblue')

# - Frame for score and game-related labels
score_frame = tk.Frame(game_frame, bg='lightblue')

# Arrange frames within the main game_frame
# - Frames are positioned within the game_frame using a grid layout.
# - Ensures the board, controls, and scores are visually distinct and accessible.
board_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
control_frame.grid(row=1, column=0, columnspan=3, pady=10)
score_frame.grid(row=2, column=0, columnspan=3, pady=10)

# Create the grid of buttons for the game board within board_frame
# - Creates 9 buttons to represent the 3x3 Tic-Tac-Toe board.
# - Each button is added to the board_frame in a 3x3 layout using grid positioning.
# - Buttons are stored in the `buttons` list for easy access by index.
# - `command=lambda i=i: player_move(i)` allows tracking of the specific button clicked.
for i in range(9):
    button = tk.Button(board_frame, text='', font=('Arial', 20), width=5, height=2,
                       command=lambda i=i: player_move(i))
    button.grid(row=i // 3, column=i % 3, padx=5, pady=5)
    buttons.append(button)

# Control buttons
# - "Back" button: Allows the player to return to the start screen.
reset_button = tk.Button(control_frame, text="Back", font=('Arial', 12), command=show_start_screen)
reset_button.grid(row=0, column=0, padx=5, pady=5)

# - "Log Out" button: Logs the player out, saves progress if necessary, and returns to the start screen.
log_out_button = tk.Button(control_frame, text="Log Out", font=('Arial', 12), command=log_out)
log_out_button.grid(row=0, column=1, padx=5, pady=5)

# Score, timer, and games played labels in the score_frame
# - Displays the player's score, showing the player name and current score.
# - Dynamically updated during the game.
player_score_label = tk.Label(score_frame, text=f"{player_name}: {player_score}", font=('Arial', 12), bg='lightblue')
player_score_label.grid(row=0, column=0, padx=5)

# - Displays the AI's score to track the player's performance against the AI.
ai_score_label = tk.Label(score_frame, text=f"AI: {ai_score}", font=('Arial', 12), bg='lightblue')
ai_score_label.grid(row=0, column=1, padx=5)

# - Displays the number of games played in the current session.
# - Provides a sense of progress, with a maximum of 3 games.
games_played_label = tk.Label(score_frame, text=f"Games Played: {games_played}/3", font=('Arial', 12), bg='lightblue')
games_played_label.grid(row=0, column=2, padx=5)


# Function to update scores and track games played
def update_score(winner):
    """
    Updates the score based on the winner of the game, keeps track of games played, 
    and performs actions accordingly like displaying messages, updating labels, and starting a new session.
    """
    global player_score, ai_score, games_played, timer_running, total_time

    # Update scores based on the winner of the current round
    if winner == "player":
        player_score += 1  # Increment player's score
        games_played += 1  # Increment number of games played by the player
        games_played_label.config(text=f"Games Played: {games_played}/3")  # Update games played label
        messagebox.showinfo("Game Over", f"{player_name} has won this round!")  # Display a message indicating the player won

    elif winner == "ai":
        ai_score += 1  # Increment AI's score

        # Decrement the games_played if AI wins, but ensure it does not drop below zero
        if games_played > 0:
            games_played -= 1
        games_played_label.config(text=f"Games Played: {games_played}/3")  # Update games played label
        messagebox.showinfo("Game Over", "AI has won this round!")  # Display a message indicating the AI won

    elif winner == "draw":
        # Handle a draw situation
        messagebox.showinfo("Game Over", "It's a draw!")  # Display a message indicating the game is a draw

    # Update score labels after each game
    # - Reflect the latest score changes for both the player and AI
    player_score_label.config(text=f"{player_name}: {player_score}")
    ai_score_label.config(text=f"AI: {ai_score}")

    # If the player has won 3 rounds, handle the end of the session
    if games_played == 3:
        # Stop the timer and calculate the total time taken for the session
        timer_running = False  # Stop the timer
        total_time = calculate_game_time()  # Calculate and store the total time for the session

        # Show results in a new frame instead of a popup for a better user experience
        show_results_screen()

        # Save the current session results to the leaderboard for tracking player progress
        save_to_leaderboard(player_name, player_score, total_time)

        # Reset all necessary variables for a new session after leaderboard update
        reset_for_new_session()
    else:
        # Reset the board for the next game round to continue playing
        reset_board()
        
        # If AI starts, initiate AI's move
        if not player_starts:
            ai_turn()

# Function to save the player's performance to the leaderboard in the database
def save_to_leaderboard(player_name, score, time_taken, games_played=3):
    """
    Save the player's name, score, time taken, and games played to the leaderboard in the database.
    Ensures that the player name is unique before saving.
    """
    try:
        # Establish a connection to the MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mohamed@123",
            database="tictactoe"
        )
        cursor = conn.cursor()

        # Ensure that the player name is unique
        # - If the player's name already exists in the leaderboard, append a suffix to make it unique.
        unique_name = player_name
        count = 1
        while True:
            cursor.execute("SELECT player_name FROM leaderboard WHERE player_name = %s", (unique_name,))
            result = cursor.fetchone()
            if result:
                # If the name exists, create a new unique name by appending a suffix (e.g., Player_1, Player_2, etc.)
                unique_name = f"{player_name}_{count}"
                count += 1
            else:
                # Found a unique name that doesn't exist in the leaderboard
                break

        # Insert the player's information into the leaderboard
        cursor.execute("""
            INSERT INTO leaderboard (player_name, score, time_taken, games_played)
            VALUES (%s, %s, %s, %s)
        """, (unique_name, score, time_taken, games_played))
        
        # Commit the transaction to save the changes to the database
        conn.commit()

    except mysql.connector.Error as err:
        # Handle database errors
        # - Suppress duplicate entry errors (error code 1062), as unique names are being generated.
        # - Show other errors to the user to notify of potential issues with the database.
        if err.errno != 1062:
            messagebox.showerror("Database Error", f"Error saving to leaderboard: {err}")

    finally:
        # Ensure that the cursor and database connection are closed properly
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Function to show results after 3 games are completed
def show_results_screen():
    """
    Replaces the main game window with a results screen showing game statistics.
    Displays the total time taken, allows viewing the leaderboard, and provides a logout option.
    """
    global results_frame

    # Hide the current game frame to transition to the results screen
    # - Ensures the main game interface is not visible while displaying the results.
    game_frame.pack_forget()

    # Initialize the results_frame if it does not already exist
    # - The frame is used to display the results after the player completes 3 games.
    if results_frame is None:
        results_frame = tk.Frame(window, bg='lightblue')

    # Clear any previous content in results_frame to ensure it is clean before displaying new information
    for widget in results_frame.winfo_children():
        widget.destroy()

    # Pack and display the results frame
    # - Set the frame to expand fully within the window for better visual coverage.
    results_frame.pack(expand=True, fill='both')

    # Display results header to indicate that 3 games have been completed
    tk.Label(results_frame, text="3 games have been completed.", font=('Arial', 16), bg='lightblue').pack(pady=10)
    
    # Display total time taken for the session
    # - Provides the player with the statistics of their gameplay.
    tk.Label(results_frame, text=f"Total Time: {total_time:.2f} seconds.", font=('Arial', 14), bg='lightblue').pack(pady=10)
    
    # Prompt to check the leaderboard after completing 3 games
    tk.Label(results_frame, text="Please check the leaderboard.", font=('Arial', 14), bg='lightblue').pack(pady=10)

    # Button to log out
    # - Allows the player to log out from the results screen.
    logout_button = tk.Button(results_frame, text="Log Out", font=('Arial', 14), command=log_out)
    logout_button.pack(pady=10)

    # Button to view the leaderboard
    # - Clicking this button hides the results frame and shows the leaderboard screen.
    leaderboard_button = tk.Button(results_frame, text="View Leaderboard", font=('Arial', 14), 
                                   command=lambda: [results_frame.pack_forget(), show_leaderboard()])
    leaderboard_button.pack(pady=10)

    # Instructions to close the game using the ESC key
    # - Provides the player with a quick way to exit the game.
    tk.Label(results_frame, text="Press ESC to close the game", font=('Arial', 12), bg='lightblue').pack(pady=10)

# Function to reset the board and prepare for a new game
def reset_board():
    """
    Resets the board to its initial empty state, preparing for a new game.
    Clears all board cells and enables all buttons for the next game round.
    """
    global board

    # Reset the game board to an empty state
    # - Initializes the board list with empty strings to represent an empty 3x3 Tic-Tac-Toe grid.
    board = ['' for _ in range(9)]

    # Update the button states to reflect the empty board
    # - Clears the text in all buttons and sets them to a normal (enabled) state.
    for button in buttons:
        button.config(text='', state=tk.NORMAL)

# Function to reset all variables and prepare for a new session
def reset_for_new_session():
    """
    Reset variables for a new session after 3 games are completed.
    Resets scores, games played count, timer, and game board to start a fresh new session.
    """
    global player_score, ai_score, games_played, total_time, game_start_time

    # Reset scores, games played count, and the timer
    # - Start the session anew by setting all counters and time-related variables back to zero.
    games_played = 0
    player_score = 0
    ai_score = 0
    total_time = 0
    game_start_time = None  # Clear the start time to indicate a fresh session

    # Update the displayed labels to reflect the reset state
    # - Ensures all score-related UI elements are updated to show zero scores and progress.
    games_played_label.config(text=f"Games Played: {games_played}/3")
    player_score_label.config(text=f"{player_name}: {player_score}")
    ai_score_label.config(text=f"AI: {ai_score}")
    timer_label.config(text="Total Time: 00:00")

    # Reset the game board to an initial state for the new session
    reset_board()

# Function to check if a player has won the game
def check_winner(player):
    """
    Checks if the given player has won the game.
    Args:
        player (str): The symbol representing the player ('X' or 'O').

    Returns:
        bool: True if the player has a winning combination, False otherwise.
    """
    # Define all possible winning combinations for a 3x3 Tic-Tac-Toe board
    # - Includes rows, columns, and diagonals.
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]

    # Check each winning combination to determine if the player has won
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] == player:
            return True  # Return True if the player has three symbols in a row

    # Return False if no winning combination is found
    return False

# Function to calculate the time taken for the game
def calculate_game_time():
    """Calculates the time taken for the game in seconds and updates the start time for continuous tracking."""
    global game_start_time

    # Check if the game start time is set
    if game_start_time is None:
        return 0  # Return 0 if the game start time is not available

    # Record the current time as the end time
    end_time = datetime.datetime.now()

    # Calculate the difference between the start and end time in seconds
    time_taken = (end_time - game_start_time).total_seconds()

    # Update the start time for ongoing time tracking
    game_start_time = end_time

    # Return the total time taken
    return time_taken

# Function to handle the player's move
def player_move(index):
    """Handles the player's move by updating the board, checking for a winner or a draw."""
    
    # Ensure the cell is empty and there is no winner before proceeding
    if board[index] == '' and not check_winner(PLAYER) and not check_winner(AI):
        # Update the board with the player's move
        board[index] = PLAYER
        # Update the button text to reflect the player's move and disable the button
        buttons[index].config(text=PLAYER, state=tk.DISABLED)

        # Check if the player won after their move
        if check_winner(PLAYER):
            # Update the score to reflect the player's win
            update_score("player")
            return

        # Check for a draw if no empty cells remain
        if '' not in board:
            # Update the score to reflect a draw
            update_score("draw")
            return

        # Let AI make a move if the game is still ongoing
        ai_turn()

# Function for AI's move based on selected difficulty
def ai_turn():
    """Handles the AI's move based on the selected difficulty level."""

    # Choose AI's move based on the difficulty selected by the player
    if difficulty == 'easy':
        move = ai_move_easy()  # AI selects a random empty cell for easy difficulty
    else:
        move = find_best_move()  # AI uses minimax to find the best move for higher difficulty

    # If a valid move is found, update the board and disable the button
    if move != -1:
        board[move] = AI
        buttons[move].config(text=AI, state=tk.DISABLED)

        # Check if AI won after the move
        if check_winner(AI):
            # Update the score to reflect AI's win
            update_score("ai")
            return

        # If no empty cells are left, declare a draw
        if '' not in board:
            update_score("draw")

# Function for easy AI move (random choice)
def ai_move_easy():
    """AI move for easy difficulty - randomly selects an empty cell."""
    
    # Create a list of all empty cells
    empty_spots = [i for i in range(9) if board[i] == '']

    # Return a random choice from empty cells if available
    if empty_spots:
        return random.choice(empty_spots)
    return -1  # Return -1 if no moves are possible

# Helper function to evaluate the board for minimax (AI) purposes
def evaluate():
    """Evaluates the board and returns a score based on the game result."""

    # Check if AI has won and return +10 if true
    if check_winner(AI):
        return 10
    # Check if the player has won and return -10 if true
    elif check_winner(PLAYER):
        return -10
    # Return 0 for a draw or if the game is ongoing
    return 0

# Minimax algorithm for AI to find the best move
def minimax(is_maximizing):
    """Minimax algorithm to find the best move for the AI."""

    # Evaluate the board to determine if the game has ended
    score = evaluate()

    # Return score if a winning or losing condition has been reached
    if score == 10 or score == -10:
        return score

    # If no cells are empty, return a draw score of 0
    if '' not in board:
        return 0

    if is_maximizing:
        # Maximize AI's score
        best_score = -1000
        for i in range(9):
            if board[i] == '':
                board[i] = AI  # Make a hypothetical move
                best_score = max(best_score, minimax(False))  # Recursively find the best score
                board[i] = ''  # Undo the move
        return best_score
    else:
        # Minimize player's score
        best_score = 1000
        for i in range(9):
            if board[i] == '':
                board[i] = PLAYER  # Make a hypothetical move
                best_score = min(best_score, minimax(True))  # Recursively find the best score
                board[i] = ''  # Undo the move
        return best_score

# Function to find the best move for AI using minimax
def find_best_move():
    """Finds the best move for the AI using the Minimax algorithm."""

    best_val = -1000  # Initialize the best score for AI
    best_move = -1  # Initialize the best move as invalid (-1)

    # Iterate through all cells to evaluate the best possible move
    for i in range(9):
        if board[i] == '':  # Check if the cell is empty
            board[i] = AI  # Make a hypothetical move
            move_val = minimax(False)  # Evaluate the move using minimax
            board[i] = ''  # Undo the move

            # Update the best move if the current move value is higher
            if move_val > best_val:
                best_move = i
                best_val = move_val

    # Return the index of the best move
    return best_move

# Function to start the game
def start_game():
    """Initializes the game by recording start time, starting timer, and hiding the start screen."""
    global game_start_time, timer_running

    # Ensure the player name is set before starting
    if not player_name:
        messagebox.showerror("Error", "Player name is not set. Please enter a valid name.")
        return

    # Set the game start time if not already set
    if game_start_time is None:
        game_start_time = datetime.datetime.now()  # Record the start time

    # Start the game timer
    timer_running = True
    update_timer()  # Begin the timer update loop

    # Hide the start screen and show the game frame
    start_frame.pack_forget()
    game_frame.pack(expand=True)

    # Reset the board for a new game
    reset_board()

    # If AI starts, let AI make the first move
    if not player_starts:
        ai_turn()

# Function to update the timer every second
def update_timer():
    """Updates the timer label with the time elapsed since the game started."""

    if timer_running and game_start_time is not None:
        # Calculate the elapsed time
        elapsed_time = datetime.datetime.now() - game_start_time
        seconds = elapsed_time.total_seconds()

        # Format the time in MM:SS format
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        time_string = f"Total Time: {minutes:02}:{seconds:02}"

        # Update the timer label
        timer_label.config(text=time_string)

        # Re-call this function after 1 second for continuous update
        window.after(1000, update_timer)

# Adding timer label to the game frame
# - Displays the total time elapsed in the current session
timer_label = tk.Label(game_frame, text="Total Time: 00:00", font=('Arial', 12), bg='lightblue')
timer_label.grid(row=3, column=1, columnspan=1)  # Position the timer in the game frame

# Show the start screen initially
# - Display the initial start screen when the application runs
show_start_screen()

# Run the Tkinter event loop
# - Starts the application's main event loop for user interaction
window.mainloop()