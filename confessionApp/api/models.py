from django.db import models
from .utils import page_id_generator, page_pin_generator, conf_id_generator
from django.db.models.signals import pre_save
from datetime import datetime, timezone

class Page(models.Model):
    name = models.CharField(max_length=50)
    pageId= models.CharField(unique=True, editable=False,max_length=6)
    pin = models.PositiveSmallIntegerField(editable=False)
    isPublic = models.BooleanField()
    
    @property
    def totalConfessions(self):
        return len(self.confessions.all())

    def __str__(self):
        return (self.name + ' ('+self.pageId +')')

    class Meta:
        ordering = ('pk',)

def pre_save_create_page_id(sender, instance, *args, **kwargs):
    if not instance.pageId:
        instance.pageId=page_id_generator(instance)
    if not instance.pin:
        instance.pin=page_pin_generator(instance)

pre_save.connect(pre_save_create_page_id, sender=Page)


class Confession(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    dateAdded = models.DateTimeField(auto_now_add=True)
    confId= models.CharField(editable=False,max_length=10)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='confessions')
    ownerLiked = models.BooleanField(default=False)

    @property
    def dateAddedText(self):
        x = self.dateAdded
        x=x.replace(tzinfo=timezone.utc).astimezone(tz=None)
        x = x.strftime("%d %b %y (%I:%M %p)")
        return x

    def __str__(self):
        return ('#'+str(self.pk) + ' [ '+str(self.page) +' ]')

    class Meta:
        ordering = ('title',)

def pre_save_create_conf_id(sender, instance, *args, **kwargs):
    if not instance.confId:
        instance.confId=conf_id_generator(instance)
        print(instance.confId)

pre_save.connect(pre_save_create_conf_id, sender=Confession)

