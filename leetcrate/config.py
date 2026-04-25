"""config.py

Reads and exposes user configuration from settings.INI and VS Code
workspace settings. Consumed by core.py and cli.py.
"""

import os
import json

DEFAULT_SETTINGS: dict[str, str | bool] = {
    'language': 'python',
    'contests': False,
    'courses': False,
    'interview': False,
}


def read_settings() -> dict[str, str | bool]:
    """Read settings.INI from the current working directory.

    Returns a dict with the following keys:

    - ``language`` (str): Target language for code generation.
      One of: ``python``, ``java``, ``javascript``, ``go``, ``cpp``.
    - ``contests`` (bool): Whether the contests folder is enabled.
    - ``courses`` (bool): Whether the courses folder is enabled.
    - ``interview`` (bool): Whether the interview folder is enabled.

    Falls back to :data:`DEFAULT_SETTINGS` if the file is missing or unreadable.
    """
    settings = DEFAULT_SETTINGS.copy()
    settings_path = 'settings.INI'

    if not os.path.exists(settings_path):
        return settings

    try:
        try:
            with open(settings_path, 'r', encoding='utf-8-sig') as handle:
                content = handle.read()
        except UnicodeDecodeError:
            with open(settings_path, 'r', encoding='utf-16') as handle:
                content = handle.read()

        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip().lower()
                continue
            if '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip().lower()
            value = value.strip()

            if key == 'language':
                lang_value = value.lower()
                if lang_value == 'c++':
                    lang_value = 'cpp'
                settings['language'] = lang_value
            elif current_section == 'framework' and key in ('contests', 'courses', 'interview'):
                settings[key] = value.lower() in ('true', '1', 'yes')

    except Exception as exc:
        print(f"Warning: Could not read settings.INI: {exc}")
        print("Using default settings.")

    return settings


def get_vscode_settings() -> dict[str, bool | int | str]:
    """Detect indentation settings from VS Code.

    Checks workspace-level ``.vscode/settings.json`` first, then the user-level
    VS Code settings file. Workspace settings take precedence.

    Returns a dict with:

    - ``insert_spaces`` (bool): True if spaces are used for indentation.
    - ``tab_size`` (int): Number of spaces per indent level.
    - ``indent_string`` (str): The actual indent string to inject into generated code.
    """
    defaults: dict[str, bool | int | str] = {
        'insert_spaces': True,
        'tab_size': 4,
        'indent_string': '    ',
    }

    workspace_settings_path = os.path.join('.vscode', 'settings.json')
    user_settings_path = os.path.expanduser('~/AppData/Roaming/Code/User/settings.json')

    def read_settings_file(path: str) -> dict:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                raw = handle.read()
        except (OSError, UnicodeDecodeError):
            return {}

        filtered = []
        for line in raw.split('\n'):
            if '//' in line:
                line = line.split('//', 1)[0]
            filtered.append(line)
        try:
            return json.loads('\n'.join(filtered))
        except json.JSONDecodeError:
            return {}

    user_settings = read_settings_file(user_settings_path)
    workspace_settings = read_settings_file(workspace_settings_path)

    merged = user_settings.copy()
    merged.update(workspace_settings)

    insert_spaces = merged.get('editor.insertSpaces', defaults['insert_spaces'])
    tab_size = merged.get('editor.tabSize', defaults['tab_size'])

    python_section = merged.get('[python]', {})
    insert_spaces = python_section.get('editor.insertSpaces', insert_spaces)
    tab_size = python_section.get('editor.tabSize', tab_size)

    indent_string = (' ' * tab_size) if insert_spaces else '\t'

    return {
        'insert_spaces': insert_spaces,
        'tab_size': tab_size,
        'indent_string': indent_string,
    }
