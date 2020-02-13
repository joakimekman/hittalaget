from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save 
from django.urls import reverse
from django.utils.text import slugify
from hittalaget.users.models import City


def get_upload_path(instance, filename):
    return "images/teams/{}/{}".format(instance.sport, filename)


class Team(models.Model):
    
    class Sport(models.TextChoices):
        FOTBOLL = "fotboll"
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teams"
    )
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    team_id = models.IntegerField(unique=True)
    slug = models.SlugField()
    founded = models.PositiveIntegerField() 
    home = models.CharField(max_length=255)
    is_looking = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    website = models.URLField(max_length=255, blank=True)
    sport = models.CharField(max_length=255, choices=Sport.choices)
    level = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to=get_upload_path,
        blank=True,
        null=True,
        default="images/teams/default.png"
    )

    class Meta:
        ''' A user can only have one team for each sport. '''
        constraints = [
            models.UniqueConstraint(fields=['user', 'sport'], name="unique_team"),
        ]
        indexes = [
            models.Index(fields=['team_id',]),
        ]
    
    
    def get_absolute_url(self):
        return reverse("team:detail", kwargs={
            "sport": self.sport,
            "team_id": self.team_id,
            "slug": self.slug,
        })
    
    def __str__(self):
        return self.name


def pre_save_six_digit_team_id(sender, instance, **kwargs):
    ''' Each Football team will have a 6 digit team_id that will be
    used in the URL to identify the team. '''
    from random import randint
    rand_id = randint(100000, 999999)

    if not instance.team_id:
        while Team.objects.filter(team_id=rand_id).exists():
            rand_id = randint(100000, 999999)
        else:
            instance.team_id = rand_id

def pre_save_slugify_name(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)


pre_save.connect(pre_save_six_digit_team_id, sender=Team)
pre_save.connect(pre_save_slugify_name, sender=Team)


