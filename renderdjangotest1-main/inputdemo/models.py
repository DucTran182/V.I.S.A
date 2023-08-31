from django.db import models

class ImageModel(models.Model):
    image = models.TextField(null=True)
    userid = models.IntegerField(null=True)
    command = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
