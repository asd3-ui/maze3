[app]
title = Dark Dungeon 3D Chase
package.name = dark_dungeon_3d_chase
package.domain = org.fantasy3dgames
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,pygame,numpy
icon.filename = %(source.dir)s/icon.png
orientation = landscape
fullscreen = 1
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
