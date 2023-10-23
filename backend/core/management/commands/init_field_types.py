import json
import os

from django.core.management import BaseCommand


from backend.settings import INITIAL_DATA_DIR
from documents.models import TemplateFieldType
from core.constants import Messages

TEMPLATE_FIELD_TYPES_FILE: str = "template_field_types.json"


class Command(BaseCommand):
    help = "Загрузка данных о типах полей шаблонов из /data/"

    def handle(self, *args, **options):
        field_type_dicts = {}

        if TemplateFieldType.objects.exists():
            print(
                Messages.TABLE_IS_NOT_EMPTY.format("TemplateFieldType"), end=""
            )
            choice = input()
            if choice == "1":
                TemplateFieldType.objects.all().delete()
            elif choice != "2":
                return
        print(Messages.TABLE_LOADING.format("TemplateFieldType"))
        field_type_dicts = {}
        with open(
            os.path.join(INITIAL_DATA_DIR, TEMPLATE_FIELD_TYPES_FILE),
            "rt",
            encoding="utf-8",
        ) as file:
            field_type_dicts = json.load(file)
        records_loaded = 0
        for record in field_type_dicts:
            type = record.pop("type")
            try:
                obj, created = TemplateFieldType.objects.update_or_create(
                    type=type, defaults=record
                )
                records_loaded += 1
            except Exception as e:
                print("Error:", e)
        print(
            self.style.SUCCESS(Messages.LOAD_FINISHED.format(records_loaded))
        )
