from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from .models import Template


@receiver(pre_delete, sender=Template)
def template_model_delete(sender, instance, **kwargs):
    if instance.template:
        try:
            instance.template.delete(False)
        except Exception as e:
            print(e)
