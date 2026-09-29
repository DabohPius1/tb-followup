[app]
title = TB Follow-up Calculator
package.name = tbfollowup
package.domain = org.tbfollowup
source.dir = .
source.include_exts = py,json,png,jpg,kv
version = 1.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 0

[android]
android.api = 34
android.minapi = 23
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
