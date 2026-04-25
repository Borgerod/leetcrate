"""python_generator.py

Generates a Python boilerplate solution file for a LeetCode problem.

Handles:
- Typing imports detection from the code snippet
- ListNode uncomment + linked list builder function
- Test runner with OPTION 0 (nodes), OPTION 1 (single input), OPTION 2 (multiple inputs)
"""

import re
from html.parser import HTMLParser


def get_typing_imports(code_snippet: str) -> str:
    # find all class names defined in the code
    class_names = set(re.findall(r'class\s+([A-Z][A-Za-z0-9_]*)\b', code_snippet))
    # find all capitalized type names in type annotations
    type_names = set(re.findall(r':\s*([A-Z][A-Za-z0-9_]*)', code_snippet))
    type_names |= set(re.findall(r'->\s*([A-Z][A-Za-z0-9_]*)', code_snippet))
    # exclude class names
    import_types = [t for t in type_names if t not in class_names]
    if not import_types:
        return ''
    return f"from typing import {', '.join(sorted(import_types))}\n\n"

def generate_boilerplate(data, indent):
    """Generate Python-specific boilerplate code"""
    # Build test cases string
    cases_str = ',\n\t\t'.join([f'{case}' for case in data['test_cases']])
    if not cases_str:
        cases_str = '"TESTCASE"'

    code_snippet = data['code_snippet']
    typing_import = get_typing_imports(code_snippet)
    is_linked_list = 'ListNode' in code_snippet

    if is_linked_list:
        lines = code_snippet.split('\n')
        processed_lines = []
        in_listnode = False
        for line in lines:
            if line.strip() == '# Definition for singly-linked list.':
                continue
            elif line.strip().startswith('# class ListNode:'):
                in_listnode = True
                processed_lines.append(line.lstrip('# ').rstrip())
            elif in_listnode and line.startswith('#'):
                processed_lines.append(line[2:])
            else:
                if in_listnode:
                    processed_lines.append('')
                in_listnode = False
                processed_lines.append(line)
        code_snippet = '\n'.join(processed_lines)

        build_fn = (
            '\n'
            'def build_linked_list(values, pos):\n'
            '    if not values:\n'
            '        return None\n'
            '    nodes = [ListNode(v) for v in values]\n'
            '    for i in range(len(nodes) - 1):\n'
            '        nodes[i].next = nodes[i + 1]\n'
            '    if pos != -1:\n'
            '        nodes[-1].next = nodes[pos]\n'
            '    return nodes[0]\n'
        )
#> OPTION 0 (FOR NODES)
        bottom_boilerplate = f'''
#> OPTION 0 (for Nodes)
{indent}s = Solution()
{indent}for i in range(0, len(cases), 2):
{indent}{indent}vals = cases[i]
{indent}{indent}pos = cases[i + 1]
{indent}{indent}head = build_linked_list(vals, pos)
{indent}{indent}print(f"___ NO.{{i//2}} ___________________________________")
{indent}{indent}print(f"Input: vals={{(str(vals[:10])[:-1] + f', ... {{vals[-1]}}]') if len(vals) > 10 else vals}}, pos={{pos}}")
{indent}{indent}ans = s.{data['function_name']}(head)
{indent}{indent}print(f"Output: {{ans}}\\n")
'''
    else:
    #> OPTION 1 (for single inputs)
        build_fn = ''
        
        if len(data['params']) <= 1:
            param_name = data['params'][0] if data['params'] else 'PARAM'
            bottom_boilerplate = f'''
#> OPTION 1 (FOR SINGLE INPUTS)
{indent}s = Solution()
{indent}for i, {param_name} in enumerate(cases):
{indent}{indent}print(f"___ NO.{{i}} ___________________________________")
{indent}{indent}print(f"Input: {param_name}={{(str({param_name}[:10])[:-1] + f', ... {{{param_name}[-1]}}]') if isinstance({param_name}, list) and len({param_name}) > 10 else {param_name}}}")
{indent}{indent}ans = s.{data['function_name']}({param_name})
{indent}{indent}print(f"Output: {{ans}}\\n")
'''
        else:
        #> OPTION 2 (for multiple inputs)
            param_list = ', '.join(data['params'])
            param_print = ', '.join([f"{p}={{(str({p}[:10])[:-1] + f', ... {{{p}[-1]}}]') if isinstance({p}, list) and len({p}) > 10 else {p}}}" for p in data['params']])
            bottom_boilerplate = f'''
#> OPTION 2 (FOR MULTIPLE INPUTS)
{indent}s = Solution()
{indent}for i in range(0, len(cases), {len(data['params'])}):
'''
            for j, param in enumerate(data['params']):
                bottom_boilerplate += f'\n{indent}{indent}{param} = cases[i+{j}]'
            bottom_boilerplate += f'''
{indent}{indent}print(f"___ NO.{{i}} ___________________________________")
{indent}{indent}print(f"Input: {param_print}")
{indent}{indent}ans = s.{data['function_name']}({param_list})
{indent}{indent}print(f"Output: {{ans}}\\n")
'''

    return f'''{typing_import}{code_snippet}
{indent}{indent}\'\'\'
{indent}{indent}
{indent}{indent}\'\'\'



{indent}{indent}return None



{indent}
{build_fn}
if __name__ == '__main__':

{indent}cases = [
{indent}{indent}{cases_str}
{indent}]
{bottom_boilerplate}
'''