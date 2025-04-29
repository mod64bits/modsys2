from django.db import models
import uuid
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE


class BaseModel(models.Model):
    _safedelete_policy = SOFT_DELETE
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField('Criado em', auto_now_add=True)
    modified = models.DateTimeField('Modificado em', auto_now=True)

    class Meta:
        abstract = True