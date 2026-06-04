#!/usr/bin/env python3
"""
Focus Buddy - A beautiful terminal Pomodoro timer with stats and ASCII art.

Usage:
    python focus_buddy.py              # Start interactive mode
    python focus_buddy.py timer        # Quick Pomodoro (25 min work, 5 min break)
    python focus_buddy.py custom 40 10  # Custom: 40 min work, 10 min break
    python focus_buddy.py stats        # View today's focus statistics
    python focus_buddy.py history      # View focus history
"""

import sys
import os
import json
import time
import math
import signal
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# ─── Constants ───────────────────────────────────────────────────────────────

VERSION = "1.0.0"
DATA_DIR = Path.home() / ".focus-buddy"
STATS_FILE = DATA_DIR / "stats.json"
DEFAULT_WORK = 25
DEFAULT_BREAK = 5
DEFAULT_LONG_BREAK = 15
SESSIONS_BEFORE_LONG_BREAK = 4

# ─── ASCII Art ───────────────────────────────────────────────────────────────

BUDDY_FACE_WORK = """
    ╭──────╮
    │ ◕  ◕ │  Let's focus!
    │  ──  │
    │ ╰──╯ │
    ╰──────╯
"""

BUDDY_FACE_BREAK = """
    ╭──────╮
    │ ˘  ˘ │  Break time!
    │  ──  │
    │ ╰‿╯ │
    ╰──────╯
"""

BUDDY_FACE_DONE = """
    ╭──────╮
    │ ★  ★ │  Amazing!
    │  ──  │
    │ ╰▽╯ │
    ╰──────╯
"""

BUDDY_FACE_CELEBRATION = """
  ★ ☆ ★ ☆ ★ ☆ ★
  ╭──────╮
  │ ✧  ✧ │  Session complete!
  │  ──  │
  │ ╰▽╯ │
  ╰──────╯
  ☆ ★ ☆ ★ ☆ ★ ☆
"""

LOGO = r"""
  ███████╗ ██████╗  ██████╗██╗   ██╗███████╗
  ██╔════╝██╔═══██╗██╔════╝██║   ██║██╔════╝
  █████╗  ██║   ██║██║     ██║   ██║███████╗
  ██╔══╝  ██║   ██║██║     ██║   ██║╚════██║
  ██║     ╚██████╔╝╚██████╗╚██████╔╝███████║
  ╚═╝      ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝
        ██████╗ ██╗   ██╗██████╗ ██████╗ ██╗   ██╗
        ██╔══██╗██║   ██║██╔══██╗██╔══██╗╚██╗ ██╔╝
        ██████╔╝██║   ██║██║  ██║██║  ██║ ╚████╔╝
        ██╔══██╗██║   ██║██║  ██║██║  ██║  ╚██╔╝
        ██████╔╝╚██████╔╝██████╔╝██████╔╝   ██║
        ╚═════╝  ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝
"""

# ─── Utility Functions ───────────────────────────────────────────────────────

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_width():
    return shutil.get_terminal_size().columns

def center_text(text, width=None):
    width = width or get_terminal_width()
    lines = text.split('\n')
    return '\n'.join(line.center(width) for line in lines)

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

def progress_bar(current, total, width=30, fill_char='█', empty_char='░'):
    ratio = current / total if total > 0 else 0
    filled = int(width * ratio)
    empty = width - filled
    bar = fill_char * filled + empty_char * empty
    pct = ratio * 100
    return f"[{bar}] {pct:.1f}%"

def ring_bell():
    """Try to play a terminal bell sound."""
    try:
        print('\a', end='', flush=True)
        # Also try paplay or aplay if available
        os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null &')
    except Exception:
        pass

# ─── Stats Management ────────────────────────────────────────────────────────

def load_stats():
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {"sessions": [], "daily": {}}

def save_stats(stats):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def record_session(session_type, duration_minutes, completed=True):
    stats = load_stats()
    today = datetime.now().strftime("%Y-%m-%d")
    session = {
        "type": session_type,
        "duration": duration_minutes,
        "completed": completed,
        "timestamp": datetime.now().isoformat(),
        "date": today
    }
    stats["sessions"].append(session)

    if today not in stats["daily"]:
        stats["daily"][today] = {"sessions": 0, "focus_minutes": 0, "breaks": 0}

    stats["daily"][today]["sessions"] += 1
    if session_type == "work" and completed:
        stats["daily"][today]["focus_minutes"] += duration_minutes
    elif session_type == "break":
        stats["daily"][today]["breaks"] += 1

    save_stats(stats)

def get_today_stats():
    stats = load_stats()
    today = datetime.now().strftime("%Y-%m-%d")
    return stats["daily"].get(today, {"sessions": 0, "focus_minutes": 0, "breaks": 0})

def get_all_daily_stats():
    stats = load_stats()
    return stats.get("daily", {})

# ─── Timer Engine ────────────────────────────────────────────────────────────

class PomodoroTimer:
    def __init__(self, work_minutes=DEFAULT_WORK, break_minutes=DEFAULT_BREAK,
                 long_break_minutes=DEFAULT_LONG_BREAK):
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
        self.long_break_minutes = long_break_minutes
        self.sessions_completed = 0
        self.running = True
        self.interrupted = False

        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, signum, frame):
        self.interrupted = True
        self.running = False

    def _countdown(self, total_seconds, label, face):
        """Run a countdown timer with a live display."""
        start_time = time.time()
        end_time = start_time + total_seconds

        while time.time() < end_time and self.running:
            remaining = end_time - time.time()
            if remaining < 0:
                remaining = 0

            elapsed = total_seconds - remaining
            bar = progress_bar(elapsed, total_seconds, width=40)
            time_str = format_time(remaining)

            # Build display
            clear_screen()
            print()
            print(center_text(LOGO))
            print(center_text(f"  {label}"))
            print()
            print(center_text(face))
            print()
            print(center_text(f"  ⏱  {time_str} remaining"))
            print(center_text(f"  {bar}"))
            print()
            print(center_text(f"  Sessions completed today: {self.sessions_completed}"))
            print()
            print(center_text("  Press Ctrl+C to stop"))
            print()

            time.sleep(0.25)

        return not self.interrupted

    def run_work_session(self):
        """Run a single work session."""
        self.running = True
        self.interrupted = False
        total_seconds = self.work_minutes * 60

        completed = self._countdown(
            total_seconds,
            f"🔥 WORK SESSION — {self.work_minutes} minutes",
            BUDDY_FACE_WORK
        )

        if completed:
            self.sessions_completed += 1
            record_session("work", self.work_minutes, completed=True)
            self._show_completion()
            return True
        else:
            record_session("work", self.work_minutes, completed=False)
            return False

    def run_break_session(self, is_long=False):
        """Run a break session."""
        self.running = True
        self.interrupted = False

        if is_long:
            duration = self.long_break_minutes
            label = f"🌴 LONG BREAK — {self.long_break_minutes} minutes"
        else:
            duration = self.break_minutes
            label = f"☕ SHORT BREAK — {self.break_minutes} minutes"

        total_seconds = duration * 60

        completed = self._countdown(
            total_seconds,
            label,
            BUDDY_FACE_BREAK
        )

        if completed:
            record_session("break", duration, completed=True)
            return True
        else:
            record_session("break", duration, completed=False)
            return False

    def _show_completion(self):
        """Show session completion celebration."""
        ring_bell()
        clear_screen()
        print()
        print(center_text(BUDDY_FACE_CELEBRATION))
        print(center_text("  🎉 Great job! Session complete!"))
        print()

        today = get_today_stats()
        print(center_text(f"  Today's stats: {today['sessions']} sessions, "
                         f"{today['focus_minutes']} minutes focused"))
        print()

    def run_cycle(self):
        """Run a full Pomodoro cycle: work → break → work → break → ... → long break."""
        clear_screen()
        print()
        print(center_text(LOGO))
        print(center_text("  Welcome to Focus Buddy! 🎯"))
        print()
        print(center_text(f"  Work: {self.work_minutes} min | "
                         f"Break: {self.break_minutes} min | "
                         f"Long Break: {self.long_break_minutes} min"))
        print()
        input(center_text("  Press Enter to start..."))

        while True:
            # Work session
            if not self.run_work_session():
                break

            # Decide break type
            if self.sessions_completed % SESSIONS_BEFORE_LONG_BREAK == 0:
                is_long = True
                msg = "Time for a long break! 🌴"
            else:
                is_long = False
                msg = "Time for a short break! ☕"

            clear_screen()
            print()
            print(center_text(BUDDY_FACE_DONE))
            print(center_text(f"  {msg}"))
            print()
            input(center_text("  Press Enter to start break..."))

            self.run_break_session(is_long=is_long)

            clear_screen()
            print()
            print(center_text(BUDDY_FACE_DONE))
            print(center_text("  Break over! Ready for another session?"))
            print()

            today = get_today_stats()
            print(center_text(f"  Today: {today['sessions']} sessions, "
                             f"{today['focus_minutes']} min focused"))
            print()

            choice = input(center_text("  [Enter] Continue | [q] Quit | [s) Stats: ")).strip().lower()
            if choice == 'q':
                break
            elif choice == 's':
                show_stats()
                input(center_text("  Press Enter to continue..."))

        self._show_final_summary()

    def _show_final_summary(self):
        """Show end-of-session summary."""
        today = get_today_stats()
        clear_screen()
        print()
        print(center_text("╔══════════════════════════════════════╗"))
        print(center_text("║       📊 SESSION SUMMARY             ║"))
        print(center_text("╠══════════════════════════════════════╣"))
        print(center_text(f"║  Sessions completed: {today['sessions']:<17}║"))
        print(center_text(f"║  Focus time: {today['focus_minutes']} min{' ' * (24 - len(str(today['focus_minutes'])))}║"))
        print(center_text(f"║  Breaks taken: {today['breaks']:<18}║"))
        print(center_text("╚══════════════════════════════════════╝"))
        print()
        print(center_text("  Great work today! See you next time! 👋"))
        print()

# ─── Stats Display ────────────────────────────────────────────────────────────

def show_stats():
    """Display today's focus statistics."""
    today = get_today_stats()
    clear_screen()
    print()
    print(center_text("╔══════════════════════════════════════╗"))
    print(center_text("║       📊 TODAY'S FOCUS STATS         ║"))
    print(center_text("╠══════════════════════════════════════╣"))
    print(center_text(f"║  🎯 Sessions: {today['sessions']:<21}║"))
    print(center_text(f"║  ⏱  Focus Minutes: {today['focus_minutes']:<16}║"))
    print(center_text(f"║  ☕ Breaks: {today['breaks']:<23}║"))
    print(center_text("╚══════════════════════════════════════╝"))
    print()

    # Visual session blocks
    if today['sessions'] > 0:
        blocks = '🟩' * today['sessions']
        print(center_text(f"  {blocks}"))
        print()

def show_history():
    """Display focus history for the past 7 days."""
    daily = get_all_daily_stats()
    clear_screen()
    print()
    print(center_text("╔═══════════════════════════════════════════════╗"))
    print(center_text("║          📅 7-DAY FOCUS HISTORY               ║"))
    print(center_text("╠═══════════════════════════════════════════════╣"))

    today = datetime.now()
    for i in range(6, -1, -1):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        day_label = (today - timedelta(days=i)).strftime("%a %b %d")
        if i == 0:
            day_label += " (today)"

        if day in daily:
            d = daily[day]
            sessions = d.get("sessions", 0)
            minutes = d.get("focus_minutes", 0)
            bar_len = min(sessions * 2, 20)
            bar = "🟩" * bar_len + "⬜" * (20 - bar_len)
            print(center_text(f"║  {day_label} │ {bar} │ {sessions}s {minutes}m ║"))
        else:
            print(center_text(f"║  {day_label} │ {'⬜' * 20} │ 0s 0m ║"))

    print(center_text("╚═══════════════════════════════════════════════╝"))
    print()

# ─── Interactive Menu ─────────────────────────────────────────────────────────

def interactive_menu():
    """Show the interactive menu."""
    while True:
        clear_screen()
        print()
        print(center_text(LOGO))
        print()
        print(center_text("  🎯 What would you like to do?"))
        print()
        print(center_text("  [1] 🍅 Quick Pomodoro (25/5 min)"))
        print(center_text("  [2] ⚙️  Custom Timer"))
        print(center_text("  [3] 📊 View Today's Stats"))
        print(center_text("  [4] 📅 View 7-Day History"))
        print(center_text("  [5] 🚪 Quit"))
        print()

        choice = input(center_text("  Choose an option (1-5): ")).strip()

        if choice == '1':
            timer = PomodoroTimer()
            timer.run_cycle()
        elif choice == '2':
            try:
                work = int(input(center_text("  Work minutes (default 25): ") or "25"))
                short_break = int(input(center_text("  Break minutes (default 5): ") or "5"))
                long_break = int(input(center_text("  Long break minutes (default 15): ") or "15"))
                timer = PomodoroTimer(work, short_break, long_break)
                timer.run_cycle()
            except ValueError:
                print(center_text("  ❌ Invalid input. Using defaults."))
                timer = PomodoroTimer()
                timer.run_cycle()
        elif choice == '3':
            show_stats()
            input(center_text("  Press Enter to continue..."))
        elif choice == '4':
            show_history()
            input(center_text("  Press Enter to continue..."))
        elif choice == '5':
            clear_screen()
            print()
            print(center_text(BUDDY_FACE_DONE))
            print(center_text("  Thanks for using Focus Buddy! Stay productive! 🚀"))
            print()
            break
        else:
            print(center_text("  ❌ Invalid choice. Try again."))
            time.sleep(1)

# ─── CLI Entry Point ─────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "timer":
            timer = PomodoroTimer()
            timer.run_cycle()

        elif cmd == "custom":
            try:
                work = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_WORK
                brk = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_BREAK
                long_brk = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_LONG_BREAK
            except (ValueError, IndexError):
                print("Usage: focus-buddy custom <work_min> <break_min> [long_break_min]")
                sys.exit(1)
            timer = PomodoroTimer(work, brk, long_brk)
            timer.run_cycle()

        elif cmd == "stats":
            show_stats()

        elif cmd == "history":
            show_history()

        elif cmd in ("help", "--help", "-h"):
            print(__doc__)

        elif cmd in ("version", "--version", "-v"):
            print(f"Focus Buddy v{VERSION}")

        else:
            print(f"Unknown command: {cmd}")
            print(__doc__)
            sys.exit(1)
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
