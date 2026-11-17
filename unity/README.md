# Unity 3D (URP) Mobile Application Workspace

This directory contains the **Unity 3D (Universal Render Pipeline – URP)** mobile project workspace for *25 Aralık: Antep'in Hafızası* (Android & iOS).

## Planned Modular Structure

- `Assets/Scenes/` — `PersistentCoreScene` and additive scene modules (`part00`–`part08`) for low-RAM mobile scene streaming.
- `Assets/Scripts/Core/` — Additive scene loader, game state manager, audio controller, and mobile touch controller (Virtual Joystick + Touch/Gyro Look).
- `Assets/Scripts/Flythrough/` — `Cinemachine` guided museum camera tour, free-roam navigation, and interactive exhibit info cards (**Mode A**).
- `Assets/Scripts/Gameplay/` — Living exhibit Mixamo character controllers, Level 1 mechanics (Archive clues, Atrium floor-map route puzzle, Kastel cipher telegraph), and Level 2 mechanics (Diorama supply mini-games, 360° Panorama tactical defense) (**Mode B**).
- `Assets/ScriptableObjects/` — Data-driven quest steps, historical exhibit metadata, and puzzle configurations for easy extensibility.
- `Assets/Models/` — Optimized 3D museum modules, physics colliders, and rigged character animations.

> **Note:** Large source `.fbx` packages are hosted under the repository's **[Releases (`v0.1.0`)](https://github.com/IBRAHIMHILVANI/panorama-25-aralik-museum/releases/tag/v0.1.0)** page. Ongoing Unity development updates are pushed directly to this directory.
