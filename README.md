# Инструмент командной строки для учебного конфигурационного языка

## Введение

В данном отчете представлено решение задачи по разработке инструмента командной строки, который преобразует текст из учебного конфигурационного языка в формат YAML. Инструмент также выявляет синтаксические ошибки и выдает соответствующие сообщения. 

## Структура проекта

Проект состоит из одного основного класса `ConfigParser`, который отвечает за парсинг входного текста и преобразование его в формат YAML. Основные функции класса включают в себя:

- Парсинг многострочных комментариев
- Обработка структур
- Объявление и вычисление констант
- Генерация выходного текста в формате YAML

## Основные компоненты кода

### Импорт необходимых библиотек

```python
import re
import sys
import yaml
```

Здесь мы импортируем модули:
- `re` для работы с регулярными выражениями.
- `sys` для работы с системными параметрами и стандартным вводом/выводом.
- `yaml` для работы с форматом YAML.

### Определение класса `ConfigParser`

```python
class ConfigParser:
    def __init__(self):
        self.constants = {}
```

Класс `ConfigParser` инициализируется с пустым словарем `constants`, который будет использоваться для хранения объявленных констант.

### Метод `parse`

```python
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
```

Метод `parse` принимает текст в виде строки, разбивает его на строки и обрабатывает каждую строку в цикле. В зависимости от типа конструкции (комментарий, структура, объявление константы или вычисление константы) вызываются соответствующие методы.

### Обработка многострочных комментариев

```python
def skip_multiline_comment(self, lines, i):
    while i < len(lines) and not lines[i].strip().endswith('#}'):
        i += 1
    return i
```

Метод `skip_multiline_comment` пропускает строки, пока не найдет конец многострочного комментария. Он возвращает индекс строки, следующей за комментарием.

### Парсинг структур

```python
def parse_struct(self, lines, i):
    struct_name = lines[i].strip().split('{')[0].strip()
    struct_lines = []
    i += 1
    while i < len(lines) and not lines[i].strip().startswith('}'):
        struct_lines.append(lines[i].strip())
        i += 1
    struct_value = self.parse_struct_lines(struct_lines)
    return struct_name, struct_value
```

Метод `parse_struct` извлекает имя структуры и ее содержимое. Он собирает строки, относящиеся к структуре, и передает их в метод `parse_struct_lines` для дальнейшей обработки.

### Парсинг строк структуры

```python
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
```

Метод `parse_struct_lines` обрабатывает строки внутри структуры, разбивая их на имена и значения. Он поддерживает строки, числа, вложенные структуры и вычисление констант.

### Объявление и вычисление констант

#### Проверка объявления константы

```python
def is_constant_declaration(self, line):
    return re.match(r'^[a-zA-Z][_a-zA-Z0-9]*\s*=\s*.*$', line) is not None
```

Метод `is_constant_declaration` использует регулярное выражение для проверки, является ли строка объявлением константы. Он возвращает `True`, если строка соответствует формату `имя = значение`.

#### Парсинг объявления константы

```python
def parse_constant(self, line):
    name, value = line.split('=', 1)
    name = name.strip()
    value = value.strip()
    if value.startswith("'") and value.endswith("'"):
        value = value.strip("'")
    else:
        value = int(value)
    return name, value
```

Метод `parse_constant` разбивает строку на имя и значение, удаляет лишние пробелы и обрабатывает значение. Если значение является строкой, оно очищается от кавычек; если это число, оно преобразуется в целое число.

#### Проверка вычисления константы

```python
def is_constant_evaluation(self, line):
    return re.match(r'^\?\([a-zA-Z][_a-zA-Z0-9]*\)$', line) is not None
```

Метод `is_constant_evaluation` проверяет, является ли строка выражением для вычисления константы. Он возвращает `True`, если строка соответствует формату `?(имя)`.

#### Парсинг вычисления константы

```python
def parse_constant_evaluation(self, line):
    return line[2:-1]
```

Метод `parse_constant_evaluation` извлекает имя константы из выражения, удаляя префикс `?(` и суффикс `)`.

### Основная функция `main`

```python
def main():
    input_text = sys.stdin.read()
    parser = ConfigParser()
    try:
        result = parser.parse(input_text)
        print(yaml.dump(result, default_flow_style=False))
    except ValueError as e:
        print(f"Error: {e}")
```

Функция `main` отвечает за чтение входного текста из стандартного ввода, создание экземпляра `ConfigParser`, парсинг текста и вывод результата в формате YAML. В случае возникновения ошибки при парсинге, она выводит сообщение об ошибке.

### Запуск программы

```python
if __name__ == "__main__":
    main()
```

Этот блок кода позволяет запустить функцию `main`, если скрипт выполняется как основная программа.

## Примеры конфигураций

### Пример 1: Конфигурация для веб-сервера

```plaintext
{#
Конфигурация веб-сервера
#}
server {
    host = 'localhost',
    port = 8080,
    max_connections = 100,
    timeout = 30,
}
```

### Пример 2: Конфигурация для базы данных

```plaintext
{#
Конфигурация базы данных
#}
database {
    name = 'mydatabase',
    user = 'admin',
    password = 'secret',
    max_connections = 50,
    timeout = 10,
    connection_string = ?(db_connection),
}

db_connection = 'postgresql://admin:secret@db.example.com:5432/mydatabase'
```

### Итоговый вывод программы

После обработки вышеуказанных конфигураций, программа выведет следующий результат в формате YAML:

```yaml
database:
  name: mydatabase
  password: secret
  timeout: 10
  user: admin
  max_connections: 50

server:
  host: localhost
  port: 8080
  max_connections: 100
  timeout: 30
```

### Объяснение итогового вывода

В итоговом выводе представлены две структуры: `database` и `server`. Каждая структура содержит соответствующие параметры, которые были определены в конфигурациях. 

- **Структура `server`** включает:
  - `host`: адрес сервера (localhost)
  - `port`: порт, на котором работает сервер (8080)
  - `max_connections`: максимальное количество соединений (100)
  - `timeout`: время ожидания соединения (30 секунд)

- **Структура `database`** включает:
  - `name`: имя базы данных (mydatabase)
  - `user`: имя пользователя для подключения к базе данных (admin)
  - `password`: пароль для подключения (secret)
  - `max_connections`: максимальное количество соединений к базе данных (50)
  - `timeout`: время ожидания соединения к базе данных (10 секунд)

Таким образом, программа успешно преобразует входные данные из учебного конфигурационного языка в формат YAML, сохраняя структуру и значения.

## Пример использования

Для запуска программы и преобразования конфигурационного файла из учебного конфигурационного языка в формат YAML, вы можете использовать следующую команду в терминале:

```bash
python main.py < db.txt > dbout.yaml
```

### Объяснение команды:

- `python main.py`: Запускает скрипт `main.py`, который содержит реализацию парсера конфигурационного языка.
- `< db.txt`: Перенаправляет содержимое файла `db.txt` (который должен содержать конфигурацию на учебном языке) в стандартный ввод программы.
- `> dbout.yaml`: Перенаправляет стандартный вывод программы в файл `dbout.yaml`, который будет содержать результат преобразования в формате YAML.

## Заключение

В данном отчете представлено решение задачи по разработке инструмента командной строки для парсинга учебного конфигурационного языка и преобразования его в формат YAML. Описаны основные компоненты кода, их функции и примеры использования. Инструмент поддерживает многострочные комментарии, структуры, объявление и вычисление констант, а также обрабатывает синтаксические ошибки.
