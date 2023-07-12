from django.db import models
from .choices import CERTIFICATE_OPTIONS,EVENT_OPTIONS
from django.forms import ModelForm

# Create your models here.
class candidate(models.Model):
    name = models.CharField(max_length=255 , null=False)
    certificate_type = models.CharField(max_length=30, choices=CERTIFICATE_OPTIONS, default='CA' ,blank = False)
    college = models.CharField(max_length=255 , null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    is_valid = models.BooleanField(default = True)
    event = models.CharField(max_length=50, choices=EVENT_OPTIONS, default='', blank = False)
    email = models.EmailField(max_length=70, blank = False)
    def __str__(self):
        return self.name
    
class CandidForm(ModelForm):
    class Meta:
        model = candidate
        fields = ['name', 'certificate_type', 'event', 'email','college' ]
