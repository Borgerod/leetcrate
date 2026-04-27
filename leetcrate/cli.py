"""cli.py

Entry point for the ``leetcode_tool`` command. Registers and dispatches
the following subcommands:

- ``init``     — first-time setup wizard (framework + settings.INI)
- ``update``   — add missing optional folders based on settings.INI
- ``generate`` — fetch a problem from LeetCode and write template files

Run ``leetcode_tool --help`` for full usage.
"""

import re
import os
import shutil
import argparse
from importlib.resources import files as pkg_files

from . import __version__
from .config import read_settings
from .core import fetch_leetcode_problem, create_files
from .framework import create_framework, update_framework


def _resolve_slug(url_or_slug: str) -> str:
    if 'leetcode.com' in url_or_slug:
        slug_match = re.search(r'/problems/([^/]+)', url_or_slug)
        return slug_match.group(1) if slug_match else url_or_slug
    return url_or_slug


def _cmd_init(_args: argparse.Namespace) -> None:
    if os.path.exists('settings.INI'):
        print("settings.INI already exists in this directory.")
        print("Run 'leetcrate update' to update the framework.")
        return

    print("Setting up leetcrate...\n")
    choice = input("Create a framework or just install? [framework/install]: ").strip().lower()

    if choice == 'framework':
        include: dict[str, bool] = {}
        for key in ('contests', 'courses', 'interview'):
            ans = input(f"Include {key}? [y/n]: ").strip().lower()
            include[key] = ans in ('y', 'yes')
        create_framework(include)
    else:
        template = pkg_files('leetcrate.templates').joinpath('settings.INI')
        shutil.copy(str(template), 'settings.INI')
        print("✓ Installed settings.INI")
        print("You can now run 'leetcrate generate <slug>' to generate problems.")


def _cmd_update(_args: argparse.Namespace) -> None:
    if not os.path.exists('settings.INI'):
        print("No settings.INI found. Run 'leetcrate init' first.")
        return
    settings = read_settings()
    update_framework(settings)


def _cmd_generate(args: argparse.Namespace) -> None:
    if not os.path.exists('settings.INI'):
        print("No settings.INI found. Run 'leetcrate init' first.")
        return

    settings = read_settings()
    preferred_language = str(settings['language'])
    print(f"Using preferred language: {preferred_language}")

    url_or_slug: str = args.slug or input('Enter LeetCode problem URL or slug: ')
    problem_slug = _resolve_slug(url_or_slug)

    print(f"Fetching problem: {problem_slug}...")
    data = fetch_leetcode_problem(problem_slug, preferred_language)

    if data:
        base_path = create_files(data)
        print(f"\nFolder successfully generated!\n    Folder is located at: {base_path}\n")
    else:
        print('Failed to fetch problem data')


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='leetcrate',
        description='Generate and organize LeetCode problems.',
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser(
        'init',
        help='First-time setup: create framework and settings.INI',
    )

    subparsers.add_parser(
        'update',
        help='Update the framework based on settings.INI',
    )

    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate a problem template from a LeetCode slug or URL',
    )
    generate_parser.add_argument('slug', nargs='?', help='LeetCode problem slug or URL')

    args = parser.parse_args()

    if args.command == 'init':
        _cmd_init(args)
    elif args.command == 'update':
        _cmd_update(args)
    elif args.command in ('generate', 'gen', 'get', 'create'):
        _cmd_generate(args)
    else:
        parser.print_help()
