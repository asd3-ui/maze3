[app]
# Android packaging configuration aligned with the proven maze2 build.
title = Dark Dungeon 3D Chase
package.name = dark_dungeon_3d_chase
package.domain = org.fantasy3dgames
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
# Pin Python to the version supported by the pinned python-for-android Pygame recipe.
requirements = python3==3.10.12,pygame
orientation = landscape
fullscreen = 1
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.private_storage = True
# Use the stable python-for-android release tested by the maze2 build.
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
