import json
import os
from typing import Dict, List

from django.core.files import File
from django.core.management import BaseCommand

from backend.settings import INITIAL_DATA_DIR

from api.v1.serializers import TemplateWriteSerializer
from core.constants import Messages
from documents.models import (
    Template,
    TemplateField,
    TemplateFieldGroup,
    TemplateFieldType,
)

TEMPLATE_LIST_SOURCE_FILE: str = "template_list.json"


def print_red(*args):
    print("\033[31m", end="")
    print(*args, end="")
    print("\033[0m")


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
        type_slug = field.pop("type")
        group = None
        if group_id:
            group = groups.get(group_id)
            if not group:
                print(Messages.UNKNOWN_GROUP_ID.format(group_id))
        if type_slug:
            type = TemplateFieldType.objects.get(type=type_slug)
            if not type:
                print(Messages.UNKNOWN_TYPE.format(type_slug))
        template_fields.append(
            TemplateField(template=template, group=group, type=type, **field)
        )
    TemplateField.objects.bulk_create(template_fields)


def load_template(docx_file_name, json_file_name):
    print("\n")
    print(Messages.TEMPLATE_LOADING.format(docx_file_name))
    if not os.path.isfile(docx_file_name):
        print_red(Messages.FILE_NOT_FOUND.format(docx_file_name))
        return 0
    if not os.path.isfile(json_file_name):
        print_red(Messages.FILE_NOT_FOUND.format(json_file_name))
        return 0
    with open(json_file_name, encoding="utf-8") as jsonfile:
        try:
            context = json.load(jsonfile)
        except Exception as e:
            print_red(Messages.TEMPLATE_JSON_CORRUPTED.format(json_file_name))
            print(e)
            return 0

        new_docx_name = context.pop("template")
        name = context.get("name", None)
        qs = Template.objects.filter(name=name)
        if qs.exists():
            print(Messages.TEMPLATE_ALREADY_EXISTS.format(name), end="")
            choice = input()
            if choice == "1":
                try:
                    qs.delete()
                except Exception as e:
                    print("Error at template delete operation!")
                    print(e)
            elif choice != "2":
                return 0
        try:
            serializer = TemplateWriteSerializer(data=context)
            if not serializer.is_valid():
                print_red(
                    Messages.TEMPLATE_JSON_CORRUPTED.format(json_file_name)
                )
                print_red(serializer.errors)
                return 0
            template = serializer.save()
            with open(docx_file_name, "rb") as f:
                template.template.save(new_docx_name, File(f))

            # проверка консистентности загруженных полей и шаблона docx
            errors = template.get_consistency_errors()
            if errors:
                print_red("Ошибки в шаблоне\n", errors)
        except Exception as e:
            msg = "Error for data {}".format(json.dumps(context))
            print_red(msg)
            print_red(e)
            return 0
        print(Messages.TEMPLATE_LOADED.format(docx_file_name))
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
        print(
            self.style.SUCCESS(
                Messages.TEMPLATE_LOAD_FINISHED.format(records_loaded)
            )
        )
