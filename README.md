# Study Tracker — Kivy Android Project

This project converts the original Tkinter Study Tracker into a Kivy app suitable for Android packaging.

## Included features
- 12 subjects from the original app
- Start / Pause / Stop timer
- Timer resets when the subject changes
- 360-minute daily goal
- Daily progress bar and percentage
- Today and total study hours
- Subject dashboard
- Study history
- Reset today's data
- Automatic JSON data saving inside the app's Android user-data directory

## Build the APK on a computer

1. Install Python 3 and Buildozer on Linux/WSL.
2. Open a terminal in this project folder.
3. Run:

```bash
buildozer android debug
```

4. The APK will be created in the `bin/` folder.

For a release build later:

```bash
buildozer android release
```

The original Tkinter code is not used directly because Tkinter is a desktop GUI toolkit. The Android version uses Kivy widgets and Kivy's Clock for the timer.
