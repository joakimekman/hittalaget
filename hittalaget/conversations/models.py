from django.db import models
from django.db.models.signals import pre_save 
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from hittalaget.ads.models import Ad


# ---------------------------------- #
# --------- ABSTRACT MODELS -------- #
# ---------------------------------- #


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True


class Conversation(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    users_arr = ArrayField(models.CharField(max_length=255))

    class Meta:
        abstract = True


class Message(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        abstract = True


# ---------------------------------- #
# ---------- CONVERSATIONS --------- #
# ---------------------------------- #


class PmConversation(Conversation):
    tag = models.CharField(max_length=255, default="pm")


class AdConversation(Conversation):
    tag = models.CharField(max_length=255, default="ad")
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    conversation_id = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['conversation_id',]),
        ]

    def get_absolute_url(self):
        return reverse("conversation:detail_ad", kwargs={"conversation_id": self.conversation_id})


# ---------------------------------- #
# ------------- MESSAGES ----------- #
# ---------------------------------- #


class PmMessage(Message):
    ''' Messages added to a PmConversation. '''
    conversation = models.ForeignKey(PmConversation, on_delete=models.CASCADE, related_name="messages")


class AdMessage(Message):
    ''' Messages added to an AdConversation. '''
    conversation = models.ForeignKey(AdConversation, on_delete=models.CASCADE, related_name="messages")


# ---------------------------------- #
# ------------- SIGNALS ------------ #
# ---------------------------------- #


def pre_save_conversation_id(sender, instance, **kwargs):
    ''' Generate conversation_id used with the AdConversation model. '''
    from random import randint
    rand_id = randint(100000, 999999)
    
    if not instance.conversation_id: 
        while AdConversation.objects.filter(conversation_id=rand_id).exists():
            rand_id = randint(100000, 999999)
        else:
            instance.conversation_id = rand_id
    
pre_save.connect(pre_save_conversation_id, sender=AdConversation)