"""Утилиты."""

import datetime
import io
import pathlib
import subprocess
import tempfile
from typing import Any, Dict, List, Set, Union

from django.core.mail import send_mail

from documents.models import Document, DocumentTemplate, TemplateField


class Util:
    @staticmethod
    def send_email(data):
        send_mail(
            data["email_subject"],
            data["email_body"],
            "draftnikox@rambler.ru",
            [data["to_email"]],
            fail_silently=False,
        )


def get_non_unique_items(items: List[Any]) -> Set[Any]:
    """Возвращает множество неуникальных элементов списка."""
    visited = set()
    non_unique = set()
    for item in items:
        if item not in visited:
            visited.add(item)
        else:
            non_unique.add(item)
    return non_unique


def fill_docx_template_for_document(document: Document) -> io.BytesIO:
    """Создание документа из шаблона."""
    context = {
        docfield.field.tag: docfield.value
        for docfield in document.document_fields.all()
    }
    context_default = {
        field.tag: field.default or field.name
        for field in document.template.fields.all()
    }
    path = document.template.template
    doc = DocumentTemplate(path)
    buffer = doc.get_partial(context, context_default)
    return buffer


def create_document_pdf_for_export(document: Document) -> io.BytesIO:
    """Создание pdf-файла."""
    doc_file = fill_docx_template_for_document(document)
    buffer = convert_file_to_pdf(doc_file)
    return buffer


def convert_file_to_pdf(in_file: io.BytesIO) -> io.BytesIO:
    """Файл в виде строки байт преобразуем в строку байт pdf-файла."""
    with tempfile.NamedTemporaryFile() as output:
        out_file = pathlib.Path(output.name).resolve()
        out_file.write_bytes(in_file.getvalue())
        subprocess.run(
            [
                "soffice",
                "--headless",
                "--invisible",
                "--nologo",
                "--convert-to",
                "pdf",
                "--outdir",
                out_file.parent,
                out_file.absolute(),
            ],
            check=True,
        )
        pdf_file = out_file.with_suffix(".pdf")
        out_buffer = pdf_file.read_bytes()
        pdf_file.unlink(missing_ok=True)
    return out_buffer


def date_iso_to_ddmmyyyy(value: str):
    """Преобразует строку из ISO формата в dd.mm.yyyy"""
    try:
        date = datetime.date.fromisoformat(value)
        return date.strftime("%d.%m.%Y")
    except Exception as e:
        print(e)  # TODO logging
        return value


def custom_fieldtypes_validation(
    validated_data: List[Dict[str, Union[TemplateField, str]]]
):
    """Валидация полей согласно кастомным типам"""
    for data in validated_data:
        field = data["field"]
        if field.type.type == "date":
            data["value"] = date_iso_to_ddmmyyyy(data["value"])
            print("DATE CONVERTED TO ", data["value"])
