from import_export import resources
from .models import *

class CandidateResource(resources.ModelResource):
    class meta:
        model = candidate