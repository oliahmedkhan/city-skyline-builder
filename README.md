# 🏙️ City Skyline Builder

**City Skyline Builder** is a 2D building-stacking game developed using **Python, PyOpenGL, and GLUT**. The objective is to construct a tall city tower by dropping building blocks from a moving crane while maintaining tower balance.

The game features animated clouds, flying birds, a city skyline background, a moving crane, balance calculations, tower sway, and collapse animations.

## 🎮 Game Preview

<!-- Add your game screenshot or GIF here -->
<!-- Example: ![City Skyline Builder](screenshots/gameplay.png) -->

## ✨ Features

- **Building Stacking:** Drop building blocks to construct a tall tower.
- **Moving Crane:** A crane moves horizontally and carries the next building block.
- **Tower Balance System:** Calculates tower balance using the center of mass and support margins.
- **Dynamic Tower Sway:** The tower moves according to its balance condition.
- **Collapse Animation:** The tower collapses when it becomes unstable.
- **Camera Following:** The camera automatically follows the tower as it grows.
- **Animated Clouds:** Clouds move across the sky.
- **City Skyline:** Includes buildings, windows, trees, roads, and construction-site graphics.
- **Game HUD:** Displays score, floor count, best height, balance percentage, and tower status.
- **Restart System:** Restart the game whenever the tower collapses.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| PyOpenGL | 2D graphics rendering |
| OpenGL | Graphics rendering |
| GLUT / FreeGLUT | Window management and keyboard/mouse interaction |
| Math | Balance calculations, animation, and movement |
| Random | Randomized cloud and bird positions |

## 🎯 Game Controls

| Key / Action | Function |
|---|---|
| `SPACE` | Drop the building block |
| `LEFT CLICK` | Drop the building block |
| `A` | Move the crane left |
| `D` | Move the crane right |
| `LEFT ARROW` | Move the crane left |
| `RIGHT ARROW` | Move the crane right |
| `R` | Restart the game |
| `ESC` | Exit the game |

## ⚖️ Tower Balance System

The game calculates tower balance using the center of mass and support margins of the stacked building modules.

The balance percentage represents how safely the tower is supported.

| Balance | Status |
|---|---|
| 80–100% | EXCELLENT |
| 60–79% | GOOD |
| 40–59% | WARNING |
| 20–39% | CRITICAL |
| 1–19% | EXTREMELY UNSTABLE |
| 0% | UNSTABLE |

When the tower becomes unstable, a collapse animation is triggered, followed by the Game Over screen.

*Note: The balance system is an arcade-style approximation based on the implemented center-of-mass and support-margin calculations. It is not a full rigid-body physics simulation.*

## 🎓 Project Purpose

This project was developed as a 2D computer graphics application using Python and OpenGL.

It demonstrates practical applications of:

- 2D geometric transformations
- Translation and rotation
- OpenGL primitive rendering
- Animation using timer callbacks
- Keyboard and mouse interaction
- Camera movement
- Center-of-mass calculations
- Basic stability and collision-related game logic
  
## 📜 License

This project is available for educational and personal learning purposes. You may modify and improve it with appropriate attribution.

---

⭐ If you like this project, consider giving the repository a star!
