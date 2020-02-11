from django.conf import settings
from django.db.models.signals import pre_save 
from django.db import models
from django.urls import reverse


def get_upload_path(instance, filename):
    return "images/players/{}/{}".format(instance.sport, filename)


class Position(models.Model):
    sport = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Player(models.Model):
    
    class Sport(models.TextChoices):
        FOTBOLL = "fotboll"
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="player_profiles"
    )
    username = models.CharField(max_length=255)
    sport = models.CharField(max_length=255, choices=Sport.choices)
    positions = models.ManyToManyField(Position, related_name="players")
    side = models.CharField(max_length=255)
    experience = models.CharField(max_length=255)
    special_ability = models.CharField(max_length=255)
    is_available = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to=get_upload_path,
        blank=True,
        null=True,
        default='images/players/default.png'
    )
    

    class Meta:
        ''' Each user can have ONE player profile for each sport. '''
        constraints = [
            models.UniqueConstraint(fields=['user', 'sport'], name="unique player")
        ]


    def __str__(self):
        return self.sport

    def get_absolute_url(self):
        return reverse('player:detail', kwargs={"sport": self.sport, "username": self.username})


class History(models.Model):
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField()
    team_name = models.CharField(max_length=255)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="history_entries")


def pre_save_username(sender, instance, **kwargs):
    user = instance.user
    instance.username = user.username

pre_save.connect(pre_save_username, sender=Player)

    


