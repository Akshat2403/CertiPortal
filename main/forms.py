import datetime
from django import forms
from .choices import *
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import RegexValidator, EmailValidator


alcher_id_validator = RegexValidator(r"ALC-[A-Z]{3}-[0-9]+", "Alcher ID should be of the form ALC-AAA-12")
email_validator = EmailValidator()
def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)

def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


class CandidForm(forms.Form):
    alcher_id = forms.CharField(max_length=20, validators = [alcher_id_validator])
    name = forms.CharField(max_length=100)
    certificate_type = forms.CharField(
        max_length=2,
        widget=forms.Select(choices=CERTIFICATE_OPTIONS),
    )
    position = forms.IntegerField(
        initial=1, validators=[MinValueValidator(0), MaxValueValidator(3)])
    college = forms.CharField(max_length=255)
    event = forms.CharField(
        max_length=50,
        widget=forms.Select(choices=EVENT_OPTIONS),
    )
    email = forms.EmailField(max_length=70, required = True, validators = [email_validator])
    year = forms.IntegerField(
        initial=current_year(), validators=[MinValueValidator(1984), max_value_current_year])

    is_valid = forms.BooleanField(initial=True, required=False)
    special_achievement = forms.CharField(max_length = 255, required=False)


class CSVUploadForm(forms.Form):
    file_CSV = forms.FileField(validators=[validate_file_extension]) 
    



