import os
import re
import sys
import json
import requests
from html.parser import HTMLParser

from generators import GENERATOR_MAP
from generators.utils import TestCaseGenerator, SourceControlGenerator

class HTMLFilter(HTMLParser):
    """Remove HTML tags from description."""

    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.text.append('\n')
        elif tag in ['p', 'div']:
            self.text.append('\n')

    def handle_endtag(self, tag):
        if tag in ['p', 'div']:
            self.text.append('\n')

    def get_text(self):
        return ''.join(self.text)


def clean_html(html_text):
    """Remove HTML tags from description and format nicely."""
    parser = HTMLFilter()
    parser.feed(html_text or '')
    text = parser.get_text().strip()

    lines = text.split('\n')
    formatted_lines = []
    in_example = False
    in_constraints = False

    def wrap_text(source, width=100, indent_level=0):
        if not source.strip():
            return ['']

        words = source.split()
        wrapped_lines = []
        current_line = ''
        indent = '    ' * indent_level

        for word in words:
            candidate = current_line + (' ' if current_line else '') + word
            if len(indent + candidate) <= width:
                current_line = candidate
            else:
                if current_line:
                    wrapped_lines.append(indent + current_line)
                current_line = word

        if current_line:
            wrapped_lines.append(indent + current_line)

        return wrapped_lines or ['']

    for line in lines:
        line = line.strip()

        if not line:
            formatted_lines.append('')
            continue

        if line.startswith('Example ') and line.endswith(':'):
            in_example = True
            in_constraints = False
            formatted_lines.append(line)
            continue
        if line.lower().startswith('constraint') and ':' in line:
            in_example = False
            in_constraints = True
            formatted_lines.append(line)
            continue

        if line.startswith(('Input:', 'Output:', 'Explanation:')):
            formatted_lines.append(f'    {line}')
            continue

        if line.replace(' ', '').replace('\t', '').isdigit():
            continue

        if in_example:
            wrapped = wrap_text(line, indent_level=1)
            formatted_lines.extend(wrapped)
        elif in_constraints:
            wrapped = wrap_text(line, indent_level=1)
            formatted_lines.extend(wrapped)
        else:
            wrapped = wrap_text(line, indent_level=0)
            formatted_lines.extend(wrapped)

    final_lines = []
    empty_count = 0

    for line in formatted_lines:
        if not line.strip():
            empty_count += 1
            if empty_count <= 1:
                final_lines.append(line)
        else:
            empty_count = 0
            final_lines.append(line)

    return '\n'.join(final_lines)


def read_settings():
    """Read preferred language from settings.INI file."""
    settings = {'language': 'python'}
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

        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip().lower()
            value = value.strip()

            if key == 'language':
                lang_value = value.lower()
                if lang_value == 'c++':
                    lang_value = 'cpp'
                settings['language'] = lang_value
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Warning: Could not read settings.INI: {exc}")
        print("Using default language: python")

    return settings


def get_vscode_settings():
    """Get VS Code indentation settings."""
    defaults = {
        'insert_spaces': True,
        'tab_size': 4,
        'indent_string': '    ',
    }

    workspace_settings_path = os.path.join('.vscode', 'settings.json')
    user_settings_path = os.path.expanduser('~/AppData/Roaming/Code/User/settings.json')

    def read_settings_file(path):
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


def fetch_leetcode_problem(problem_slug, preferred_language='python'):
    """Fetch problem data using LeetCode's GraphQL API."""
    language_map = {
        'python': 'Python3',
        'java': 'Java',
        'cpp': 'C++',
        'javascript': 'JavaScript',
        'go': 'Go',
    }

    leetcode_lang = language_map.get(preferred_language.lower(), 'Python3')

    url = 'https://leetcode.com/graphql'
    query = """
    query getQuestionDetail($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId
            questionFrontendId
            title
            titleSlug
            difficulty
            content
            topicTags {
                name
                slug
            }
            codeSnippets {
                lang
                code
            }
            exampleTestcases
        }
    }
    """

    variables = {"titleSlug": problem_slug}
    headers = {
        'Content-Type': 'application/json',
        'Referer': 'https://leetcode.com',
    }

    try:
        response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        print(f"Error fetching data: {exc}")
        return None

    if 'errors' in data:
        print(f"API Error: {data['errors']}")
        return None

    question = data.get('data', {}).get('question')
    if not question:
        print('No question data returned.')
        return None

    target_code = None
    for snippet in question.get('codeSnippets', []):
        if snippet.get('lang') == leetcode_lang:
            target_code = snippet.get('code')
            break

    if not target_code:
        print(f"No {leetcode_lang} code snippet found")
        return None

    if preferred_language.lower() == 'python':
        target_code = re.sub(r'\bList\[', 'list[', target_code)
        target_code = re.sub(r'\bDict\[', 'dict[', target_code)
        target_code = re.sub(r'\bSet\[', 'set[', target_code)
        target_code = re.sub(r'\bTuple\[', 'tuple[', target_code)

    function_name = 'solve'
    params = []

    if preferred_language.lower() == 'python':
        func_match = re.search(r'def\s+(?!__init__)(\w+)\s*\(self(?:,\s*(.+?))?\)\s*->', target_code, re.DOTALL)
        if func_match:
            function_name = func_match.group(1)
            if func_match.group(2):
                param_text = func_match.group(2)
                for param in param_text.split(','):
                    name = param.split(':')[0].strip()
                    if name and name != 'self':
                        params.append(name)
    elif preferred_language.lower() == 'javascript':
        func_match = re.search(r'var\s+(\w+)\s*=\s*function\s*\(([^)]*)\)', target_code)
        if func_match:
            function_name = func_match.group(1)
            param_text = func_match.group(2).strip()
            if param_text:
                params = [param.strip() for param in param_text.split(',') if param.strip()]
    elif preferred_language.lower() == 'java':
        func_match = re.search(r'public\s+\w+(?:\[\])?\s+(\w+)\s*\(([^)]*)\)', target_code)
        if func_match:
            function_name = func_match.group(1)
            param_text = func_match.group(2).strip()
            if param_text:
                for param in param_text.split(','):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        params.append(parts[-1])
    elif preferred_language.lower() == 'cpp':
        func_match = re.search(r'(\w+(?:<[^>]+>)?)\s*\*?\s+(\w+)\s*\(([^)]*)\)', target_code)
        if func_match:
            function_name = func_match.group(2)
            param_text = func_match.group(3).strip()
            if param_text:
                for param in param_text.split(','):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        name = parts[-1].replace('&', '').replace('*', '')
                        params.append(name)
    elif preferred_language.lower() == 'go':
        func_match = re.search(r'func\s+(\w+)\s*\(([^)]*)\)', target_code)
        if func_match:
            function_name = func_match.group(1)
            param_text = func_match.group(2).strip()
            if param_text:
                for param in param_text.split(','):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        params.append(parts[0])

    test_cases = question.get('exampleTestcases')
    test_cases = test_cases.split('\n') if test_cases else []

    return {
        'number': question.get('questionFrontendId'),
        'title': f"{question.get('questionFrontendId')}. {question.get('title')}",
        'difficulty': question.get('difficulty'),
        'topics': [tag.get('name') for tag in question.get('topicTags', [])],
        'description': question.get('content'),
        'function_name': function_name,
        'params': params,
        'test_cases': test_cases,
        'code_snippet': target_code,
        'language': preferred_language,
    }


def create_files(data):
    """Create folder structure and files with API data."""
    vscode_settings = get_vscode_settings()
    indent = vscode_settings['indent_string']

    language = data.get('language', 'python').lower()
    generator = GENERATOR_MAP.get(language)
    if generator is None:
        print(f"Warning: No generator found for '{language}', defaulting to python.")
        language = 'python'
        generator = GENERATOR_MAP['python']

    extension_map = {
        'python': '.py',
        'java': '.java',
        'cpp': '.cpp',
        'javascript': '.js',
        'go': '.go',
    }
    file_extension = extension_map.get(language, '.py')

    print(f"Using language: {language}")
    print(
        f"Using indentation: {'spaces' if vscode_settings['insert_spaces'] else 'tabs'} "
        f"(size: {vscode_settings['tab_size']})"
    )

    folder_name = data['title'].replace(' ', '_').replace('.', '')

    title_without_number = re.sub(r'^\d+\s*\.?\s*', '', data['title'])
    file_name = title_without_number.replace(' ', '_').lower() + file_extension

    base_path = os.path.join('problems', 'incomplete', folder_name)
    os.makedirs(base_path, exist_ok=True)

    desc_path = os.path.join(base_path, 'description.txt')

    title_line = f"___ {data['title']} "
    total_width = 100
    remaining_width = max(total_width - len(title_line), 0)
    title_underline = '_' * remaining_width
    bottom_underline = '_' * total_width

    desc_content = (
        f"{title_line}{title_underline}\n"
        f"difficulty: {data['difficulty']}\n"
        f"topics: {', '.join(data['topics'])}\n"
        f"{bottom_underline}\n\n\n"
        f"{clean_html(data['description'])}\n"
    )

    with open(desc_path, 'w', encoding='utf-8') as handle:
        handle.write(desc_content)

    code_path = os.path.join(base_path, file_name)
    code_content = generator(data, indent)
    
    # Generate additional test cases comment
    testcase_comment = TestCaseGenerator.generate_testcase_comment(data, data['description'])
    code_content += testcase_comment
    
    # Generate GitHub push comment template
    github_comment = SourceControlGenerator.generate_github_push_comment(data)
    code_content += github_comment

    with open(code_path, 'w', encoding='utf-8') as handle:
        handle.write(code_content)

    print(f"✓ Created folder: {folder_name}")
    print("✓ Created files:")
    print(f"  - {desc_path}")
    print(f"  - {code_path}")
    print(f"\nTitle: {data['title']}")
    print(f"Difficulty: {data['difficulty']}")
    print(f"Topics: {', '.join(data['topics'])}")
    print(f"Function: {data['function_name']}")
    print(f"Parameters: {', '.join(data['params'])}")

    return base_path


if __name__ == '__main__':
    settings = read_settings()
    preferred_language = settings['language']

    print(f"Using preferred language: {preferred_language}")

    if len(sys.argv) < 2:
        url_or_slug = input('Enter LeetCode problem URL or slug: ')
    else:
        url_or_slug = sys.argv[1]

    if 'leetcode.com' in url_or_slug:
        slug_match = re.search(r'/problems/([^/]+)', url_or_slug)
        problem_slug = slug_match.group(1) if slug_match else url_or_slug
    else:
        problem_slug = url_or_slug

    print(f"Fetching problem: {problem_slug}...")
    data = fetch_leetcode_problem(problem_slug, preferred_language)

    if data:
        base_path = create_files(data)
        print(f"\nFolder succsessfully generated!\n    Folder is located at: {base_path}\n")
    else:
        print('Failed to fetch problem data')
