"""
Using runpy to run the lowes module as a script without having to
specify the module name. This is the same as running the following command
from the terminal: python -m lowes
"""

import runpy

if __name__ == "__main__":
    runpy.run_module("lowes", run_name="__main__")
