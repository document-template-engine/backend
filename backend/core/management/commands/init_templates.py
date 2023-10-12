import json
import os

from django.core.files import File
from django.core.management import BaseCommand

from backend.settings import INITIAL_DATA_DIR
from documents.models import Template, TemplateField

ALREADY_LOADED_MESSAGE: str = """
Шаблон с именем {} уже существует!
Вы можете:
    1) Полностью обновить данные (существующий шаблон и его поля будут удалены)
    2) Добавить новый шаблон
иначе) Оставить таблицу без изменения
Ваш выбор (1 или 2): """

MESSAGE_TEMPLATE_LOAD: str = "Загрузка шаблона {}"
MESSAGE_TEMPLATE_LOADED: str = "Шаблон {} загружен"
MESSAGE_LOAD_FINISHED: str = "Загрузка завершена. Загружено {} шаблонов."
MESSAGE_FILE_NOT_FOUND: str = "Файл {} не найден."


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
        template_fields = [
            TemplateField(template_id=template, **field) for field in fields
        ]
        TemplateField.objects.bulk_create(template_fields)
        print(MESSAGE_TEMPLATE_LOADED.format(docx_file_name))
        return 1


template_names = (
    ("заявление_детсад_tpl.docx", "заявление_детсад_tpl.json"),
    ("заявление_на_отпуск_tpl.docx", "заявление_на_отпуск_tpl.json"),
)


class Command(BaseCommand):
    help = "Загрузка данных о шаблонах из /data/"

    def handle(self, *args, **options):
        records_loaded = 0
        for fdocx, fjson in template_names:
            fdocx = os.path.join(INITIAL_DATA_DIR, fdocx)
            fjson = os.path.join(INITIAL_DATA_DIR, fjson)
            records_loaded += load_template(fdocx, fjson)
        print(self.style.SUCCESS(MESSAGE_LOAD_FINISHED.format(records_loaded)))
