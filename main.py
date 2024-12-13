import sys
import re
import yaml

# Регулярные выражения для синтаксического анализа
comment_pattern = r'--.*'
array_pattern = r'$$(.*?)$$'
name_pattern = r'[_A-Z][_a-zA-Z0-9]*'
value_pattern = r'(\d+|' + array_pattern + '|' + name_pattern + ')'
assignment_pattern = rf'^{value_pattern}\s*->\s*{name_pattern}$'
constant_pattern = r'^!(\w+)$'

# Хранение констант
constants = {}

def parse_line(line):
    # Удаляем комментарии
    line = re.sub(comment_pattern, '', line).strip()
    if not line:
        return None

    # Проверка на объявление константы
    match = re.match(assignment_pattern, line)
    if match:
        value, name = match.groups()
        constants[name] = parse_value(value)
        return None

    # Проверка на вычисление константы
    match = re.match(constant_pattern, line)
    if match:
        name = match.group(1)
        if name in constants:
            return constants[name]
        else:
            raise ValueError(f"Неизвестная константа: {name}")

    raise ValueError(f"Синтаксическая ошибка: {line}")

def parse_value(value):
    # Проверка на массив
    array_match = re.match(array_pattern, value)
    if array_match:
        items = [parse_value(v.strip()) for v in array_match.group(1).split(',')]
        return items

    # Проверка на число
    if value.isdigit():
        return int(value)

    # Проверка на имя
    if re.match(name_pattern, value):
        return f'!{value}'  # Возвращаем как ссылку на константу

    raise ValueError(f"Некорректное значение: {value}")

def main():
    output = {}
    for line in sys.stdin:
        try:
            result = parse_line(line.strip())
            if result is not None:
                output[line.strip()] = result
        except ValueError as e:
            print(e, file=sys.stderr)

    # Выводим результат в формате YAML
    print(yaml.dump(output, default_flow_style=False))

if __name__ == "__main__":
    main()
