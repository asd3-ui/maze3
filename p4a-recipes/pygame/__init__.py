import os
import sys

from pythonforandroid.recipes.pygame import Pygame2Recipe
from pythonforandroid.toolchain import current_directory
from sh import Command, ErrorReturnCode_1
from pythonforandroid.logger import shprint


class Pygame261Recipe(Pygame2Recipe):
    """Build pygame 2.6.1 with fresh Cython output for Android's CPython."""

    version = "2.6.1"
    url = "https://github.com/pygame/pygame/archive/{version}.tar.gz"

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # pygame 2.6.1's optional Cython sprite extension is not needed by
            # this game and is incompatible with Cython 3.1's parser.
            sprite_pyx = os.path.join("src_c", "cython", "pygame", "_sprite.pyx")
            if os.path.exists(sprite_pyx):
                os.remove(sprite_pyx)

            setup_file = os.path.join("buildconfig", "Setup.Android.SDL2.in")
            if os.path.exists(setup_file):
                with open(setup_file, encoding="utf-8") as stream:
                    setup_text = stream.read()
                setup_text = "\n".join(
                    line for line in setup_text.splitlines()
                    if not line.lstrip().startswith("_sprite ")
                ) + "\n"
                with open(setup_file, "w", encoding="utf-8") as stream:
                    stream.write(setup_text)

    def build_compiled_components(self, arch):
        # p4a's hostpython intentionally does not contain Cython. Generate
        # pygame's C sources with the build runner's pinned Cython 3.1 first;
        # the following hostpython build then compiles only generated C.
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(
                Command(sys.executable),
                "setup.py",
                "cython_only",
                _env=env,
            )
        super().build_compiled_components(arch)


recipe = Pygame261Recipe()
