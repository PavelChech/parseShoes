import re


def get_digits_from_str(string):
    # Используем для выделения числа из цены
    digits = string.replace('\xa0', '')
    digits = float(re.search(r'\d+', digits).group(0))
    return digits


def clear_list_from_spaces(other_list):
    # Очистить элементы (строки) списка от пробелов
    new_list = []
    [new_list.append(elem.replace('\n', '').strip()) for elem in other_list]
    return new_list


def remove_empty_strs(other_list):
    new_list = []
    [new_list.append(string) for string in other_list if string]
    return new_list
