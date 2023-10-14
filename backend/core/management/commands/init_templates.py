import json
import os
from typing import Dict, List

from django.core.files import File
from django.core.management import BaseCommand

from backend.settings import INITIAL_DATA_DIR
from documents.models import Template, TemplateField, TemplateFieldGroup

ALREADY_LOADED_MESSAGE: str = """
Шаблон с именем '{}' уже существует!
Вы можете:
    1) Полностью обновить данные (существующий шаблон и его поля будут удалены)
    2) Добавить новый шаблон, оставив старый шаблон в базе
иначе) Оставить таблицу без изменения (не загружать новый файл шаблона)
Ваш выбор (1 или 2): """

MESSAGE_TEMPLATE_LOAD: str = "Загрузка шаблона '{}'"
MESSAGE_TEMPLATE_LOADED: str = "Шаблон '{}' загружен"
MESSAGE_LOAD_FINISHED: str = "Загрузка завершена. Загружено {} шаблонов."
MESSAGE_FILE_NOT_FOUND: str = "Файл '{}' не найден."
MESSAGE_UNKNOWN_GROUP_ID: str = "Ошибка: неизвестный идентификатор группы '{}'"
TEMPLATE_LIST_SOURCE_FILE: str = "template_list.json"


def create_field_groups(
    group_list: List[Dict], template: Template
) -> Dict[int, TemplateFieldGroup]:
    """Создание групп из заданного списка."""
    group_list.sort(key=lambda x: x["id"])
    group_models = {}
    for group in group_list:
        id = group.get("id")
        name = group.get("name")
        model = TemplateFieldGroup(name=name, template=template)
        model.save()
        group_models[id] = model
    return group_models


def create_template_fields(
    fields: List[Dict], template: Template, groups: List[Dict]
):
    """Создание полей для шаблона."""

    template_fields = []
    for field in fields:
        group_id = field.pop("group")
        group = None
        if group_id:
            group = groups.get(group_id)
            if not group:
                print(MESSAGE_UNKNOWN_GROUP_ID.format(group_id))
        template_fields.append(
            TemplateField(template=template, group=group, **field)
        )
    TemplateField.objects.bulk_create(template_fields)


def load_template(docx_file_name, json_file_name):
    print(MESSAGE_TEMPLATE_LOAD.format(docx_file_name))
    if not os.path.isfile(docx_file_name):
        print(MESSAGE_FILE_NOT_FOUND.format(docx_file_name))
        return 0
    if not os.path.isfile(json_file_name):
        print(MESSAGE_FILE_NOT_FOUND.format(json_file_name))
        return 0
    with open(json_file_name, encoding="utf-8") as jsonfile:
        context = json.load(jsonfile)
        fields = context.pop("fields")
        groups_list = context.pop("groups")
        name = context.get("name")
        new_docx_name = context.pop("template")
        qs = Template.objects.filter(name=name)
        if qs.exists():
            print(ALREADY_LOADED_MESSAGE.format(name), end="")
            choice = input()
            if choice == "1":
                qs.delete()
            elif choice != "2":
                return 0
        try:
            template = Template(template=docx_file_name, **context)
            template.save()
            with open(docx_file_name, "rb") as f:
                template.template.save(new_docx_name, File(f))
        except Exception as e:
            print("Error for data {}".format(context))
            print(e)
            return 0
        field_groups = create_field_groups(groups_list, template)
        create_template_fields(fields, template, field_groups)
        print(MESSAGE_TEMPLATE_LOADED.format(docx_file_name))
        return 1


class Command(BaseCommand):
    help = "Загрузка данных о шаблонах из /data/"

    def handle(self, *args, **options):
        template_dicts = {}
        with open(
            os.path.join(INITIAL_DATA_DIR, TEMPLATE_LIST_SOURCE_FILE),
            "rt",
            encoding="utf-8",
        ) as file:
            template_dicts = json.load(file)

        records_loaded = 0
        for item in template_dicts:
            fdocx = os.path.join(INITIAL_DATA_DIR, item.get("template"))
            fjson = os.path.join(INITIAL_DATA_DIR, item.get("fields"))
            records_loaded += load_template(fdocx, fjson)
        print(self.style.SUCCESS(MESSAGE_LOAD_FINISHED.format(records_loaded)))
