"""javascript_generator.py

Generates a JavaScript (Node.js) boilerplate solution file for a LeetCode problem.

Handles:
- ListNode uncomment + buildLinkedList helper
- Test runner wrapped in ``if (require.main === module)`` guard
- OPTION 0 (linked list), OPTION 1 (single input), OPTION 2 (multiple inputs)
"""

import re


def generate_boilerplate(data, indent):
    """Generate JavaScript-specific boilerplate code."""
    test_cases = data.get('test_cases', [])
    code_snippet = data['code_snippet']
    is_linked_list = 'ListNode' in code_snippet

    # --- Build cases string ---
    cases_str = ',\n\t\t'.join([f'{case}' for case in test_cases])
    if not cases_str:
        cases_str = '"TESTCASE"'

    # --- Uncomment ListNode block ---
    if is_linked_list:
        lines = code_snippet.split('\n')
        processed_lines = []
        in_listnode = False
        for line in lines:
            if line.strip() == '// Definition for singly-linked list.':
                continue
            elif line.strip().startswith('// function ListNode') or line.strip().startswith('// class ListNode'):
                in_listnode = True
                processed_lines.append(line.lstrip('/ ').rstrip())
            elif in_listnode and line.startswith('//'):
                processed_lines.append(line[2:] if len(line) > 2 else '')
            else:
                if in_listnode:
                    processed_lines.append('')
                in_listnode = False
                processed_lines.append(line)
        code_snippet = '\n'.join(processed_lines)

        build_fn = (
            '\n'
            'function buildLinkedList(values, pos) {\n'
            '    if (!values.length) return null;\n'
            '    const nodes = values.map(v => ({ val: v, next: null }));\n'
            '    for (let i = 0; i < nodes.length - 1; i++) nodes[i].next = nodes[i + 1];\n'
            '    if (pos !== -1) nodes[nodes.length - 1].next = nodes[pos];\n'
            '    return nodes[0];\n'
            '}\n'
        )

        # OPTION 0 (FOR NODES)
        bottom_boilerplate = f'''
// OPTION 0 (for Nodes)
if (require.main === module) {{

{indent}const cases = [
{indent}{indent}{cases_str}
{indent}];

{indent}for (let i = 0; i < cases.length; i += 2) {{
{indent}{indent}const vals = cases[i];
{indent}{indent}const pos = cases[i + 1];
{indent}{indent}const head = buildLinkedList(vals, pos);
{indent}{indent}const valsStr = vals.length > 10 ? \'[\' + vals.slice(0, 10).join(\', \') + `, ... ${{vals[vals.length - 1]}}]` : JSON.stringify(vals);
{indent}{indent}console.log(`___ NO.${{i / 2}} ___________________________________`);
{indent}{indent}console.log(`Input: vals=${{valsStr}}, pos=${{pos}}`);
{indent}{indent}const ans = {data['function_name']}(head);
{indent}{indent}console.log(`Output: ${{ans}}\\n`);
{indent}}}
}}
'''

    else:
        build_fn = ''

        # OPTION 1 (for single inputs)
        if len(data['params']) <= 1:
            param_name = data['params'][0] if data['params'] else 'param'
            bottom_boilerplate = f'''
// OPTION 1 (for single inputs)
if (require.main === module) {{

{indent}const cases = [
{indent}{indent}{cases_str}
{indent}];

{indent}cases.forEach(({param_name}, i) => {{
{indent}{indent}const {param_name}Str = Array.isArray({param_name}) && {param_name}.length > 10 ? \'[\' + {param_name}.slice(0, 10).join(\', \') + `, ... ${{{param_name}[{param_name}.length - 1]}}]` : JSON.stringify({param_name});
{indent}{indent}console.log(`___ NO.${{i}} ___________________________________`);
{indent}{indent}console.log(`Input: {param_name}=${{{param_name}Str}}`);
{indent}{indent}const ans = {data['function_name']}({param_name});
{indent}{indent}console.log(`Output: ${{ans}}\\n`);
{indent}}});
}}
'''

        # OPTION 2 (for multiple inputs)
        else:
            param_count = len(data['params'])
            param_list = ', '.join(data['params'])
            param_print_parts = ', '.join([f'{p}=${{{p}Str}}' for p in data['params']])

            bottom_boilerplate = f'''
// OPTION 2 (for multiple inputs)
if (require.main === module) {{

{indent}const cases = [
{indent}{indent}{cases_str}
{indent}];

{indent}for (let i = 0; i < cases.length; i += {param_count}) {{
'''
            for j, param in enumerate(data['params']):
                bottom_boilerplate += f'{indent}{indent}const {param} = cases[i + {j}];\n'
                bottom_boilerplate += f'{indent}{indent}const {param}Str = Array.isArray({param}) && {param}.length > 10 ? \'[\' + {param}.slice(0, 10).join(\', \') + `, ... ${{{param}[{param}.length - 1]}}]` : JSON.stringify({param});\n'

            bottom_boilerplate += f'''{indent}{indent}console.log(`___ NO.${{i}} ___________________________________`);
{indent}{indent}console.log(`Input: {param_print_parts}`);
{indent}{indent}const ans = {data['function_name']}({param_list});
{indent}{indent}console.log(`Output: ${{ans}}\\n`);
{indent}}}
}}
'''

    # --- Inject comment block into code snippet ---
    comment_block = '    /*\n\n    */\n\n    return null;\n};'

    if '{\n    \n};' in code_snippet:
        code_content = code_snippet.replace('{\n    \n};', '{\n' + comment_block)
    elif '{\n    \n}' in code_snippet:
        code_content = code_snippet.replace('{\n    \n}', '{\n' + comment_block.rstrip(';'))
    else:
        # Fallback: replace last closing brace with comment block
        lines = code_snippet.split('\n')
        for idx in range(len(lines) - 1, -1, -1):
            if lines[idx].strip() in ('}', '};'):
                lines[idx] = comment_block
                break
        code_content = '\n'.join(lines)

    return f'''{code_content}


{build_fn}
{bottom_boilerplate}
'''