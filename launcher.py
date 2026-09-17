import os
import sys
import shutil


def get_app_directory() -> str:
    """Return the directory containing the executable or source file."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = get_app_directory()
os.chdir(APP_DIR)

# PyInstaller one-file builds extract bundled files to a temporary directory.
# Copy the icon next to the executable so the existing GUI can use it.
if getattr(sys, "frozen", False):
    bundled_icon = os.path.join(sys._MEIPASS, "vault.ico")
    external_icon = os.path.join(APP_DIR, "vault.ico")

    if os.path.exists(bundled_icon) and not os.path.exists(external_icon):
        try:
            shutil.copy2(bundled_icon, external_icon)
        except OSError:
            pass

import app


if __name__ == "__main__":
    app.App().mainloop()
