import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'packages': ["os"],

    }
}

executables = [
    Executable('ide.py', base=base)
]

setup(name='MIPS_ide',
      version='0.1',
      description='naive ide for mips',
      options=options,
      executables=executables
      )
