from wtforms.validators import ValidationError

class ValueRequired:
    def __init__(self, value, message=None):
        self.value = value
        self.message = message

    def __call__(self, form, field):
        if field.data != self.value:
            raise ValidationError(self.message)
