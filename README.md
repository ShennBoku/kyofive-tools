# 🛠️ KyoFive Tools

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/ShennBoku/kyofive-tools/blob/main/LICENSE)
[![Discord](https://img.shields.io/discord/1356249888802734132?label=Discord&logo=discord&color=7289DA)](https://discord.gg/XGaNQZ8R2e)
[![Support Me on Saweria](https://img.shields.io/badge/Support_Me-Saweria-yellow?logo=buymeacoffee)](https://saweria.co/ShennBoku)

A lightweight, efficient tool designed for FiveM players and developers to manage server caches and switch profiles instantly.

[Explore Features](#-features) •
[Installation](#-installation) •
[How to Use](#-how-to-use) •
[Credits](#-credits)

---

</div>

## 🌟 Features

KyoFive Tools provides a comprehensive suite of utilities designed for FiveM players and developers:

- 📂 **Smart Path Configuration**:
   - **Auto-Detection**: Automatically finds your CitizenFX (Roaming) and FiveM Application Data (Local) folders.
   - **Validation Logic**: Ensures your paths are valid by verifying essential files like `fivem.cfg` and `CitizenFX.ini`.

- 🎮 **Client Config Manager (Multi-Profile Binds)**:
   - **Profile Switcher**: Create multiple configuration profiles without affecting your core game settings (Graphics/Audio).
   - **Smart Sanitization**: Automatically wipes existing binds when creating new profiles for a clean slate.
   - **Binding Editor**: Manage `bind` and `rbind` commands with a searchable list of valid FiveM key parameters.
   - **Zero-Conflict Logic**: Injects your custom binds safely after the `unbindall` command in your config file.

- 🌐 **Advanced Cache Manager**:
   - **Server Search**: Fetch server details instantly using *Server Codes* (e.g., `k4y10g`).
   - **Hot-Swap Profiles**: Swap cache folders (`server-cache-priv`) between different servers to save GBs of bandwidth.
   - **Flexible Connection**: Toggle between Connect IP and Connect Code via the dropdown menu on the play button.
   - **Local Dev Support**: Auto-detects local servers (127.0.0.1:30120) with real-time player counts and game build info.
   - **Storage Stats**: Real-time calculation of cache sizes (GB/MB) directly in the UI.

- ⌨️ **Keyboard Clicker (Optimized Spammer)**:
   - **FiveM Engine Ready**: Uses 30ms hold-time logic to ensure the game engine registers every keystroke.
   - **Glassmorphism Overlay**: A sleek, floating status indicator that stays on top while you are in-game.
   - **Smart Recording**: Record triggers and spam keys instantly without manual typing.
   - **Loop Prevention**: Built-in logic to prevent key conflicts between triggers and targets.

- 📦 **Professional Storage Structure**:
   - **Isolated Data**: All configurations are stored securely in `%LOCALAPPDATA%/Kyogo Development/kyofive-tools/`.
   - **Safe Backups**: Keeps your original `fivem.cfg` safe in a dedicated `temp/` directory during profile swaps.

---

## 🚀 Installation

Make sure you have [Python 3.x](https://www.python.org/downloads/) installed on your system.

1. **Clone the Repository**
   ```bash
   git clone ShennBoku/kyofive-tools
   cd kyofive-tools
   ```

2. **Install Dependencies**
   ```bash
   pip install pywebview requests
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

---

## 📖 How to Use

1. **Search Server**: Open [FiveM Server List](https://servers.fivem.net), find the destination server, copy its unique code (example: `k4y10g`), then paste it in the application and press **Enter**.
2. **Connect**: Click the **Connect** button on the server card. The application will automatically configure your cache.
3. **Local Dev**: Turn on your FXServer, and the application will automatically display the **Local Server Detected** card.
4. **Manage Library**: Previously visited servers will be listed below. Use the **Reload** button to update the file size.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 🙌 Credits

- **Kyogo Development Team** - *Core Developer*
- [PyWebView](https://pywebview.flowrl.com/) - *GUI Engine*
- [SweetAlert2](https://sweetalert2.github.io/) - *Modern Popups*

<div align="center">
    <p>Made with ❤️ for the FiveM Community</p>
</div>