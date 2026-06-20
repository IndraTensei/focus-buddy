# 🎯 Focus Buddy

**Your friendly terminal Pomodoro companion that makes productivity fun.**

Focus Buddy is a beautiful, interactive terminal-based Pomodoro timer that helps you stay focused, track your work sessions, and build better productivity habits — all with a cute ASCII buddy cheering you on.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)
![Version](https://img.shields.io/badge/Version-1.1.0-blue)

## ✨ Features

- 🍅 **Classic Pomodoro Timer** — 25-minute work sessions with 5-minute breaks
- ⚙️ **Custom Durations** — Set your own work, break, and long break times
- 📊 **Session Statistics** — Track daily focus time and completed sessions
- 📅 **7-Day History** — Visual history of your productivity over the past week
- 🎨 **Beautiful ASCII Art** — Your buddy reacts to your progress
- 🔔 **Audio Notifications** — Terminal bell when sessions complete
- 💾 **Persistent Stats** — All data saved locally in `~/.focus-buddy/`
- 🚀 **Zero Dependencies** — Pure Python, no pip install needed
- 🏆 **Achievement System** — Unlock 15 badges as you hit milestones (new!)
- 📤 **CSV Export** — Export all your session data to CSV for analysis (new!)
- 📈 **Weekly & Monthly Reports** — Rich analytics with streaks, averages, and best days (new!)

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

### View Achievements

See your unlocked badges and progress:

```bash
python3 focus_buddy.py achievements
```

### Export to CSV

Export all session data to a CSV file:

```bash
# Export to default location (~/.focus-buddy/)
python3 focus_buddy.py export

# Export to a specific path
python3 focus_buddy.py export ~/my-focus-data.csv
```

### Weekly / Monthly Reports

View detailed analytics with streaks, averages, and best days:

```bash
# Weekly report (default)
python3 focus_buddy.py report

# Monthly report
python3 focus_buddy.py report monthly
```

### Help

```bash
python3 focus_buddy.py --help
```

### Version

```bash
python3 focus_buddy.py --version
```

## 🏆 Achievements

Focus Buddy has **15 achievements** to unlock as you build your productivity habits:

| Achievement | Badge | How to Unlock |
|---|---|---|
| First Step | 🌱 | Complete your first Pomodoro session |
| Getting Started | 🔟 | Complete 10 Pomodoro sessions |
| Dedicated | 🏅 | Complete 50 Pomodoro sessions |
| Centurion | 💯 | Complete 100 Pomodoro sessions |
| Hour Hero | ⏰ | Accumulate 60 minutes of focus time |
| Focus Warrior | 🕐 | Accumulate 300 minutes (5 hours) of focus time |
| Focus Machine | 🦾 | Accumulate 600 minutes (10 hours) of focus time |
| On Fire | 🔥 | Maintain a 3-day focus streak |
| Week Warrior | ⚡ | Maintain a 7-day focus streak |
| Streak Legend | 👑 | Maintain a 30-day focus streak |
| Early Bird | 🐦 | Complete a session before 8 AM |
| Night Owl | 🦉 | Complete a session after 10 PM |
| Marathon Runner | 🏃 | Complete 8 sessions in a single day |
| Century Club | 🎯 | Focus for 100 minutes in a single day |
| Consistent | 📅 | Complete sessions on 5 different days |

New achievements are automatically checked and celebrated when you complete a work session!

## 📈 Report Features

The weekly and monthly reports include:
- **Total sessions, focus time, and breaks** for the period
- **Averages**: sessions/day and minutes/day (overall and active days only)
- **Streaks**: current streak and all-time longest streak
- **Best day**: your most productive day in the period
- **Daily breakdown**: visual bar chart for each day

## 🎮 How It Works

1. **Start a work session** — Your buddy appears and the countdown begins
2. **Focus!** — Watch the progress bar fill up as time passes
3. **Session complete** — Your buddy celebrates with you 🎉
4. **Check achievements** — New badges pop up automatically!
5. **Take a break** — Short break after each session, long break every 4 sessions
6. **Track progress** — All sessions are saved and stats are updated

The Pomodoro Technique:
- 🍅 Work for 25 minutes
- ☕ Take a 5-minute break
- 🔄 Repeat 4 times
- 🌴 Take a 15-minute long break

## 📁 Data Storage

Focus Buddy stores all data locally in `~/.focus-buddy/`:
- `stats.json` — Session and daily statistics
- `achievements.json` — Unlocked achievements
- `focus_buddy_export_*.csv` — CSV exports (when requested)

No cloud, no tracking, no accounts. Your data stays on your machine.

## 🛠️ Project Structure

```
focus-buddy/
├── focus_buddy.py    # Main application (single file, ~900 lines)
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
- 🔊 Custom notification sounds
- 🌍 Multi-language support
- 📱 Mobile-friendly web version
- 🔗 Integration with task managers (Todoist, etc.)
- 🎵 Spotify/ambient sound integration during focus

## 📝 License

This project is licensed under the MIT License — feel free to use, modify, and distribute it.

## 🙏 Acknowledgments

- Inspired by the [Pomodoro Technique](https://francescocirillo.com/pages/pomodoro-technique) by Francesco Cirillo
- ASCII art crafted with love
- Built for everyone who wants to be more productive, one session at a time

---

Made with 💚 by [IndraTensei](https://github.com/IndraTensei)
