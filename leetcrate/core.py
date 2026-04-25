"""core.py

Core logic for fetching LeetCode problems via the GraphQL API and
writing the generated template files to disk.
"""

import os
import re
import json
import requests
from html.parser import HTMLParser

from .config import get_vscode_settings
from .generators import GENERATOR_MAP
from .generators.utils import TestCaseGenerator, SourceControlGenerator


class HTMLFilter(HTMLParser):

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


def clean_html(html_text: str) -> str:
    """Strip HTML tags from a LeetCode problem description and reformat it as plain text.

    Args:
        html_text: Raw HTML string from the LeetCode API.

    Returns:
        A plain-text, line-wrapped string suitable for writing to a ``.txt`` file.
    """
    parser = HTMLFilter()
    parser.feed(html_text or '')
    text = parser.get_text().strip()

    lines = text.split('\n')
    formatted_lines = []
    in_example = False
    in_constraints = False

    def wrap_text(source: str, width: int = 100, indent_level: int = 0) -> list[str]:
        if not source.strip():
            return ['']

        words = source.split()
        wrapped_lines: list[str] = []
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

    final_lines: list[str] = []
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


def fetch_leetcode_problem(problem_slug: str, preferred_language: str = 'python') -> dict | None:
    """Fetch problem data from the LeetCode GraphQL API.

    Args:
        problem_slug: The URL slug of the problem, e.g. ``two-sum``.
        preferred_language: Language to fetch the code snippet for.
            One of: ``python``, ``java``, ``javascript``, ``go``, ``cpp``.

    Returns:
        A dict containing the problem metadata and code snippet, or
        ``None`` if the request fails or the problem is not found.
    """
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
        response = requests.post(
            url,
            json={'query': query, 'variables': variables},
            headers=headers,
            timeout=20,
        )
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
    params: list[str] = []

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

    test_cases_raw = question.get('exampleTestcases')
    test_cases = test_cases_raw.split('\n') if test_cases_raw else []

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


def create_files(data: dict) -> str:
    """Generate the folder structure and template files for a problem.

    Creates ``problems/incomplete/<folder>/`` in the current working directory,
    containing a ``description.txt`` and a language-specific solution file.

    Args:
        data: Problem data dict as returned by :func:`fetch_leetcode_problem`.

    Returns:
        The path to the created problem folder.
    """
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

    testcase_comment = TestCaseGenerator.generate_testcase_comment(data, data['description'])
    code_content += testcase_comment

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
