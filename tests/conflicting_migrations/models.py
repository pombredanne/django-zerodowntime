from django.db import models


class UnsafeModel(models.Model):
    name = models.CharField(max_length=100)
    some_date = models.DateTimeField(auto_now=True)

    field_added = models.IntegerField()
