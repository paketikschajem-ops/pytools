[app]

title = PyTools
package.name = pytools
package.domain = org.pytools
source.dir = .
source.include_exts = py,pyc,png,jpg,jpeg,kv,atlas
version = 1.0
requirements = python3,kivy,qrcode,pillow
orientation = portrait
icon.filename = %(source.dir)s/icon.png
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 35
android.minapi = 26
android.ndk = 28c
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
