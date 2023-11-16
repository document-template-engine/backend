from typing import Final


class Messages:
    """Текстовые сообщения приложения"""

    TABLE_IS_NOT_EMPTY: Final = (
        "Таблица {} не пустая!\n"
        "Вы можете:\n"
        "    1) Обновить все данные (все существующие записи будут удалены)\n"
        "    2) Дополнить таблицу несуществующими записями\n"
        "иначе) Оставить таблицу без изменения\n"
        "Ваш выбор (1 или 2): "
    )
    WRONG_FIELD_AND_GROUP_TEMPLATES: Final = (
        "Объект шаблон для поля и группы не совпадают"
    )
    WRONG_TEMPLATE_FIELD: Final = (
        "Идентификатор поля {} не соответствует шаблону"
    )

    TEMPLATE_ALREADY_DELETED: Final = "Шаблон уже удален ранее"

    TABLE_LOADING: Final = "Обновление таблицы {}"

    LOAD_FINISHED: Final = "Загрузка завершена. Загружено {} записей."

    TEMPLATE_ALREADY_EXISTS: Final = (
        "Шаблон с именем '{}' уже существует!\n"
        "Вы можете:\n"
        "    1) Полностью обновить данные (существующий шаблон и его поля будут удалены)\n"
        "    2) Добавить новый шаблон, оставив старый шаблон в базе\n"
        "иначе) Оставить таблицу без изменения (не загружать новый файл шаблона)\n"
        "Ваш выбор (1 или 2): "
    )

    TEMPLATE_LOADING: Final = "Загрузка шаблона '{}'"
    TEMPLATE_LOADED: Final = "Шаблон '{}' загружен"
    TEMPLATE_LOAD_FINISHED: Final = (
        "Загрузка завершена. Загружено {} шаблонов."
    )
    FILE_NOT_FOUND: Final = "Файл '{}' не найден."
    UNKNOWN_GROUP_ID: Final = "Ошибка: неизвестный идентификатор группы '{}'"
    UNKNOWN_TYPE: Final = "Ошибка: неизвестный тип поля '{}'"

    TEMPLATE_EXCESS_TAGS: Final = (
        "Шаблон содержит тэги, для которых отсутствуют поля в базе"
    )
    TEMPLATE_EXCESS_FIELDS: Final = (
        "В шаблоне отсутствуют тэги, для которых имеются поля в базе"
    )
    TEMPLATE_CONSISTENT: Final = "Шаблон и поля согласованы"
    TEMPLATE_FIELD_TAGS_ARE_NOT_UNIQUE: Final = (
        "Поля шаблона содержат неуникальные теги {}"
    )
    TEMPLATE_GROUP_IDS_ARE_NOT_UNIQUE: Final = (
        "Группы полей шаблона содержат неуникальные идентификаторы id {}"
    )
