from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
import datetime

class City(models.Model):
  name = models.CharField(max_length=255, unique=True)

  def __str__(self):
    return self.name


class User(AbstractUser):
  username = models.CharField(max_length=30, unique=True, verbose_name="användarnamn")
  first_name = models.CharField(max_length=30, verbose_name='förnamn')
  last_name = models.CharField(max_length=150, verbose_name='efternamn')
  email = models.EmailField(unique=True, verbose_name='emailaddress')
  birthday = models.DateTimeField(verbose_name="födelsedag")
  height = models.PositiveIntegerField(blank=True, null=True, verbose_name="längd", help_text="Längden kommer att synas i dina spelarprofiler. Ange längden i cm.")
  city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="users", verbose_name="stad")

  def __str__(self):
    return self.username

  def get_absolute_url(self):
    return reverse("user:detail", kwargs={ "username": self.username })
  
  def get_age(self):
    current_year = datetime.datetime.now().year
    birth_year = self.birthday.year
    age = current_year - birth_year
    return age



