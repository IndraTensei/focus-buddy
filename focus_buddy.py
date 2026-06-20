#!/usr/bin/env python3
"""
Focus Buddy - A beautiful terminal Pomodoro timer with stats and ASCII art.

Usage:
    python focus_buddy.py              # Start interactive mode
    python focus_buddy.py timer        # Quick Pomodoro (25 min work, 5 min break)
    python focus_buddy.py custom 40 10  # Custom: 40 min work, 10 min break
    python focus_buddy.py stats        # View today's focus statistics
    python focus_buddy.py history      # View focus history
    python focus_buddy.py achievements # View unlocked achievements
    python focus_buddy.py export       # Export stats to CSV
    python focus_buddy.py report       # View weekly/monthly report
"""

import sys
import os
import json
import time
import math
import signal
import shutil
import csv
import io
from datetime import datetime, timedelta
from pathlib import Path

# ─── Constants ───────────────────────────────────────────────────────────────

VERSION = "1.1.0"
DATA_DIR = Path.home() / ".focus-buddy"
STATS_FILE = DATA_DIR / "stats.json"
ACHIEVEMENTS_FILE = DATA_DIR / "achievements.json"
DEFAULT_WORK = 25
DEFAULT_BREAK = 5
DEFAULT_LONG_BREAK = 15
SESSIONS_BEFORE_LONG_BREAK = 4

# ─── Achievement Definitions ─────────────────────────────────────────────────

ACHIEVEMENTS = {
    "first_session": {
        "name": "🌱 First Step",
        "description": "Complete your first Pomodoro session",
        "icon": "🌱",
        "condition": lambda s: count_completed_work_sessions(s) >= 1,
    },
    "ten_sessions": {
        "name": "🔟 Getting Started",
        "description": "Complete 10 Pomodoro sessions",
        "icon": "🔟",
        "condition": lambda s: count_completed_work_sessions(s) >= 10,
    },
    "fifty_sessions": {
        "name": "🏅 Dedicated",
        "description": "Complete 50 Pomodoro sessions",
        "icon": "🏅",
        "condition": lambda s: count_completed_work_sessions(s) >= 50,
    },
    "hundred_sessions": {
        "name": "💯 Centurion",
        "description": "Complete 100 Pomodoro sessions",
        "icon": "💯",
        "condition": lambda s: count_completed_work_sessions(s) >= 100,
    },
    "first_hour": {
        "name": "⏰ Hour Hero",
        "description": "Accumulate 60 minutes of focus time",
        "icon": "⏰",
        "condition": lambda s: total_focus_minutes(s) >= 60,
    },
    "five_hours": {
        "name": "🕐 Focus Warrior",
        "description": "Accumulate 300 minutes (5 hours) of focus time",
        "icon": "🕐",
        "condition": lambda s: total_focus_minutes(s) >= 300,
    },
    "ten_hours": {
        "name": "🦾 Focus Machine",
        "description": "Accumulate 600 minutes (10 hours) of focus time",
        "icon": "🦾",
        "condition": lambda s: total_focus_minutes(s) >= 600,
    },
    "streak_3": {
        "name": "🔥 On Fire",
        "description": "Maintain a 3-day focus streak",
        "icon": "🔥",
        "condition": lambda s: get_longest_streak(s) >= 3,
    },
    "streak_7": {
        "name": "⚡ Week Warrior",
        "description": "Maintain a 7-day focus streak",
        "icon": "⚡",
        "condition": lambda s: get_longest_streak(s) >= 7,
    },
    "streak_30": {
        "name": "👑 Streak Legend",
        "description": "Maintain a 30-day focus streak",
        "icon": "👑",
        "condition": lambda s: get_longest_streak(s) >= 30,
    },
    "early_bird": {
        "name": "🐦 Early Bird",
        "description": "Complete a session before 8 AM",
        "icon": "🐦",
        "condition": lambda s: has_session_before_hour(s, 8),
    },
    "night_owl": {
        "name": "🦉 Night Owl",
        "description": "Complete a session after 10 PM",
        "icon": "🦉",
        "condition": lambda s: has_session_after_hour(s, 22),
    },
    "marathon": {
        "name": "🏃 Marathon Runner",
        "description": "Complete 8 sessions in a single day",
        "icon": "🏃",
        "condition": lambda s: max_sessions_in_day(s) >= 8,
    },
    "centurion_minutes": {
        "name": "🎯 Century Club",
        "description": "Focus for 100 minutes in a single day",
        "icon": "🎯",
        "condition": lambda s: max_minutes_in_day(s) >= 100,
    },
    "consistent": {
        "name": "📅 Consistent",
        "description": "Complete sessions on 5 different days",
        "icon": "📅",
        "condition": lambda s: count_days_with_sessions(s) >= 5,
    },
}

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

# ─── Achievement Helper Functions ────────────────────────────────────────────

def count_completed_work_sessions(stats):
    return sum(1 for s in stats.get("sessions", [])
               if s.get("type") == "work" and s.get("completed"))

def total_focus_minutes(stats):
    return sum(d.get("focus_minutes", 0) for d in stats.get("daily", {}).values())

def count_days_with_sessions(stats):
    return len([d for d, v in stats.get("daily", {}).items() if v.get("sessions", 0) > 0])

def max_sessions_in_day(stats):
    return max((v.get("sessions", 0) for v in stats.get("daily", {}).values()), default=0)

def max_minutes_in_day(stats):
    return max((v.get("focus_minutes", 0) for v in stats.get("daily", {}).values()), default=0)

def get_longest_streak(stats):
    """Calculate the longest consecutive day streak with at least one completed work session."""
    daily = stats.get("daily", {})
    if not daily:
        return 0

    active_days = set()
    for day, data in daily.items():
        if data.get("sessions", 0) > 0:
            active_days.add(day)

    if not active_days:
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    max_streak = 0
    for seed_day in [today, yesterday]:
        if seed_day not in active_days:
            continue
        current = datetime.strptime(seed_day, "%Y-%m-%d")
        streak = 0
        while current.strftime("%Y-%m-%d") in active_days:
            streak += 1
            current -= timedelta(days=1)
        max_streak = max(max_streak, streak)

    sorted_days = sorted(active_days)
    current_streak = 1
    for i in range(1, len(sorted_days)):
        prev = datetime.strptime(sorted_days[i - 1], "%Y-%m-%d")
        curr = datetime.strptime(sorted_days[i], "%Y-%m-%d")
        if (curr - prev).days == 1:
            current_streak += 1
        else:
            max_streak = max(max_streak, current_streak)
            current_streak = 1
    max_streak = max(max_streak, current_streak)

    return max_streak

def has_session_before_hour(stats, hour):
    for s in stats.get("sessions", []):
        if s.get("completed") and s.get("type") == "work":
            try:
                ts = datetime.fromisoformat(s["timestamp"])
                if ts.hour < hour:
                    return True
            except (ValueError, KeyError):
                pass
    return False

def has_session_after_hour(stats, hour):
    for s in stats.get("sessions", []):
        if s.get("completed") and s.get("type") == "work":
            try:
                ts = datetime.fromisoformat(s["timestamp"])
                if ts.hour >= hour:
                    return True
            except (ValueError, KeyError):
                pass
    return False

# ─── Achievement System ──────────────────────────────────────────────────────

def load_achievements():
    if ACHIEVEMENTS_FILE.exists():
        with open(ACHIEVEMENTS_FILE, 'r') as f:
            return json.load(f)
    return {"unlocked": {}, "first_seen": {}}

def save_achievements(ach):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(ACHIEVEMENTS_FILE, 'w') as f:
        json.dump(ach, f, indent=2)

def check_achievements():
    """Check all achievements and return newly unlocked ones."""
    stats = load_stats()
    ach = load_achievements()
    newly_unlocked = []

    for key, achievement in ACHIEVEMENTS.items():
        if key not in ach["unlocked"]:
            try:
                if achievement["condition"](stats):
                    ach["unlocked"][key] = {
                        "unlocked_at": datetime.now().isoformat(),
                        "name": achievement["name"],
                        "description": achievement["description"],
                    }
                    newly_unlocked.append(achievement)
            except Exception:
                pass

    save_achievements(ach)
    return newly_unlocked, ach

def show_achievements():
    """Display all achievements (locked and unlocked)."""
    _, ach = check_achievements()
    clear_screen()
    print()
    print(center_text("╔══════════════════════════════════════════════════╗"))
    print(center_text("║            🏆 ACHIEVEMENTS                       ║"))
    print(center_text("╠══════════════════════════════════════════════════╣"))

    unlocked_count = len(ach["unlocked"])
    total_count = len(ACHIEVEMENTS)

    for key, achievement in ACHIEVEMENTS.items():
        if key in ach["unlocked"]:
            unlocked_at = ach["unlocked"][key].get("unlocked_at", "")
            try:
                dt = datetime.fromisoformat(unlocked_at)
                date_str = dt.strftime("%b %d")
            except (ValueError, TypeError):
                date_str = ""
            status = f"✅ {achievement['name']}"
            desc = f"   {achievement['description']} — {date_str}"
        else:
            status = "🔒 ???"
            desc = "   (locked)"

        print(center_text(f"║  {status:<47}║"))
        print(center_text(f"║  {desc:<47}║"))
        print(center_text("║                                                  ║"))

    print(center_text("╠══════════════════════════════════════════════════╣"))
    print(center_text(f"║  Unlocked: {unlocked_count}/{total_count}{' ' * (36 - len(str(unlocked_count)) - len(str(total_count)))}║"))
    print(center_text("╚══════════════════════════════════════════════════╝"))
    print()

def show_new_achievements(newly_unlocked):
    """Display newly unlocked achievements with fanfare."""
    if not newly_unlocked:
        return
    print()
    print(center_text("  🎉🎉🎉 NEW ACHIEVEMENT UNLOCKED! 🎉🎉🎉"))
    print()
    for ach in newly_unlocked:
        print(center_text(f"  {ach['icon']} {ach['name']}"))
        print(center_text(f"  {ach['description']}"))
        print()
    print(center_text("  Keep up the great work! 💪"))
    print()

# ─── CSV Export ──────────────────────────────────────────────────────────────

def export_csv(output_path=None):
    """Export all session data to CSV format."""
    stats = load_stats()
    sessions = stats.get("sessions", [])

    if not sessions:
        print("No sessions to export yet!")
        return None

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = DATA_DIR / f"focus_buddy_export_{timestamp}.csv"
    else:
        output_path = Path(output_path)

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Time", "Type", "Duration (min)", "Completed"])
        for s in sessions:
            try:
                dt = datetime.fromisoformat(s["timestamp"])
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M:%S")
            except (ValueError, KeyError):
                date_str = s.get("date", "unknown")
                time_str = "00:00:00"
            writer.writerow([
                date_str,
                time_str,
                s.get("type", ""),
                s.get("duration", 0),
                "Yes" if s.get("completed") else "No"
            ])

    return output_path

def export_csv_string():
    """Export all session data to a CSV string for display."""
    stats = load_stats()
    sessions = stats.get("sessions", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Time", "Type", "Duration (min)", "Completed"])
    for s in sessions:
        try:
            dt = datetime.fromisoformat(s["timestamp"])
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")
        except (ValueError, KeyError):
            date_str = s.get("date", "unknown")
            time_str = "00:00:00"
        writer.writerow([
            date_str,
            time_str,
            s.get("type", ""),
            s.get("duration", 0),
            "Yes" if s.get("completed") else "No"
        ])

    return output.getvalue()

# ─── Report Generation ───────────────────────────────────────────────────────

def show_report(period="weekly"):
    """Display a detailed weekly or monthly report."""
    daily = get_all_daily_stats()
    today = datetime.now()

    if period == "weekly":
        days_range = 7
        title = "📈 WEEKLY FOCUS REPORT"
        period_label = "This Week"
    elif period == "monthly":
        days_range = 30
        title = "📈 MONTHLY FOCUS REPORT"
        period_label = "This Month"
    else:
        days_range = 7
        title = "📈 WEEKLY FOCUS REPORT"
        period_label = "This Week"

    period_days = []
    total_sessions = 0
    total_minutes = 0
    total_breaks = 0
    active_days = 0
    best_day_sessions = 0
    best_day_minutes = 0
    best_day_label = "N/A"

    for i in range(days_range - 1, -1, -1):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        day_label = (today - timedelta(days=i)).strftime("%a %b %d")

        if day in daily:
            d = daily[day]
            sessions = d.get("sessions", 0)
            minutes = d.get("focus_minutes", 0)
            breaks = d.get("breaks", 0)
            total_sessions += sessions
            total_minutes += minutes
            total_breaks += breaks
            if sessions > 0:
                active_days += 1
            if sessions > best_day_sessions or (sessions == best_day_sessions and minutes > best_day_minutes):
                best_day_sessions = sessions
                best_day_minutes = minutes
                best_day_label = day_label
            period_days.append((day_label, sessions, minutes, True))
        else:
            period_days.append((day_label, 0, 0, False))

    avg_sessions = total_sessions / days_range
    avg_minutes = total_minutes / days_range
    avg_minutes_active = total_minutes / active_days if active_days > 0 else 0

    stats = load_stats()
    current_streak = 0
    check_day = today
    while True:
        day_str = check_day.strftime("%Y-%m-%d")
        if day_str in daily and daily[day_str].get("sessions", 0) > 0:
            current_streak += 1
            check_day -= timedelta(days=1)
        else:
            break

    longest_streak = get_longest_streak(stats)

    clear_screen()
    print()
    print(center_text("╔═══════════════════════════════════════════════════╗"))
    print(center_text(f"║  {title:<48}║"))
    print(center_text("╠═══════════════════════════════════════════════════╣"))

    hours = total_minutes // 60
    mins = total_minutes % 60
    print(center_text(f"║  Period: {period_label:<40}║"))
    print(center_text("║                                                   ║"))
    print(center_text(f"║  📊 Total Sessions:   {total_sessions:<25}║"))
    print(center_text(f"║  ⏱  Total Focus Time: {hours}h {mins}m{' ' * (22 - len(str(hours)) - len(str(mins)))}║"))
    print(center_text(f"║  ☕ Total Breaks:     {total_breaks:<25}║"))
    print(center_text(f"║  📅 Active Days:      {active_days}/{days_range}{' ' * (23 - len(str(active_days)) - len(str(days_range)))}║"))
    print(center_text("║                                                   ║"))
    print(center_text("╠═══════════════════════════════════════════════════╣"))
    print(center_text("║  📈 AVERAGES                                      ║"))
    print(center_text(f"║  Sessions/day:  {avg_sessions:.1f}{' ' * (32 - len(f'{avg_sessions:.1f}'))}║"))
    print(center_text(f"║  Minutes/day:   {avg_minutes:.1f}{' ' * (32 - len(f'{avg_minutes:.1f}'))}║"))
    if active_days > 0:
        print(center_text(f"║  Minutes/active: {avg_minutes_active:.1f}{' ' * (31 - len(f'{avg_minutes_active:.1f}'))}║"))
    print(center_text("║                                                   ║"))
    print(center_text("╠═══════════════════════════════════════════════════╣"))
    print(center_text("║  🔥 STREAKS                                       ║"))
    print(center_text(f"║  Current Streak:  {current_streak} day(s){' ' * (27 - len(str(current_streak)))}║"))
    print(center_text(f"║  Longest Streak:  {longest_streak} day(s){' ' * (27 - len(str(longest_streak)))}║"))
    print(center_text("║                                                   ║"))
    print(center_text("╠═══════════════════════════════════════════════════╣"))
    print(center_text("║  🏆 BEST DAY                                      ║"))
    print(center_text(f"║  {best_day_label} — {best_day_sessions} sessions, {best_day_minutes} min{' ' * (20 - len(best_day_label) - len(str(best_day_sessions)) - len(str(best_day_minutes)))}║"))
    print(center_text("║                                                   ║"))
    print(center_text("╠═══════════════════════════════════════════════════╣"))
    print(center_text("║  📅 DAILY BREAKDOWN                               ║"))

    for day_label, sessions, minutes, active in period_days:
        bar_len = min(sessions * 2, 16)
        bar = "🟩" * bar_len + "⬜" * (16 - bar_len)
        line = f"  {day_label} │ {bar} │ {sessions}s {minutes}m"
        print(center_text(f"║  {line:<48}║"))

    print(center_text("╚═══════════════════════════════════════════════════╝"))
    print()

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

        # Check for new achievements
        newly_unlocked, _ = check_achievements()
        show_new_achievements(newly_unlocked)

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
        print(center_text("  [5] 🏆 View Achievements"))
        print(center_text("  [6] 📈 Weekly Report"))
        print(center_text("  [7] 📤 Export to CSV"))
        print(center_text("  [8] 🚪 Quit"))
        print()

        choice = input(center_text("  Choose an option (1-8): ")).strip()

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
            show_achievements()
            input(center_text("  Press Enter to continue..."))
        elif choice == '6':
            clear_screen()
            print()
            period = input(center_text("  [w] Weekly report | [m] Monthly report: ")).strip().lower()
            if period == 'm':
                show_report("monthly")
            else:
                show_report("weekly")
            input(center_text("  Press Enter to continue..."))
        elif choice == '7':
            path = export_csv()
            if path:
                clear_screen()
                print()
                print(center_text("  📤 Export complete!"))
                print()
                print(center_text(f"  Saved to: {path}"))
                print()
                csv_content = export_csv_string()
                lines = csv_content.strip().split('\n')
                print(center_text("  Preview (first 10 rows):"))
                print()
                for line in lines[:11]:
                    print(center_text(f"  {line}"))
                print()
            input(center_text("  Press Enter to continue..."))
        elif choice == '8':
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

        elif cmd == "achievements":
            show_achievements()

        elif cmd == "export":
            output_path = sys.argv[2] if len(sys.argv) > 2 else None
            path = export_csv(output_path)
            if path:
                print(f"Exported to: {path}")
            else:
                print("No sessions to export.")

        elif cmd == "report":
            period = "weekly"
            if len(sys.argv) > 2:
                if sys.argv[2].lower() in ("monthly", "m"):
                    period = "monthly"
            show_report(period)

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
