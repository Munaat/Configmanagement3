import re
import sys
import yaml

class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, text):
        lines = text.split('\n')
        result = {}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('{#'):
                i = self.skip_multiline_comment(lines, i)
            elif line.startswith('struct {'):
                struct_name, struct_value = self.parse_struct(lines, i)
                result[struct_name] = struct_value
                i = self.find_end_of_struct(lines, i)
            elif self.is_constant_declaration(line):
                name, value = self.parse_constant(line)
                self.constants[name] = value
            elif self.is_constant_evaluation(line):
                name = self.parse_constant_evaluation(line)
                if name in self.constants:
                    result[name] = self.constants[name]
                else:
                    raise ValueError(f"Constant '{name}' is not defined")
            i += 1
        return result

    def skip_multiline_comment(self, lines, i):
        while i < len(lines) and not lines[i].strip().endswith('#}'):
            i += 1
        return i

    def parse_struct(self, lines, i):
        struct_name = lines[i].strip().split('{')[0].strip()
        struct_lines = []
        i += 1
        while i < len(lines) and not lines[i].strip().startswith('}'):
            struct_lines.append(lines[i].strip())
            i += 1
        struct_value = self.parse_struct_lines(struct_lines)
        return struct_name, struct_value

    def find_end_of_struct(self, lines, i):
        while i < len(lines) and not lines[i].strip().startswith('}'):
            i += 1
        return i

    def parse_struct_lines(self, lines):
        struct_dict = {}
        for line in lines:
            if '=' in line:
                name, value = line.split('=', 1)
                name = name.strip()
                value = value.strip().rstrip(',')
                if value.startswith("'") and value.endswith("'"):
                    value = value.strip("'")
                elif value.startswith('struct {'):
                    value = self.parse_struct_lines(value[len('struct {'):-1].split(','))
                elif value.startswith('?'):
                    const_name = value[2:-1]
                    if const_name in self.constants:
                        value = self.constants[const_name]
                    else:
                        raise ValueError(f"Constant '{const_name}' is not defined")
                else:
                    value = int(value)
                struct_dict[name] = value
        return struct_dict

    def is_constant_declaration(self, line):
        return re.match(r'^[a-zA-Z][_a-zA-Z0-9]*\s*=\s*.*$', line) is not None

    def parse_constant(self, line):
        name, value = line.split('=', 1)
        name = name.strip()
        value = value.strip()
        if value.startswith("'") and value.endswith("'"):
            value = value.strip("'")
        else:
            value = int(value)
        return name, value

    def is_constant_evaluation(self, line):
        return re.match(r'^\?\([a-zA-Z][_a-zA-Z0-9]*\)$', line) is not None

    def parse_constant_evaluation(self, line):
        return line[2:-1]

def main():
    input_text = sys.stdin.read()
    parser = ConfigParser()
    try:
        result = parser.parse(input_text)
        print(yaml.dump(result, default_flow_style=False))
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
