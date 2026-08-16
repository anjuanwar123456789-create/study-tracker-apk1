[app]
title = Study Tracker
package.name = studytracker
package.domain = org.studytracker
source.dir = .
source.include_exts = py,json,png,jpg,kv
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 35
minapi = 23
archs = arm64-v8a, armeabi-v7a
accept_sdk_license = True
