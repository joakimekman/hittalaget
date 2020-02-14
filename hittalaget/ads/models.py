from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.urls import reverse
from hittalaget.players.models import Position
from hittalaget.teams.models import Team


class Ad(models.Model):
    ad_id = models.IntegerField(unique=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    sport = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(max_length=500, verbose_name="beskrivning")
    max_age = models.PositiveIntegerField(verbose_name="ålder")
    min_height = models.PositiveIntegerField(verbose_name="längd")
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="ads")
    min_experience = models.CharField(max_length=255, verbose_name="erfarenhet")
    special_ability = models.CharField(max_length=255, verbose_name="spetsegenskap")


    class Meta:
        indexes = [
            models.Index(fields=['ad_id',]),
        ]

    
    def get_absolute_url(self):
        return reverse("ad:detail", kwargs={"sport": self.sport, "ad_id": self.ad_id, "slug": self.slug})

    def __str__(self):
        return self.title


def pre_save_title(sender, instance, **kwargs):
    instance.title = "{} söker {}".format(
        instance.team,
        instance.position
    )
    
def pre_save_slug(sender, instance, **kwargs):
    instance.slug = slugify(instance.title)

def pre_save_ad_id(sender, instance, **kwargs):
    from random import randint
    rand_id = randint(100000, 999999)
    
    if not instance.ad_id: 
        while Ad.objects.filter(ad_id=rand_id).exists():
            rand_id = randint(100000, 999999)
        else:
            instance.ad_id = rand_id
    
pre_save.connect(pre_save_title, sender=Ad)
pre_save.connect(pre_save_slug, sender=Ad)
pre_save.connect(pre_save_ad_id, sender=Ad)