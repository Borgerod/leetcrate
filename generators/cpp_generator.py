import re


LISTNODE_STRUCT = '''struct ListNode {
    int val;
    ListNode *next;
    ListNode(int x) : val(x), next(NULL) {}
};

ListNode* buildLinkedList(vector<int>& vals, int pos) {
    if (vals.empty()) return nullptr;
    ListNode* head = new ListNode(vals[0]);
    ListNode* cur = head;
    ListNode* cycleNode = (pos == 0) ? head : nullptr;
    for (int i = 1; i < (int)vals.size(); i++) {
        cur->next = new ListNode(vals[i]);
        cur = cur->next;
        if (i == pos) cycleNode = cur;
    }
    if (cycleNode) cur->next = cycleNode;
    return head;
}'''


def _infer_cpp_type_and_init(raw: str) -> tuple[str, str]:
    raw = raw.strip()
    if raw.startswith('[['):
        rows = re.findall(r'\[([^\]]*)\]', raw[1:-1])
        row_exprs = ['{' + r + '}' for r in rows]
        return 'vector<vector<int>>', '{' + ', '.join(row_exprs) + '}'
    elif raw.startswith('['):
        inner = raw[1:-1]
        return 'vector<int>', '{' + inner + '}'
    elif raw in ('true', 'false'):
        return 'bool', raw
    elif re.match(r'^-?\d+$', raw):
        return 'int', raw
    else:
        return 'string', '"' + raw + '"'


def _cpp_print_lines(var_name: str, cpp_type: str, ind: str = '    ') -> list[str]:
    if cpp_type == 'vector<int>':
        return [
            f'{ind}cout << "[";',
            f'{ind}if ({var_name}.size() > 10) {{',
            f'{ind}    for (size_t _j = 0; _j < 9; _j++) {{',
            f'{ind}        cout << {var_name}[_j] << ",";',
            f'{ind}    }}',
            f'{ind}    cout << "... " << {var_name}.back();',
            f'{ind}}} else {{',
            f'{ind}    for (size_t _j = 0; _j < {var_name}.size(); _j++) {{',
            f'{ind}        cout << {var_name}[_j];',
            f'{ind}        if (_j + 1 < {var_name}.size()) cout << ",";',
            f'{ind}    }}',
            f'{ind}}}',
            f'{ind}cout << "]";',
        ]
    elif cpp_type == 'vector<vector<int>>':
        return [
            f'{ind}cout << "[";',
            f'{ind}for (size_t _i = 0; _i < {var_name}.size(); _i++) {{',
            f'{ind}    cout << "[";',
            f'{ind}    for (size_t _j = 0; _j < {var_name}[_i].size(); _j++) {{',
            f'{ind}        cout << {var_name}[_i][_j];',
            f'{ind}        if (_j + 1 < {var_name}[_i].size()) cout << ",";',
            f'{ind}    }}',
            f'{ind}    cout << "]";',
            f'{ind}    if (_i + 1 < {var_name}.size()) cout << ",";',
            f'{ind}}}',
            f'{ind}cout << "]";',
        ]
    elif cpp_type == 'bool':
        return [f'{ind}cout << boolalpha << {var_name};']
    else:
        return [f'{ind}cout << {var_name};']


def _extract_cpp_return_type(code_snippet: str, function_name: str) -> str:
    pattern = rf'([\w<>, *]+)\s+{re.escape(function_name)}\s*\('
    match = re.search(pattern, code_snippet)
    if match:
        return match.group(1).strip()
    return 'auto'


def generate_boilerplate(data, indent):
    """Generate C++-specific boilerplate code."""
    code_snippet = data['code_snippet']

    if '{\n        \n    }' in code_snippet:
        code_content = code_snippet.replace('{\n        \n    }', '''{\n        /*\n        \n        */\n        \n        return {};\n    }''')
    elif '{\n        \n}' in code_snippet:
        code_content = code_snippet.replace('{\n        \n}', '''{\n        /*\n        \n        */\n        \n        return {};\n    }''')
    else:
        code_content = code_snippet.rstrip() + '''
        /*
        
        */
        
        return {};
    }'''

    has_listnode = 'ListNode' in code_snippet
    if has_listnode:
        code_content = re.sub(r'^/\*\*.*?\*/\s*', '', code_content, flags=re.DOTALL)

    test_cases = data.get('test_cases', [])
    function_name = data.get('function_name', 'solution')

    if 'two' in data['title'].lower() and 'sum' in data['title'].lower():
        if test_cases and len(test_cases) >= 2:
            cpp_test_cases = []
            for index in range(0, len(test_cases), 2):
                if index + 1 < len(test_cases):
                    array_case = test_cases[index]
                    target_case = test_cases[index + 1]
                    inner_values = array_case[1:-1] if array_case.startswith('[') and array_case.endswith(']') else array_case
                    vector_expr = f'vector<int>{{{inner_values}}}' if inner_values else 'vector<int>{}'
                    cpp_test_cases.append((vector_expr, target_case))
            if cpp_test_cases:
                case_entries = [f'        {{ {vector_expr}, {target} }}' for vector_expr, target in cpp_test_cases]
                cases_str = ',\n'.join(case_entries)
                test_code = f'''    vector<pair<vector<int>, int>> testCases = {{
{cases_str}
    }};
    
    for (int i = 0; i < static_cast<int>(testCases.size()); i++) {{
        vector<int> nums = testCases[i].first;
        int target = testCases[i].second;
        vector<int> result = solution.{function_name}(nums, target);
        cout << "___ NO." << i << " ___________________________________" << endl;
        cout << "Input: [";
        if (nums.size() > 10) {{
            for (size_t j = 0; j < 9; j++) {{
                cout << nums[j] << ",";
            }}
            cout << "... " << nums.back();
        }} else {{
            for (size_t j = 0; j < nums.size(); j++) {{
                cout << nums[j];
                if (j + 1 < nums.size()) cout << ",";
            }}
        }}
        cout << "], " << target << endl;
        cout << "Output: [";
                for (size_t j = 0; j < result.size(); j++) {{
                    cout << result[j];
                    if (j + 1 < result.size()) cout << ",";
                }}
                cout << "]" << endl << endl;
            }}'''

            else:
                test_code = f'''    // No test cases available
    cout << "C++ solution for: {data['title']}" << endl;'''
        else:
            test_code = f'''    // No test cases available
    cout << "C++ solution for: {data['title']}" << endl;'''
    elif test_cases and has_listnode:
        is_cycle_style = (
            len(test_cases) % 2 == 0 and
            all(
                test_cases[i].startswith('[') and re.match(r'^-?\d+$', test_cases[i + 1].strip())
                for i in range(0, len(test_cases), 2)
            )
        )
        if is_cycle_style:
            val_groups = [test_cases[i] for i in range(0, len(test_cases), 2)]
            positions = [test_cases[i + 1].strip() for i in range(0, len(test_cases), 2)]
        else:
            val_groups = test_cases
            positions = ['-1'] * len(test_cases)
        cases_str = ', '.join(
            '{' + v[1:-1] + '}' for v in val_groups
        )
        positions_str = ', '.join(positions)
        ret_type = _extract_cpp_return_type(code_snippet, function_name)
        if 'ListNode' in ret_type:
            print_output_if_list = (
                'while (result) {\n'
                '            cout << result->val << " ";\n'
                '            result = result->next;\n'
                '        }'
            )
        elif 'bool' in ret_type:
            print_output_if_list = 'cout << boolalpha << result;'
        else:
            print_output_if_list = 'cout << result;'
        test_code = f'''    vector<vector<int>> vals = {{{{
        {cases_str}
    }}}};
    vector<int> positions = {{{positions_str}}};

    for (int i = 0; i < (int)vals.size(); i++) {{
        ListNode* head = buildLinkedList(vals[i], positions[i]);
        cout << "___ NO." << i << " ___________________________________" << endl;
        cout << "Input: ";
        if (vals[i].size() > 10) {{
            cout << "[";
            for (int j = 0; j < 6; ++j) cout << vals[i][j] << ",";
            cout << " ..., " << vals[i].back() << "]";
        }} else {{
            for (int v : vals[i]) cout << v << " ";
        }}
        cout << ", pos=" << positions[i] << endl;
        auto result = solution.{function_name}(head);
        cout << "Output: ";
        {print_output_if_list}
        cout << endl << endl;
    }}'''
    elif test_cases and len(data['params']) <= 1:
        cpp_cases = []
        if 'int' in code_snippet and '[]' not in code_snippet:
            vector_type = 'vector<int>'
            cpp_cases = [f'        {case}' for case in test_cases]
        elif 'string' in code_snippet:
            vector_type = 'vector<string>'
            cpp_cases = [f'        "{case}"' for case in test_cases]
        elif 'bool' in code_snippet:
            vector_type = 'vector<bool>'
            cpp_cases = [f'        {case}' for case in test_cases]
        else:
            vector_type = 'vector<string>'
            for case in test_cases:
                if isinstance(case, list):
                    vector_str = '{' + ', '.join(str(value) for value in case) + '}'
                    cpp_cases.append(f'        vector<int>{vector_str}')
                else:
                    cpp_cases.append(f'        {case}')
        test_array = ',\n'.join(cpp_cases)
        test_code = f'''    {vector_type} testCases = {{
{test_array}
    }};
    
   '''
    elif test_cases and len(data['params']) > 1:
        num_params = len(data['params'])
        param_names = data['params']
        groups: list[list[str]] = []
        for idx in range(0, len(test_cases), num_params):
            group = test_cases[idx:idx + num_params]
            if len(group) == num_params:
                groups.append(group)
        if not groups:
            test_code = f'    // No valid test cases\n    cout << "C++ solution for: {data["title"]}" << endl;'
        else:
            param_types = [_infer_cpp_type_and_init(v)[0] for v in groups[0]]
            ret_type = _extract_cpp_return_type(code_snippet, function_name)
            tuple_types = ', '.join(param_types)

            case_entries: list[str] = []
            for group in groups:
                args: list[str] = []
                for raw_val, cpp_type in zip(group, param_types):
                    _, init_val = _infer_cpp_type_and_init(raw_val)
                    args.append(f'{cpp_type}{init_val}' if cpp_type.startswith('vector') else init_val)
                case_entries.append('        make_tuple(' + ', '.join(args) + ')')
            cases_str = ',\n'.join(case_entries)

            unpack_lines: list[str] = []
            for ui, (param_name, cpp_type) in enumerate(zip(param_names, param_types)):
                unpack_lines.append(f'        {cpp_type} {param_name} = get<{ui}>(testCases[i]);')
            unpack_str = '\n'.join(unpack_lines)

            call_args = ', '.join(param_names)
            has_result = 'void' not in ret_type
            call_line = (
                f'        auto result = solution.{function_name}({call_args});'
                if has_result else
                f'        solution.{function_name}({call_args});'
            )

            print_input_lines: list[str] = []
            for pi, (param_name, cpp_type) in enumerate(zip(param_names, param_types)):
                prefix = f', {param_name}=' if pi > 0 else f'{param_name}='
                print_input_lines.append(f'        cout << "{prefix}";')
                print_input_lines.extend(_cpp_print_lines(param_name, cpp_type, ind='        '))
            print_input_str = '\n'.join(print_input_lines)

            loop_inner = (
                f'{unpack_str}\n'
                f'{call_line}\n'
                f'        cout << "___ NO." << i << " ___________________________________" << endl;\n'
                f'        cout << "Input: ";\n'
                f'{print_input_str}\n'
                f'        cout << endl;'
            )
            if has_result:
                print_output_str = '\n'.join(_cpp_print_lines('result', ret_type, ind='        '))
                loop_inner += f'\n        cout << "Output: ";\n{print_output_str}\n        cout << endl << endl;'

            test_code = (
                f'    using TestCase = tuple<{tuple_types}>;\n'
                f'    vector<TestCase> testCases = {{\n{cases_str}\n    }};\n'
                f'    \n'
                f'    for (int i = 0; i < static_cast<int>(testCases.size()); i++) {{\n'
                f'{loop_inner}\n'
                f'    }}'
            )
    else:
        test_code = f'''    // TODO: Add test cases
    cout << "C++ solution for: {data['title']}" << endl;'''

    listnode_block = LISTNODE_STRUCT + '\n\n' if has_listnode else ''

    full_code = f'''#include <iostream>
#include <vector>
#include <string>
#include <utility>
using namespace std;

{listnode_block}{code_content}

int main() {{
    Solution solution;
    
{test_code}
    
    return 0;
}}'''

    return full_code
