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
    
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
    if re.match(pattern, value) is None:
        raise ValidationError('Password has incorrecr format.')
    
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
    if re.match(pattern, value) is None:
        raise ValidationError('Password has incorrecr format.')
    
    return value

