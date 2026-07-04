import subprocess
import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        root = Path(self.root)
        compilers = [
            "compiler/api/compiler.py",
            "compiler/errors/compiler.py",
            "compiler/methods/compiler.py",
        ]
        for rel in compilers:
            compiler_path = root / rel
            if compiler_path.exists():
                subprocess.run([sys.executable, str(compiler_path)], cwd=root, check=True)
