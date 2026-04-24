import re
import random

class TestCaseGenerator:
    #! BROKEN

    def parse_constraints(self, description_text):
        """
        Extract constraints from problem description.
        Returns a dict with constraint information.
        """
        constraints = {
            'array_length': None,
            'value_range': None,
            'string_length': None,
            'allows_negative': False,
            'allows_empty': False,
        }
        
        # Look for common constraint patterns
        lines = description_text.split('\n')
        in_constraints = False
        
        for line in lines:
            line_lower = line.lower()
            
            if 'constraint' in line_lower and ':' in line:
                in_constraints = True
                continue
            
            if not in_constraints:
                continue
            
            # Array/list length: "1 <= nums.length <= 10^4"
            length_match = re.search(r'(\d+)\s*<=?\s*(?:nums?|arr|s|operations?|words?)\.(?:length|size)\s*<=?\s*(\d+(?:\s*\^\s*\d+)?)', line, re.IGNORECASE)
            if length_match:
                min_len = int(length_match.group(1))
                max_len_str = length_match.group(2).replace(' ', '')
                if '^' in max_len_str:
                    base, exp = max_len_str.split('^')
                    max_len = int(base) ** int(exp)
                else:
                    max_len = int(max_len_str)
                constraints['array_length'] = (min_len, max_len)
                if min_len == 0:
                    constraints['allows_empty'] = True
            
            # Value range: "-10^4 <= nums[i] <= 10^4"
            value_match = re.search(r'(-?\d+(?:\s*\^\s*\d+)?)\s*<=?\s*(?:nums?|arr|val|target|x)\[?i?\]?\s*<=?\s*(-?\d+(?:\s*\^\s*\d+)?)', line, re.IGNORECASE)
            if value_match:
                min_val_str = value_match.group(1).replace(' ', '')
                max_val_str = value_match.group(2).replace(' ', '')
                
                if '^' in min_val_str:
                    if min_val_str.startswith('-'):
                        base, exp = min_val_str[1:].split('^')
                        min_val = -(int(base) ** int(exp))
                    else:
                        base, exp = min_val_str.split('^')
                        min_val = int(base) ** int(exp)
                else:
                    min_val = int(min_val_str)
                
                if '^' in max_val_str:
                    base, exp = max_val_str.split('^')
                    max_val = int(base) ** int(exp)
                else:
                    max_val = int(max_val_str)
                
                constraints['value_range'] = (min_val, max_val)
                if min_val < 0:
                    constraints['allows_negative'] = True
            
            # String length: "1 <= s.length <= 100"
            str_len_match = re.search(r'(\d+)\s*<=?\s*s\.length\s*<=?\s*(\d+)', line, re.IGNORECASE)
            if str_len_match:
                min_len = int(str_len_match.group(1))
                max_len = int(str_len_match.group(2))
                constraints['string_length'] = (min_len, max_len)
        
        return constraints


    def generate_edge_case_value(self, constraints, case_type='max'):
        """Generate a single value based on constraints."""
        if not constraints.get('value_range'):
            return 0
        
        min_val, max_val = constraints['value_range']
        
        if case_type == 'max':
            return max_val
        elif case_type == 'min':
            return min_val
        elif case_type == 'zero':
            if min_val <= 0 <= max_val:
                return 0
            return min_val
        elif case_type == 'negative':
            if constraints['allows_negative']:
                return min_val
            return min_val
        elif case_type == 'all_same':
            return random.choice([min_val, max_val, 0 if min_val <= 0 <= max_val else min_val])
        else:
            return random.randint(min_val, max_val)


    def generate_array_testcase(self, constraints, case_type='max'):
        """Generate array-type test case."""
        if not constraints.get('array_length'):
            return [1, 2, 3]
        
        min_len, max_len = constraints['array_length']
        
        if case_type == 'max_length':
            length = min(max_len, 100)  # Cap at 100 for practicality
        elif case_type == 'min_length':
            length = min_len
        elif case_type == 'empty':
            if constraints['allows_empty']:
                return []
            length = min_len
        else:
            length = min(max_len // 2, 50)
        
        # Generate values
        if case_type == 'all_same':
            val = self.generate_edge_case_value(constraints, 'max')
            return [val] * length
        elif case_type == 'all_negative':
            if constraints['allows_negative']:
                val = self.generate_edge_case_value(constraints, 'negative')
                return [val] * length
            return [self.generate_edge_case_value(constraints, 'min')] * length
        elif case_type == 'alternating':
            min_val, max_val = constraints.get('value_range', (0, 10))
            return [max_val if i % 2 == 0 else min_val for i in range(length)]
        else:
            return [self.generate_edge_case_value(constraints, 'random') for _ in range(length)]


    def generate_string_testcase(self, constraints, case_type='max'):
        """Generate string-type test case."""
        if not constraints.get('string_length'):
            return "abc"
        
        min_len, max_len = constraints['string_length']
        
        if case_type == 'max_length':
            length = min(max_len, 100)
        elif case_type == 'min_length':
            length = min_len
        elif case_type == 'empty':
            if constraints['allows_empty']:
                return ""
            length = min_len
        else:
            length = min(max_len // 2, 50)
        
        # Generate string
        if case_type == 'all_same':
            return 'a' * length
        elif case_type == 'alternating':
            return ''.join(['a' if i % 2 == 0 else 'b' for i in range(length)])
        else:
            chars = 'abcdefghijklmnopqrstuvwxyz'
            return ''.join(random.choice(chars) for _ in range(length))


    def generate_additional_testcases(self, data, description_text, original_count):
        """
        Generate additional test cases based on constraints.
        
        Args:
            data: Problem data dict
            description_text: Full description text
            original_count: Number of original test cases
        
        Returns:
            List of additional test cases
        """
        constraints = self.parse_constraints(description_text)
        param_count = len(data.get('params', []))
        
        # Calculate how many additional cases to generate
        if param_count <= 1:
            target_total = 8
            needed = target_total - original_count
        else:
            # Multiple parameters - double the limit
            target_total = 16
            needed = target_total - original_count
        
        if needed <= 0:
            return []
        
        additional_cases = []
        
        # Determine test case types to generate
        case_types = [
            'max_length',
            'min_length',
            'all_same',
            'alternating',
        ]
        
        if constraints['allows_empty']:
            case_types.append('empty')
        
        if constraints['allows_negative']:
            case_types.append('all_negative')
        
        # Analyze original test cases to determine type
        original_cases = data.get('test_cases', [])
        is_array_problem = any('[' in str(case) for case in original_cases)
        is_string_problem = any(isinstance(case, str) and not case.startswith('[') for case in original_cases)
        
        # Generate cases
        for i in range(needed):
            case_type = case_types[i % len(case_types)]
            
            if param_count <= 1:
                # Single parameter
                if is_array_problem:
                    case = self.generate_array_testcase(constraints, case_type)
                elif is_string_problem:
                    case = self.generate_string_testcase(constraints, case_type)
                else:
                    case = self.generate_edge_case_value(constraints, case_type)
                additional_cases.append(case)
            else:
                # Multiple parameters - generate for each
                case_group = []
                for param_idx in range(param_count):
                    if param_idx == 0:  # Usually the main array/string
                        if is_array_problem:
                            case_group.append(self.generate_array_testcase(constraints, case_type))
                        elif is_string_problem:
                            case_group.append(self.generate_string_testcase(constraints, case_type))
                        else:
                            case_group.append(self.generate_edge_case_value(constraints, case_type))
                    else:  # Secondary parameters (like target)
                        case_group.append(self.generate_edge_case_value(constraints, 'random'))
                additional_cases.extend(case_group)
        
        return additional_cases


    def format_testcases_for_submission(self, all_cases, language='python'):
        """Format test cases for submission code (with cases = [...])."""
        if language == 'python':
            formatted = "cases = [\n"
            for case in all_cases:
                formatted += f"    {repr(case)},\n"
            formatted += "]"
            return formatted
        elif language == 'javascript':
            formatted = "const cases = [\n"
            for case in all_cases:
                formatted += f"    {self.json_repr(case)},\n"
            formatted += "];"
            return formatted
        elif language in ['java', 'cpp', 'go']:
            # For compiled languages, just show Python-style for simplicity
            formatted = "// cases = [\n"
            for case in all_cases:
                formatted += f"//     {repr(case)},\n"
            formatted += "// ]"
            return formatted
        return ""


    def format_testcases_for_leetcode(self, all_cases):
        """Format test cases for LeetCode (without commas, brackets)."""
        formatted = ""
        for case in all_cases:
            formatted += f"{repr(case)}\n"
        return formatted


    def json_repr(self, obj):
        """JSON representation for JavaScript."""
        if isinstance(obj, list):
            return '[' + ', '.join(self.json_repr(item) for item in obj) + ']'
        elif isinstance(obj, str):
            return f'"{obj}"'
        else:
            return str(obj)


    @staticmethod
    def generate_testcase_comment(data, description_text):
        """
        Generate the full test case comment block to append to submission file.
        
        Args:
            data: Problem data dict with original test_cases
            description_text: Problem description for constraint parsing
        
        Returns:
            String containing the formatted comment block
        """
        generator = TestCaseGenerator()
        original_cases = data.get('test_cases', [])
        original_count = len(original_cases)
        language = data.get('language', 'python')
        
        # Generate additional cases
        additional = generator.generate_additional_testcases(data, description_text, original_count)
        
        if not additional:
            return ""
        
        # Combine original + additional
        all_cases = original_cases + additional
        
        # Format for submission
        submission_format = generator.format_testcases_for_submission(all_cases, language)
        
        # Format for LeetCode
        leetcode_format = generator.format_testcases_for_leetcode(all_cases)
        
        #! BROKEN - generates wrong comments + does not generate unique test cases. 
        # TODO generates wrong comments
        # TODO does not generate unique test cases. 
        
        # # Build comment block
        # comment = "\n\n'''\n(NEW) TESTCASES:\n"
        # comment += submission_format
        # comment += "\n\nFOR LEETCODE:\n"
        # comment += leetcode_format
        # comment += "'''\n"
        # return comment
        return ""

class SourceControlGenerator:
    @staticmethod
    def generate_github_push_comment(data):
        """
        Generate a GitHub push comment template.
        
        Args:
            data: Problem data dictionary containing title, difficulty, and topics
            
        Returns:
            String containing formatted GitHub push comment
        """
        title = data.get('title', 'Problem')
        difficulty = data.get('difficulty', 'Unknown')
        topics = data.get('topics', [])
        topics_str = ', '.join(topics) if topics else 'None'
        language = data.get('language', 'python').lower()

        # Determine comment style based on language
        if language in ['cpp', 'c++', 'java', 'go', 'javascript', 'js']:
            start_quote = "/*"
            end_quote = "*/"
        else:
            start_quote = '"""'
            end_quote = '"""'
        
        comment_lines = [
            "",
            "",
            start_quote,
            "__ GITHUB PUSH COMMENT _________________________",
            f"Finish {title} + move to completed",
            "contains: description, solution.",
            f"difficulty: {difficulty}",
            f"topics: {topics_str}",
            end_quote
        ]
        
        return "\n".join(comment_lines)
