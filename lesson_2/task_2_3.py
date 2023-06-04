import yaml

from yaml.loader import Loader


"""  
3. Задание на закрепление знаний по модулю yaml. Написать скрипт,
автоматизирующий сохранение данных в файле YAML-формата. Для этого:

Подготовить данные для записи в виде словаря, в котором первому ключу
соответствует список, второму — целое число, третьему — вложенный словарь,
где знач-ение каждого ключа — это целое число с юникод-символом, отсутствующим
в кодировке ASCII (например, €);
Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
При этом обеспечить стилизацию файла с помощью параметра
default_flow_style, а также установить возможность работы с юникодом:
allow_unicode = True;
Реализовать считывание данных из созданного файла и проверить, совпадают ли они
с исходными.
"""


def write_to_yaml(some_dict):
    with open('file.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(some_dict, f, default_flow_style=False, allow_unicode=True)


if __name__ == "__main__":
    prepared_data = {
        'first_key': ['first_value', 'second_value', 123, 255,],
        'second_key': 55,
        'third_key': {
            'currency': '100€',
            'billing': '100$',
        }
    }

    write_to_yaml(prepared_data)
    with open('file.yaml', 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader)

        for key, value in prepared_data.items():
            assert value == data[key]