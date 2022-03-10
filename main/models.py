from django.db import models
from django.forms import ModelForm
from .choices import *

# Create your models here.
class candidate(models.Model):
    
    alcher_id = models.CharField(max_length=255 , null=False)
    name = models.CharField(max_length=255 , null=False)
    certificate_type = models.CharField(max_length=30, choices=CERTIFICATE_OPTIONS, default='CA' ,blank = False)
    position = models.IntegerField(default=0, blank=True)
    college = models.CharField(max_length=255 , null=True, blank=True)
    is_generated = models.BooleanField(default = None)
    is_valid = models.BooleanField(default = True)
    certificate_url = models.CharField(max_length=255 , blank=True)
    event = models.CharField(max_length=50, choices=EVENT_OPTIONS, default='', blank = False)
    year = models.IntegerField(default=2020)
    email = models.EmailField(max_length=70, blank = False)
    special_achievement = models.CharField(max_length=255 , default='', blank=True)
    def __str__(self):
        return self.name


class CandidForm(ModelForm):
    class Meta:
        model = candidate
        fields = ['alcher_id', 'name', 'certificate_type', 'event', 'email' ,'year', 'special_achievement' ]




