"""
    pygments.__main__
    ~~~~~~~~~~~~~~~~~

    Main entry point for ``python -m pygments``.

    :copyright: Copyright 2006-2024 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import sys
from fetchcode.vcs.pip._vendor.pygments.cmdline import main

try:
    sys.exit(main(sys.argv))
except KeyboardInterrupt:
    sys.exit(1)
