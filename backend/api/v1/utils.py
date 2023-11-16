from typing import Any, List, Set
from django.core.mail import send_mail


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
