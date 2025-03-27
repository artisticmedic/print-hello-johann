
# Johann's Office Survival

A top-down 2D game where Johann must survive waves of interrupting team members in an office environment.

## 🎮 Game Overview

Johann, a developer trying to get work done, must defend against waves of colleagues who constantly interrupt with new tasks, design changes, and urgent requests. Collect XP, level up, and use powerful abilities to keep the interruptions at bay.

## 🕹️ Controls

- **Movement**: WASD Keys
  - W: Move Up
  - A: Move Left
  - S: Move Down
  - D: Move Right
- **Abilities**: JIKL Keys
  - J: Lightning Ability
  - K: Magic Missile Ability
  - L: Fire Cone Ability
  - I: Speed Burst

## ✨ Features

- Top-down 2D gameplay
- Multiple enemy types (different team members)
- Four unique abilities
- XP collection and leveling system
- Office-themed environment

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Pygame
- DearPyGUI

### Installation

1. Make a local copy for the repository. Use the zip installer to open the file.

2. Grab the pathname for the unzipped folder, and then cd pathname in Terminal.

3. Install dependencies
   ```
   pip install pygame dearpygui
   ```

4. Run the game
   ```
   python src/main.py
   ```

## 🛠️ Built With

- [Python](https://www.python.org/) - Programming language
- [Pygame](https://www.pygame.org/) - Game development library
- [DearPyGUI](https://github.com/hoffstadt/DearPyGUI) - GUI library

## 🎂 Fun Fact

This game was created for Johann's birthday! The XP orbs are actually birthday cakes.

## 📁 Project Structure

```
johanns-office-survival/
├── src/                 # Source code
│   ├── main.py          # Game entry point
│   ├── entities/        # Game entities
│   │   ├── player.py    # Player class
│   │   ├── enemies.py   # Enemy classes
│   │   └── abilities.py # Player abilities
│   └── utils/           # Utility functions
├── assets/              # Game assets
│   ├── sprites/         # Character and ability sprites
│   ├── backgrounds/     # Background images
│   └── sounds/          # Sound effects and music
├── docs/                # Documentation
└── README.md            # This file
```

## 📸 Screenshots

[Screenshots coming soon]

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
