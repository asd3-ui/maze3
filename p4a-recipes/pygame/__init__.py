import sys

from pythonforandroid.logger import shprint
from pythonforandroid.recipes.pygame import Pygame2Recipe
from pythonforandroid.toolchain import current_directory
from sh import Command


class Pygame261Recipe(Pygame2Recipe):
    """Build pygame 2.6.1 and generate its Cython sources before compilation."""

    version = "2.6.1"
    url = "https://github.com/pygame/pygame/archive/{version}.tar.gz"

    def build_compiled_components(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # Generate C sources (including _sprite.c) from bundled .pyx files.
            shprint(Command(sys.executable), "setup.py", "cython_only", _env=env)
        super().build_compiled_components(arch)


recipe = Pygame261Recipe()
