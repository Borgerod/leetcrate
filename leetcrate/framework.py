"""framework.py

Handles creation and updating of the user's workspace folder structure
(the "framework"). The required folders (problems/) are always created;
optional folders (contests/, courses/, interview/) are controlled by
settings.INI.
"""

import os
import shutil
from importlib.resources import files as pkg_files

FRAMEWORK_DIRS: dict[str, list[str] | dict[str, list[str]]] = {
    'required': [
        'problems/completed',
        'problems/incomplete',
    ],
    'optional': {
        'contests': ['contests/bi_weekly', 'contests/weekly'],
        'courses': ['courses'],
        'interview': ['interview/mock_assessment', 'interview/online_interview'],
    },
}


def create_framework(include: dict[str, bool]) -> None:
    """Create the full workspace framework in the current working directory.

    Always creates the required ``problems/completed`` and
    ``problems/incomplete`` folders. Optional folders are created based
    on the ``include`` argument. Also copies ``settings.INI`` from the
    package template if it does not already exist.

    Args:
        include: Dict mapping optional folder keys
            (``contests``, ``courses``, ``interview``) to booleans.
    """
    for d in FRAMEWORK_DIRS['required']:  # type: ignore[union-attr]
        os.makedirs(d, exist_ok=True)
        _touch_init(d)
        print(f"✓ Created: {d}")

    for key, dirs in FRAMEWORK_DIRS['optional'].items():  # type: ignore[union-attr]
        if include.get(key, False):
            for d in dirs:  # type: ignore[union-attr]
                os.makedirs(d, exist_ok=True)
                print(f"✓ Created: {d}")

    _copy_settings_template()

    root_init = '__init__.py'
    if not os.path.exists(root_init):
        open(root_init, 'w', encoding='utf-8').close()

    print("\n✓ Framework created successfully.")


def update_framework(settings: dict[str, bool | str]) -> None:
    """Add any missing optional folders based on current settings.INI values.

    Existing folders are never modified or deleted. Only creates folders
    that are enabled in settings but not yet present on disk.

    Args:
        settings: Settings dict as returned by :func:`~config.read_settings`.
    """
    for key, dirs in FRAMEWORK_DIRS['optional'].items():  # type: ignore[union-attr]
        if settings.get(key, False):
            for d in dirs:  # type: ignore[union-attr]
                if not os.path.exists(d):
                    os.makedirs(d, exist_ok=True)
                    print(f"✓ Created: {d}")
                else:
                    print(f"  Skipped (exists): {d}")

    print("\n✓ Framework updated.")


def _touch_init(path: str) -> None:
    init_path = os.path.join(path, '__init__.py')
    if not os.path.exists(init_path):
        open(init_path, 'w', encoding='utf-8').close()


def _copy_settings_template() -> None:
    if os.path.exists('settings.INI'):
        print("  Skipped settings.INI (already exists)")
        return
    template = pkg_files('leetcrate.templates').joinpath('settings.INI')
    shutil.copy(str(template), 'settings.INI')
    print("✓ Created settings.INI")
