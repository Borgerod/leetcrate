"""go_generator.py

Generates a Go boilerplate solution file for a LeetCode problem.

Handles:
- ListNode struct + buildLinkedList helper injection
- Go type inference from the function signature for type assertions
- Test runner in ``main()`` with OPTION 0 (linked list), OPTION 1 (single input), OPTION 2 (multiple inputs)
- Flat and nested array literal formatting (``[]int{}``, ``[][]int{}``)
"""

import re


def format_go_case(case: str) -> str:
    """Convert a raw test case string into a valid Go literal."""
    case = case.strip()
    # Nested array: [[1,2],[3,4]] -> [][]int{{1,2},{3,4}}
    if case.startswith('[[') and case.endswith(']]'):
        inner = case[2:-2]
        rows = [r.strip() for r in inner.split('],[')]
        go_rows = ', '.join([f'{{{r}}}' for r in rows])
        return f'[][]int{{{go_rows}}}'
    # Flat array: [1,2,3] -> []int{1,2,3}
    if case.startswith('[') and case.endswith(']'):
        inner = case[1:-1]
        return f'[]int{{{inner}}}'
    return case


def format_go_cases_str(test_cases: list) -> str:
    """Format a flat list of raw test cases into Go-literal lines for a []interface{} array."""
    return ',\n\t\t'.join([format_go_case(c) for c in test_cases]) if test_cases else '"TESTCASE"'


def get_go_return_value(code_snippet: str) -> str:
    """Detect the appropriate default return value from the function signature."""
    # Extract return type from func signature: func name(...) RETURNTYPE {
    match = re.search(r'func\s+\w+\([^)]*\)\s*([\w\[\]\*]+)\s*\{', code_snippet)
    if match:
        return_type = match.group(1).strip()
        if return_type in ('int', 'int32', 'int64'):
            return '0'
        elif return_type == 'bool':
            return 'false'
        elif return_type == 'string':
            return '""'
        elif return_type == 'float64':
            return '0.0'
        elif return_type.startswith('[]') or return_type.startswith('*'):
            return 'nil'
    # Fallback heuristics
    if '*ListNode' in code_snippet or '*TreeNode' in code_snippet:
        return 'nil'
    if '[]' in code_snippet:
        return 'nil'
    if 'bool' in code_snippet:
        return 'false'
    if 'string' in code_snippet:
        return '""'
    return '0'


def generate_boilerplate(data, indent):
    """Generate Go-specific boilerplate code."""
    code_snippet = data['code_snippet']
    is_linked_list = '*ListNode' in code_snippet

    # --- Inject solution body ---
    return_value = get_go_return_value(code_snippet)
    if '{\n    \n}' in code_snippet:
        code_content = code_snippet.replace('{\n    \n}', f'''{{
    /*
    
    */
    
    return {return_value}
}}''')
    else:
        code_content = f'''{code_snippet.rstrip()}
    /*
    
    */
    
    return {return_value}
}}'''

    # --- Build test cases string ---
    test_cases = data.get('test_cases', [])
    cases_str = format_go_cases_str(test_cases)

    params = data.get('params', [])
    func_name = data['function_name']

    # --- ListNode struct + helper (OPTION 0) ---
    if is_linked_list:
        listnode_struct = '''type ListNode struct {
    Val  int
    Next *ListNode
}

func buildLinkedList(values []int, pos int) *ListNode {
    if len(values) == 0 {
        return nil
    }
    nodes := make([]*ListNode, len(values))
    for i, v := range values {
        nodes[i] = &ListNode{Val: v}
    }
    for i := 0; i < len(nodes)-1; i++ {
        nodes[i].Next = nodes[i+1]
    }
    if pos != -1 {
        nodes[len(nodes)-1].Next = nodes[pos]
    }
    return nodes[0]
}

'''
    else:
        listnode_struct = ''

    # --- OPTION 0: Linked list ---
    if is_linked_list:
        test_code = f'''    // OPTION 0 (for LinkedList)
    cases := []interface{{}}{{
        {cases_str},
    }}
    for i := 0; i < len(cases); i += 2 {{
        vals := cases[i].([]int)
        pos := cases[i+1].(int)
        head := buildLinkedList(vals, pos)
        valsStr := fmt.Sprintf("%v", vals)
        if len(vals) > 10 {{
            valsStr = fmt.Sprintf("%v ... %v]", vals[:10], vals[len(vals)-1])
        }}
        fmt.Printf("___ NO.%d ___________________________________\\n", i/2)
        fmt.Printf("Input: vals=%s, pos=%d\\n", valsStr, pos)
        ans := {func_name}(head)
        fmt.Printf("Output: %v\\n\\n", ans)
    }}'''

    elif not test_cases:
        test_code = f'''    // TODO: Add test cases
    fmt.Println("Go solution for: {data['title']}")'''

    elif len(params) <= 1:
        # --- OPTION 1: Single parameter ---
        param_name = params[0] if params else 'testCase'
        test_code = f'''    // OPTION 1 (for single inputs)
    cases := []interface{{}}{{
        {cases_str},
    }}
    for i, {param_name} := range cases {{
        {param_name}Str := fmt.Sprintf("%v", {param_name})
        if slice, ok := {param_name}.([]int); ok && len(slice) > 10 {{
            {param_name}Str = fmt.Sprintf("%v ... %v]", slice[:10], slice[len(slice)-1])
        }}
        fmt.Printf("___ NO.%d ___________________________________\\n", i)
        fmt.Printf("Input: {param_name}=%s\\n", {param_name}Str)
        ans := {func_name}({param_name}.(int))
        fmt.Printf("Output: %v\\n\\n", ans)
    }}'''

    else:
        # --- OPTION 2: Multiple parameters ---
        param_count = len(params)

        # Build testCases array entries
        go_cases = []
        for index in range(0, len(test_cases), param_count):
            case_group = test_cases[index:index + param_count]
            formatted_cases = []
            for case in case_group:
                formatted_cases.append(format_go_case(case))
            go_case = ', '.join(formatted_cases)
            go_cases.append(f'        {{{go_case}}}')
        test_array = ',\n'.join(go_cases)

        # Per-param extraction + truncation print
        param_extractions = ''
        input_prints = ''
        call_args = []

        # Parse param types from the function signature for type assertions
        sig_match = re.search(r'func\s+\w+\(([^)]*)\)', code_snippet)
        sig_types = {}
        if sig_match:
            sig_str = sig_match.group(1)
            # e.g. "nums []int, target int" or "matrix [][]int, target int"
            for part in sig_str.split(','):
                part = part.strip()
                tokens = part.split()
                if len(tokens) >= 2:
                    pname = tokens[0]
                    ptype = ' '.join(tokens[1:])
                    sig_types[pname] = ptype

        for j, param in enumerate(params):
            go_type = sig_types.get(param, 'int')
            param_extractions += f'        {param} := testCases[i][{j}].({go_type})\n'
            input_prints += (
                f'        {param}Str := fmt.Sprintf("%v", {param})\n'
            )
            if go_type.startswith('[]'):
                input_prints += (
                    f'        if len({param}) > 10 {{\n'
                    f'            {param}Str = fmt.Sprintf("%v ... %v]", {param}[:10], {param}[len({param})-1])\n'
                    f'        }}\n'
                )
            call_args.append(param)

        input_fmt = ', '.join([f'{p}=%s' for p in params])
        input_args = ', '.join([f'{p}Str' for p in params])
        call_args_str = ', '.join(call_args)

        test_code = f'''    // OPTION 2 (for multiple inputs)
    testCases := [][]interface{{}}{{
{test_array},
    }}
    for i := range testCases {{
{param_extractions}
{input_prints}        fmt.Printf("___ NO.%d ___________________________________\\n", i)
        fmt.Printf("Input: {input_fmt}\\n", {input_args})
        ans := {func_name}({call_args_str})
        fmt.Printf("Output: %v\\n\\n", ans)
    }}'''

    full_code = f'''package main

import "fmt"

{listnode_struct}{code_content}

func main() {{
{test_code}
}}'''

    return full_code