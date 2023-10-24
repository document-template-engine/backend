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
