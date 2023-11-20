import json

from api.v1.serializers import TemplateWriteSerializer
from django.test import TestCase

from core.constants import Messages
from documents.models import Template, TemplateFieldType

duplicate_fields_fixture = {
    "name": "Тестовый шаблон",
    "deleted": False,
    "description": "Тестовый шаблон",
    "fields": [
        {"tag": "tag1", "name": "Поле 1", "type": "str"},
        {"tag": "tag2", "name": "Поле 2", "type": "str"},
        {"tag": "tag1", "name": "Поле 3", "type": "str"},
    ],
    "groups": [],
}

duplicate_group_ids_fixture = {
    "name": "Тестовый шаблон",
    "deleted": False,
    "description": "Тестовый шаблон",
    "fields": [
        {"tag": "tag1", "name": "Поле 1", "type": "str"},
        {"tag": "tag2", "name": "Поле 2", "type": "str"},
        {"tag": "tag3", "name": "Поле 3", "type": "str"},
    ],
    "groups": [
        {"id": 1, "name": "Группа 1"},
        {"id": 2, "name": "Группа 2"},
        {"id": 1, "name": "Группа 3"},
    ],
}

unknown_group_id_fixture = {
    "name": "Тестовый шаблон",
    "deleted": False,
    "description": "Тестовый шаблон",
    "fields": [
        {"tag": "tag1", "name": "Поле 1", "type": "str", "group": 1},
        {"tag": "tag2", "name": "Поле 2", "type": "str", "group": 2},
        {"tag": "tag3", "name": "Поле 3", "type": "str", "group": 3},
    ],
    "groups": [
        {"id": 1, "name": "Группа 1"},
        {"id": 2, "name": "Группа 2"},
    ],
}

valid_template_fixture = {
    "name": "Тестовый шаблон",
    "deleted": False,
    "description": "Тестовый шаблон",
    "fields": [
        {"tag": "tag1", "name": "Поле 1", "type": "str", "group": 1},
        {"tag": "tag2", "name": "Поле 2", "type": "int", "group": 2},
        {"tag": "tag3", "name": "Поле 3", "type": "str", "group": 2},
        {"tag": "tag4", "name": "Поле 4", "type": "int"},
    ],
    "groups": [
        {"id": 1, "name": "Группа 1"},
        {"id": 2, "name": "Группа 2"},
    ],
}

unknown_field_type_fixture = {
    "name": "Тестовый шаблон",
    "deleted": False,
    "description": "Тестовый шаблон",
    "fields": [
        {"tag": "tag1", "name": "Поле 1", "type": "str"},
        {"tag": "tag2", "name": "Поле 2", "type": "int"},
        {"tag": "tag3", "name": "Поле 3", "type": "unknown_type"},
    ],
    "groups": [],
}

templatefieldtype_fixture = [
    {"type": "int", "name": "Целочисленный"},
    {"type": "str", "name": "Строковый"},
]


class Test(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        for data in templatefieldtype_fixture:
            TemplateFieldType.objects.create(**data)

    def test_duplicate_field_tags_is_not_valid(self):
        """Проверка, что дубликатные тэги полей взводят ошибку"""

        serializer = TemplateWriteSerializer(data=duplicate_fields_fixture)
        self.assertFalse(serializer.is_valid())
        pattern = Messages.TEMPLATE_FIELD_TAGS_ARE_NOT_UNIQUE.format(".*")
        self.assertRegex(
            json.dumps(serializer.errors, ensure_ascii=False),
            rf".*{pattern}.*",
        )

    def test_duplicate_group_ids_is_not_valid(self):
        """Проверка, что дубликатные id групп взводят ошибку"""

        serializer = TemplateWriteSerializer(data=duplicate_group_ids_fixture)
        self.assertFalse(serializer.is_valid())
        pattern = Messages.TEMPLATE_GROUP_IDS_ARE_NOT_UNIQUE.format(".*")
        self.assertRegex(
            json.dumps(serializer.errors, ensure_ascii=False),
            rf".*{pattern}.*",
        )

    def test_undefined_field_group_is_not_valid(self):
        """Проверка, что неописанные id групп в полях взводят ошибку"""

        serializer = TemplateWriteSerializer(data=unknown_group_id_fixture)
        self.assertFalse(serializer.is_valid())
        pattern = Messages.UNKNOWN_GROUP_ID.format(".*")
        self.assertRegex(
            json.dumps(serializer.errors, ensure_ascii=False),
            rf".*{pattern}.*",
        )

    def test_unknown_field_type_is_not_valid(self):
        """Проверка, что неописанный тип поля взводит ошибку"""

        serializer = TemplateWriteSerializer(data=unknown_field_type_fixture)
        self.assertFalse(serializer.is_valid())

    def test_valid_template_is_created(self):
        """Проверка, что валидный шаблон успешно создается в базе"""
        Template.objects.all().delete()
        serializer = TemplateWriteSerializer(data=valid_template_fixture)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        fields = valid_template_fixture.pop("fields")
        groups = valid_template_fixture.pop("groups")
        self.assertTrue(
            Template.objects.filter(**valid_template_fixture).exists(),
            "Валидный шаблон в базе не создан",
        )
        template = Template.objects.filter(**valid_template_fixture).first()

        # проверка, что поля созданы и они привязаны к правильной группе
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(
                    template.fields.filter(
                        name=field["name"], tag=field["tag"]
                    ).exists(),
                    "Поле {} для шаблона не создано".format(field),
                )
                field_obj = template.fields.filter(
                    name=field["name"], tag=field["tag"]
                ).first()
                self.assertEqual(
                    field_obj.type.type,
                    field["type"],
                    "Поле {} привязано к неправильному типу".format(field),
                )

        # проверка, что созданы все группы для полей
        for group in groups:
            with self.subTest(group=group, template=template):
                self.assertTrue(
                    template.field_groups.filter(
                        name=(group["name"])
                    ).exists(),
                    "Группа {} для шаблона не создана".format(group),
                )

        # проверка, что поля привязаны к правильным группам
        groups_dct = {}
        for g in groups:
            id = g.pop("id")
            groups_dct[id] = g
        for f in fields:
            if "group" in f:
                f["group"] = groups_dct[f["group"]]

        for field in fields:
            field_obj = template.fields.filter(
                name=field["name"], tag=field["tag"]
            ).first()
            with self.subTest(field=field):
                if "group" in field:
                    self.assertEqual(
                        field_obj.group.name,
                        field["group"]["name"],
                        "Поле {} неправильно привязано к группе".format(field),
                    )
