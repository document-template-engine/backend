import re
from django.core.exceptions import ValidationError

# Латинские буквы
# Одна заглавная +
# Одна строчная
# Одна цифра
# Один из спецсимволов (!#$%*&@^)
# Длина поля:
# Min 8 символов
# Max 32 символов

def validator_password(value):
    if value.len() > 8 and value < 32:
        raise ValidationError("Пароль должен сожержать больше 8 или меньше 32 символов")
    # if re.search((r'\d'), value) != ""
    return value
