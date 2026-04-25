import re


def generate_boilerplate(data, indent):
    """Generate Java-specific boilerplate code."""
    code_snippet = data['code_snippet']
    is_linked_list = 'ListNode' in code_snippet

    # --- Uncomment the ListNode class block ---
    if is_linked_list:
        lines = code_snippet.split('\n')
        processed_lines = []
        in_listnode = False
        skip_javadoc_close = False
        for line in lines:
            stripped = line.strip()
            if stripped == '/**':
                skip_javadoc_close = True
                continue
            if skip_javadoc_close and stripped in ('* Definition for singly-linked list.', '* '):
                continue
            if skip_javadoc_close and stripped == '*/':
                skip_javadoc_close = False
                continue
            if stripped.startswith('* class ListNode') or stripped.startswith('*     class ListNode'):
                in_listnode = True
                processed_lines.append(stripped[2:])
                continue
            if in_listnode:
                if stripped.startswith('*'):
                    processed_lines.append(stripped[2:] if len(stripped) > 2 else '')
                    continue
                else:
                    processed_lines.append('')
                    in_listnode = False
            processed_lines.append(line)
        code_snippet = '\n'.join(processed_lines)

    # --- Extract return type and param types from method signature ---
    sig_match = re.search(r'public\s+([\w\[\]]+)\s+\w+\s*\(([^)]*)\)', code_snippet)
    return_type = sig_match.group(1) if sig_match else 'void'
    raw_params  = sig_match.group(2) if sig_match else ''

    # Parse declared param types from signature: e.g. "int[] nums, int target" -> ['int[]', 'int']
    declared_types = []
    for token in raw_params.split(','):
        token = token.strip()
        if token:
            # type is everything except the last word (param name)
            parts = token.split()
            declared_types.append(parts[0] if len(parts) >= 2 else '')

    primitive_defaults = {
        'int':     '0',
        'long':    '0L',
        'double':  '0.0',
        'float':   '0.0f',
        'boolean': 'false',
        'char':    "'\\0'",
        'byte':    '0',
        'short':   '0',
    }
    return_value = primitive_defaults.get(return_type, 'null')

    # --- Helper: Java literal for a test case value ---
    def to_java_literal(case, declared_type=''):
        case = case.strip()
        if case.startswith('[['):
            inner = case[2:-2]
            rows = [r.strip() for r in inner.split('],[')]
            rows_java = ', '.join(['{' + r + '}' for r in rows])
            return f'new int[][]{{{rows_java}}}'
        elif case.startswith('['):
            inner = case[1:-1]
            return f'new int[]{{{inner}}}'
        elif case.startswith('"'):
            return case  # String literal
        else:
            return case  # scalar: int, boolean, etc.

    # --- Helper: cast expression from declared type ---
    def cast_from_type(declared_type, accessor):
        """Return a cast expression for pulling `accessor` out of an Object array."""
        type_to_cast = {
            'int[][]': f'(int[][]) {accessor}',
            'int[]':   f'(int[]) {accessor}',
            'String':  f'(String) {accessor}',
            'long':    f'(long) {accessor}',
            'double':  f'(double) {accessor}',
            'boolean': f'(boolean) {accessor}',
            'char':    f'(char) {accessor}',
        }
        return type_to_cast.get(declared_type, f'(int) {accessor}')

    # --- Helper: print expression for a value pulled from Object[] or Object[][] ---
    def print_expr(accessor):
        """
        Returns a Java string expression that prints `accessor`,
        handling int[][], int[], and scalars, with truncation at 10 elements.
        """
        return (
            f'({accessor} instanceof int[][])'
            f' ? java.util.Arrays.deepToString((int[][]) {accessor})'
            f' : ({accessor} instanceof int[])'
            f' ? (((int[]) {accessor}).length > 10'
            f'   ? java.util.Arrays.toString(java.util.Arrays.copyOf((int[]) {accessor}, 10)).replace("]", "") + ", ... " + ((int[]) {accessor})[((int[]) {accessor}).length - 1] + "]"'
            f'   : java.util.Arrays.toString((int[]) {accessor}))'
            f' : String.valueOf({accessor})'
        )

    # --- Helper: output print expression ---
    def ans_print_expr():
        if return_type == 'int[][]':
            return 'java.util.Arrays.deepToString((int[][]) ans)'
        elif return_type == 'int[]':
            return 'java.util.Arrays.toString((int[]) ans)'
        else:
            return 'ans'

    # --- Build test runner ---
    test_cases = data.get('test_cases', [])

    # OPTION 0 — Linked list
    if is_linked_list:
        build_fn = '''
    static ListNode buildLinkedList(int[] values, int pos) {
        if (values.length == 0) return null;
        ListNode[] nodes = new ListNode[values.length];
        for (int i = 0; i < values.length; i++) nodes[i] = new ListNode(values[i]);
        for (int i = 0; i < values.length - 1; i++) nodes[i].next = nodes[i + 1];
        if (pos != -1) nodes[values.length - 1].next = nodes[pos];
        return nodes[0];
    }

    static String listNodeToString(ListNode head) {
        StringBuilder sb = new StringBuilder("[");
        java.util.Set<ListNode> seen = new java.util.HashSet<>();
        ListNode cur = head;
        while (cur != null && !seen.contains(cur)) {
            if (sb.length() > 1) sb.append(", ");
            sb.append(cur.val);
            seen.add(cur);
            cur = cur.next;
        }
        if (cur != null) sb.append(", ...(cycle)");
        sb.append("]");
        return sb.toString();
    }
'''
        java_cases = []
        for i in range(0, len(test_cases), 2):
            vals  = test_cases[i].strip()
            pos   = test_cases[i + 1].strip()
            inner = vals[1:-1]
            java_cases.append(f'            {{new int[]{{{inner}}}, {pos}}}')
        test_array = ',\n'.join(java_cases) if java_cases else '            {new int[]{}, -1}'

        test_code = f'''        Object[][] testCases = {{
{test_array}
        }};

        for (int i = 0; i < testCases.length; i++) {{
            int[] vals = (int[]) testCases[i][0];
            int   pos  = (int)   testCases[i][1];
            ListNode head = buildLinkedList(vals, pos);

            String valsStr = vals.length > 10
                ? java.util.Arrays.toString(java.util.Arrays.copyOf(vals, 10)).replace("]", "") + ", ... " + vals[vals.length - 1] + "]"
                : java.util.Arrays.toString(vals);

            System.out.println("___ NO." + i + " ___________________________________");
            System.out.println("Input: vals=" + valsStr + ", pos=" + pos);
            Object ans = solution.{data['function_name']}(head);
            System.out.println("Output: " + {ans_print_expr()});
            System.out.println();
        }}'''

    elif not test_cases:
        build_fn = ''
        test_code = f'''        // TODO: Add test cases
        System.out.println("Java solution for: {data['title']}");'''

    # OPTION 1 — Single param
    elif len(data['params']) <= 1:
        build_fn = ''
        param_name    = data['params'][0] if data['params'] else 'param'
        declared_type = declared_types[0] if declared_types else 'int'
        java_cases    = [f'            {to_java_literal(case, declared_type)}' for case in test_cases]
        test_array    = ',\n'.join(java_cases)
        cast          = cast_from_type(declared_type, 'testCases[i]')

        test_code = f'''        Object[] testCases = {{
{test_array}
        }};

        for (int i = 0; i < testCases.length; i++) {{
            System.out.println("___ NO." + i + " ___________________________________");
            System.out.println("Input: {param_name}=" + ({print_expr('testCases[i]')}));
            Object ans = solution.{data['function_name']}({cast});
            System.out.println("Output: " + {ans_print_expr()});
            System.out.println();
        }}'''

    # OPTION 2 — Multiple params
    else:
        build_fn    = ''
        param_count = len(data['params'])
        grouped_cases = []
        for index in range(0, len(test_cases), param_count):
            case_group = test_cases[index:index + param_count]
            literals   = ', '.join(
                to_java_literal(c, declared_types[j] if j < len(declared_types) else '')
                for j, c in enumerate(case_group)
            )
            grouped_cases.append(f'            {{{literals}}}')
        test_array = ',\n'.join(grouped_cases)

        input_print_parts = ' + ", " + '.join(
            f'"{p}=" + ({print_expr(f"testCases[i][{j}]")})'
            for j, p in enumerate(data['params'])
        )
        call_args = ', '.join(
            cast_from_type(
                declared_types[j] if j < len(declared_types) else 'int',
                f'testCases[i][{j}]'
            )
            for j in range(param_count)
        )

        test_code = f'''        Object[][] testCases = {{
{test_array}
        }};

        for (int i = 0; i < testCases.length; i++) {{
            System.out.println("___ NO." + i + " ___________________________________");
            System.out.println("Input: " + {input_print_parts});
            Object ans = solution.{data['function_name']}({call_args});
            System.out.println("Output: " + {ans_print_expr()});
            System.out.println();
        }}'''

    # --- Splice everything into the code snippet ---
    main_block = f'''{build_fn}
    public static void main(String[] args) {{
        Solution solution = new Solution();

{test_code}
    }}'''

    comment_block = f'''        /*

        */

        return {return_value};
    }}
{main_block}'''

    if '{\n        \n    }' in code_snippet:
        code_content = code_snippet.replace('{\n        \n    }', '{\n' + comment_block)
    else:
        lines = code_snippet.split('\n')
        for index in range(len(lines) - 1, -1, -1):
            if lines[index].strip() == '}':
                lines.insert(index, main_block)
                break
        code_content = '\n'.join(lines)

    # Ensure public class — only substitute if not already public
    if not re.search(r'\bpublic\s+class\s+Solution\b', code_content):
        code_content = re.sub(r'\bclass\s+Solution\b', 'public class Solution', code_content)

    return code_content


