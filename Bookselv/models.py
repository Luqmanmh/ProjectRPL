from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Folder(models.Model):
  folder_name = models.CharField(max_length=255)
  parent_folder = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
  
class File(models.Model):
  filename = models.CharField(max_length=255)
  file_type = models.CharField(max_length=50)
  size = models.BigIntegerField()
  upload_date = models.DateTimeField(auto_now_add=True)
  folder_root = models.ForeignKey(Folder, null=True, on_delete=models.CASCADE)
  file = models.FileField(upload_to='files/')
  img = models.ImageField(upload_to='static/previews/', null=True, blank=True)

