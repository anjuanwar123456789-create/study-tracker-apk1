import json
import os
from datetime import datetime, date

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

DAILY_GOAL = 360
SUBJECTS = [
    "Physics", "Chemistry", "Maths", "Computer Science", "English",
    "Economics", "Accountancy", "Business Studies", "Biology",
    "History", "Geography", "Political Science"
]


class StudyTrackerApp(App):
    def build(self):
        self.title = "Study Tracker"
        self.data_file = os.path.join(self.user_data_dir, "study_tracker_data.json")
        self.data = self.load_data()

        self.selected_subject = SUBJECTS[0]
        self.timer_seconds = 0
        self.current_session_seconds = 0
        self.is_running = False
        self.timer_event = None

        self.manager = ScreenManager()
        self.manager.add_widget(self.make_main_screen())
        self.manager.add_widget(self.make_history_screen())

        self.update_dashboard()
        return self.manager

    def load_data(self):
        if not os.path.exists(self.data_file):
            return {"sessions": []}
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"sessions": []}

    def save_data(self):
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def today_string(self):
        return date.today().strftime("%Y-%m-%d")

    def format_time(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_subject_seconds(self, subject):
        return sum(
            s.get("duration", 0) for s in self.data["sessions"]
            if s.get("subject") == subject and s.get("date") == self.today_string()
        )

    def get_today_seconds(self):
        return sum(
            s.get("duration", 0) for s in self.data["sessions"]
            if s.get("date") == self.today_string()
        )

    def get_all_seconds(self):
        return sum(s.get("duration", 0) for s in self.data["sessions"])

    def save_current_session(self):
        if self.current_session_seconds <= 0:
            return
        self.data["sessions"].append({
            "date": self.today_string(),
            "time": datetime.now().strftime("%H:%M:%S"),
            "subject": self.selected_subject,
            "duration": self.current_session_seconds
        })
        self.save_data()
        self.current_session_seconds = 0

    def tick(self, dt):
        if not self.is_running:
            return
        self.timer_seconds += 1
        self.current_session_seconds += 1
        self.timer_label.text = self.format_time(self.timer_seconds)
        self.update_dashboard()

    def start_timer(self):
        if self.is_running:
            return
        self.is_running = True
        self.status_label.text = "Studying " + self.selected_subject
        if self.timer_event is None:
            self.timer_event = Clock.schedule_interval(self.tick, 1)

    def pause_timer(self):
        if not self.is_running:
            return
        self.is_running = False
        self.status_label.text = "Timer Paused"

    def stop_timer(self):
        self.is_running = False
        if self.current_session_seconds > 0:
            self.save_current_session()
        self.timer_seconds = 0
        self.current_session_seconds = 0
        self.timer_label.text = "00:00:00"
        self.status_label.text = "Timer Stopped"
        self.update_dashboard()

    def change_subject(self, spinner, text):
        if text == self.selected_subject:
            return
        if self.current_session_seconds > 0:
            self.save_current_session()
        self.selected_subject = text
        self.timer_seconds = 0
        self.current_session_seconds = 0
        self.is_running = False
        self.timer_label.text = "00:00:00"
        self.status_label.text = "Selected: " + text
        self.update_dashboard()

    def update_dashboard(self):
        if not hasattr(self, "subject_grid"):
            return

        self.subject_grid.clear_widgets()
        for subject in SUBJECTS:
            seconds = self.get_subject_seconds(subject)
            if subject == self.selected_subject and self.current_session_seconds > 0:
                seconds += self.current_session_seconds

            self.subject_grid.add_widget(Label(
                text=subject, size_hint_y=None, height=dp(38),
                halign="left", valign="middle"
            ))
            self.subject_grid.add_widget(Label(
                text=self.format_time(seconds), size_hint_y=None, height=dp(38)
            ))
            self.subject_grid.add_widget(Label(
                text=f"{seconds / 60:.1f}", size_hint_y=None, height=dp(38)
            ))

        today_seconds = self.get_today_seconds() + self.current_session_seconds
        today_minutes = today_seconds / 60
        today_hours = today_seconds / 3600

        total_seconds = self.get_all_seconds() + self.current_session_seconds
        total_hours = total_seconds / 3600

        percentage = min(100, (today_minutes / DAILY_GOAL) * 100)

        self.today_label.text = f"Today: {today_hours:.2f} hours"
        self.total_label.text = f"Total: {total_hours:.2f} hours"
        self.goal_label.text = f"{today_minutes:.0f} / {DAILY_GOAL} minutes"
        self.progress.value = percentage
        self.percent_label.text = f"{percentage:.0f}%"

    def make_main_screen(self):
        screen = Screen(name="main")
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        title = Label(text="STUDY TRACKER", font_size=dp(26),
                      bold=True, size_hint_y=None, height=dp(45))
        subtitle = Label(
            text="Track your study time and reach your daily goal",
            font_size=dp(12), size_hint_y=None, height=dp(30)
        )
        root.add_widget(title)
        root.add_widget(subtitle)

        subject_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        subject_row.add_widget(Label(text="Subject:", size_hint_x=0.3))
        self.spinner = Spinner(
            text=SUBJECTS[0], values=SUBJECTS, size_hint_x=0.7
        )
        self.spinner.bind(text=self.change_subject)
        subject_row.add_widget(self.spinner)
        root.add_widget(subject_row)

        self.timer_label = Label(text="00:00:00", font_size=dp(42),
                                 bold=True, size_hint_y=None, height=dp(75))
        self.status_label = Label(text="Ready to study", size_hint_y=None, height=dp(30))
        root.add_widget(self.timer_label)
        root.add_widget(self.status_label)

        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
        start = Button(text="START")
        pause = Button(text="PAUSE")
        stop = Button(text="STOP")
        start.bind(on_release=lambda *_: self.start_timer())
        pause.bind(on_release=lambda *_: self.pause_timer())
        stop.bind(on_release=lambda *_: self.stop_timer())
        buttons.add_widget(start)
        buttons.add_widget(pause)
        buttons.add_widget(stop)
        root.add_widget(buttons)

        goal_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(90),
                             padding=dp(6), spacing=dp(3))
        self.goal_label = Label(text="0 / 360 minutes", bold=True)
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(18))
        self.percent_label = Label(text="0%", size_hint_y=None, height=dp(24))
        goal_box.add_widget(Label(text="DAILY GOAL", bold=True))
        goal_box.add_widget(self.goal_label)
        goal_box.add_widget(self.progress)
        goal_box.add_widget(self.percent_label)
        root.add_widget(goal_box)

        stats = BoxLayout(size_hint_y=None, height=dp(45))
        self.today_label = Label(text="Today: 0.00 hours")
        self.total_label = Label(text="Total: 0.00 hours")
        stats.add_widget(self.today_label)
        stats.add_widget(self.total_label)
        root.add_widget(stats)

        dash_title = Label(text="SUBJECT DASHBOARD — Today's study time",
                           bold=True, size_hint_y=None, height=dp(35))
        root.add_widget(dash_title)

        scroll = ScrollView()
        self.subject_grid = GridLayout(cols=3, spacing=dp(4), size_hint_y=None)
        self.subject_grid.bind(minimum_height=self.subject_grid.setter("height"))
        for header in ("Subject", "Time", "Minutes"):
            self.subject_grid.add_widget(Label(text=header, bold=True,
                                               size_hint_y=None, height=dp(38)))
        scroll.add_widget(self.subject_grid)
        root.add_widget(scroll)

        bottom = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        history = Button(text="VIEW HISTORY")
        reset = Button(text="RESET TODAY")
        history.bind(on_release=lambda *_: self.show_history())
        reset.bind(on_release=lambda *_: self.reset_today())
        bottom.add_widget(history)
        bottom.add_widget(reset)
        root.add_widget(bottom)

        screen.add_widget(root)
        return screen

    def make_history_screen(self):
        screen = Screen(name="history")
        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))

        title_row = BoxLayout(size_hint_y=None, height=dp(48))
        title_row.add_widget(Label(text="STUDY HISTORY", bold=True, font_size=dp(22)))
        back = Button(text="BACK", size_hint_x=0.25)
        back.bind(on_release=lambda *_: setattr(self.manager, "current", "main"))
        title_row.add_widget(back)
        root.add_widget(title_row)

        scroll = ScrollView()
        self.history_grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=None)
        self.history_grid.bind(minimum_height=self.history_grid.setter("height"))
        scroll.add_widget(self.history_grid)
        root.add_widget(scroll)

        screen.add_widget(root)
        return screen

    def show_history(self):
        self.history_grid.clear_widgets()
        for header in ("Date", "Time", "Subject", "Duration"):
            self.history_grid.add_widget(Label(text=header, bold=True,
                                               size_hint_y=None, height=dp(38)))

        for session in reversed(self.data["sessions"]):
            for value in (
                session.get("date", ""),
                session.get("time", ""),
                session.get("subject", ""),
                self.format_time(session.get("duration", 0))
            ):
                self.history_grid.add_widget(Label(
                    text=str(value), size_hint_y=None, height=dp(36)
                ))
        self.manager.current = "history"

    def reset_today(self):
        self.is_running = False
        self.timer_seconds = 0
        self.current_session_seconds = 0
        self.timer_label.text = "00:00:00"
        self.data["sessions"] = [
            s for s in self.data["sessions"] if s.get("date") != self.today_string()
        ]
        self.save_data()
        self.status_label.text = "Today's data reset"
        self.update_dashboard()

    def on_stop(self):
        if self.current_session_seconds > 0:
            self.save_current_session()
        self.is_running = False
        self.save_data()


if __name__ == "__main__":
    StudyTrackerApp().run()
