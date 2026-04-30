# 🛠️ KyoFive Tools

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/ShennBoku/kyofive-tools/blob/main/LICENSE)
[![Discord](https://img.shields.io/discord/1356249888802734132?label=Discord&logo=discord&color=7289DA)](https://discord.gg/XGaNQZ8R2e)
[![Framework](https://img.shields.io/badge/Framework-ESX%20Legacy%201.13.3-red.svg)](https://github.com/esx-framework/esx_core/releases/tag/1.13.3)
[![Support Me on Saweria](https://img.shields.io/badge/Support_Me-Saweria-yellow?logo=buymeacoffee)](https://saweria.co/ShennBoku)

A lightweight, efficient tool designed for FiveM players and developers to manage server caches and switch profiles instantly.

[Explore Features](#-features) •
[Installation](#-installation) •
[How to Use](#-how-to-use) •
[Credits](#-credits)

---

</div>

## 🌟 Features

KyoFive Tools comes with several key features that make managing your FiveM data easier:

- 🔍 **Smart Search**: Search for specific server data by simply entering *Server Code*.
- 🔄 **Profile Switching**: Instantly swap cache folders between servers without re-downloading assets (GB).
- 📡 **Local Detection**: Auto detect local server (localhost:30120) for *development* purposes.
- 📦 **Hybrid Storage**: Using the organized `kyofive-storage` folder system.
- 📊 **Real-time Stats**: Calculate cache folder size (GB/MB) directly in UI.

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