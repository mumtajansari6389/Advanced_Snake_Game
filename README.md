# Professional Advanced Snake Game

A modern, polished, and professional take on the classic Snake game, built using Python and Pygame.

## Features
- **Modern UI/UX**: Hoverable buttons, clean typography, smooth transitions, and state management.
- **Level-wise Progression**: Features 5 unique levels. Each level introduces different speeds, distinct color themes, and new obstacle layouts (borders, crosses, mazes).
- **Settings System**: Persistent configuration for Sound, Music, and High Score using JSON.
- **Polished Animations**: Glowing food, dynamic particle effects on eating, fading level transitions, and subtle snake segment coloring.
- **Robust Architecture**: Separated into cohesive modules (`game.py`, `ui.py`, `levels.py`, `settings.py`).

## Project Structure
```text
Advanced_Snake_Game/
│
├── main.py        # Game entry point
├── game.py        # Core game loop and state management
├── ui.py          # Reusable UI components (Buttons, Panels)
├── levels.py      # Level definitions and obstacle generation
├── settings.py    # Configuration and high-score management
├── assets/        # Sounds and Images
└── README.md      # Project documentation
```

## How to Run
1. Ensure you have Python installed.
2. Install Pygame: `pip install pygame`
3. Run the game: `python main.py`

## Controls
- **Arrow Keys**: Move the snake (Up, Down, Left, Right).
- **Escape / P**: Pause the game.
- **F11**: Toggle Fullscreen.
- **Mouse**: Interact with the UI menus.

## Level System
The game progresses dynamically:
1. **Level 1 (The Forest)**: Easy, no obstacles, green theme. (Target: 50 points)
2. **Level 2 (Night Time)**: Medium speed, border obstacles, blue theme. (Target: 120 points)
3. **Level 3 (The Desert)**: Fast speed, center cross obstacles, orange theme. (Target: 200 points)
4. **Level 4 (Ice Cavern)**: Faster speed, complex maze, cyan theme. (Target: 300 points)
5. **Level 5 (Neon Future)**: Maximum speed, hard maze, purple theme. (Infinite play)

## Future Improvements
- Add power-ups (speed boost, invincibility).
- Implement an online leaderboard.
- Add more particle effects for collisions.

