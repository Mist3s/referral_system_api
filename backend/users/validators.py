from django.core import validators


class PhoneNumberValidator(validators.RegexValidator):
    regex = r'^7\d{10}$'
    message = (
        'Please enter a phone number starting with 7 followed by 10 digits.'
    )
    flags = 0
