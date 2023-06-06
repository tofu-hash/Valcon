import re


def add_spaces(number):
    # Преобразование числа в строку
    number_str = str(number)

    # Разделение числа на целую и десятичную части
    parts = number_str.split('.')

    # Добавление пробелов между разрядами в целой части числа
    integer_part = parts[0]
    formatted_integer = '{0:,}'.format(int(integer_part)).replace(',', ' ')

    # Проверка наличия десятичной части
    if len(parts) > 1:
        decimal_part = parts[1]
        formatted_number = formatted_integer + '.' + decimal_part
    else:
        formatted_number = formatted_integer

    return formatted_number


def calculator(expression):
    # Удаление пробелов из выражения
    expression = expression.replace(" ", "")

    # Проверка наличия запрещенных символов в выражении
    if re.search(r"[^\d+\-*/().]", expression):
        raise ValueError("Недопустимые символы в выражении.")

    # Проверка сбалансированности скобок
    if expression.count("(") != expression.count(")"):
        raise ValueError("Несбалансированные скобки в выражении.")

    # Вычисление значения выражения
    try:
        result = eval(expression)
        return result
    except:
        raise ValueError("Некорректное выражение.")
