# 🎯 Focus Buddy

**Your friendly terminal Pomodoro companion that makes productivity fun.**

Focus Buddy is a beautiful, interactive terminal-based Pomodoro timer that helps you stay focused, track your work sessions, and build better productivity habits — all with a cute ASCII buddy cheering you on.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

## ✨ Features

- 🍅 **Classic Pomodoro Timer** — 25-minute work sessions with 5-minute breaks
- ⚙️ **Custom Durations** — Set your own work, break, and long break times
- 📊 **Session Statistics** — Track daily focus time and completed sessions
- 📅 **7-Day History** — Visual history of your productivity over the past week
- 🎨 **Beautiful ASCII Art** — Your buddy reacts to your progress
- 🔔 **Audio Notifications** — Terminal bell when sessions complete
- 💾 **Persistent Stats** — All data saved locally in `~/.focus-buddy/`
- 🚀 **Zero Dependencies** — Pure Python, no pip install needed

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A terminal with Unicode support (most modern terminals)

### Installation

```bash
# Clone the repository
git clone https://github.com/IndraTensei/focus-buddy.git
cd focus-buddy

# Make it executable (optional)
chmod +x focus_buddy.py

# Run it!
python3 focus_buddy.py
```

### Optional: Install globally

```bash
# Copy to your PATH
sudo cp focus_buddy.py /usr/local/bin/focus-buddy
sudo chmod +x /usr/local/bin/focus-buddy

# Now use it anywhere
focus-buddy
```

## 📖 Usage

### Interactive Mode (Recommended)

Launch without arguments for the full interactive menu:

```bash
python3 focus_buddy.py
```

You'll see a menu with options for quick Pomodoro, custom timers, and stats.

### Quick Pomodoro

Jump straight into a classic 25/5 Pomodoro cycle:

```bash
python3 focus_buddy.py timer
```

### Custom Timer

Set your own durations (work / break / long break in minutes):

```bash
python3 focus_buddy.py custom 45 10 30
# 45 min work, 10 min break, 30 min long break
```

### View Stats

Check today's focus statistics:

```bash
python3 focus_buddy.py stats
```

### View History

See your 7-day productivity history:

```bash
python3 focus_buddy.py history
```

### Help

```bash
python3 focus_buddy.py --help
```

## 🎮 How It Works

1. **Start a work session** — Your buddy appears and the countdown begins
2. **Focus!** — Watch the progress bar fill up as time passes
3. **Session complete** — Your buddy celebrates with you 🎉
4. **Take a break** — Short break after each session, long break every 4 sessions
5. **Track progress** — All sessions are saved and stats are updated

The Pomodoro Technique:
- 🍅 Work for 25 minutes
- ☕ Take a 5-minute break
- 🔄 Repeat 4 times
- 🌴 Take a 15-minute long break

## 📁 Data Storage

Focus Buddy stores all data locally in `~/.focus-buddy/stats.json`. No cloud, no tracking, no accounts. Your data stays on your machine.

## 🛠️ Project Structure

```
focus-buddy/
├── focus_buddy.py    # Main application (single file, ~400 lines)
├── README.md         # This file
└── .gitignore        # Git ignore rules
```

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Ideas for Contributions

- 🌙 Dark/light theme toggle
- 📈 Weekly/monthly reports
- 🔊 Custom notification sounds
- 📤 Export stats to CSV
- 🏆 Achievement system
- 🌍 Multi-language support
- 📱 Mobile-friendly web version

## 📝 License

This project is licensed under the MIT License — feel free to use, modify, and distribute it.

## 🙏 Acknowledgments

- Inspired by the [Pomodoro Technique](https://francescocirillo.com/pages/pomodoro-technique) by Francesco Cirillo
- ASCII art crafted with love
- Built for everyone who wants to be more productive, one session at a time

---

Made with 💚 by [IndraTensei](https://github.com/IndraTensei)
