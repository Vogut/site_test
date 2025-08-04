from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import *
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from read_statistics.models import ReadNumExpandMethod,ReadDetail
# Create your models here.
class BlogType(models.Model):
    type_name=models.CharField(max_length=15)

    def __str__(self) -> str:
        return self.type_name
    
class Blog(models.Model,ReadNumExpandMethod):
    title = models.CharField(max_length=50)
    blog_type=models.ForeignKey(to=BlogType,on_delete=models.CASCADE)
    content=RichTextUploadingField()
    author = models.ForeignKey(to=User,on_delete=models.CASCADE)
    created_time=models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now=True)
    read_details = GenericRelation(ReadDetail)
   
    def get_url(self):
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})

    def get_email(self):
        return self.author.email
    
    def __str__(self) -> str:
        return f"<Blog: {self.title}>"
    
    class Meta:
        ordering=['-created_time']

