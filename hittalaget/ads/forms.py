from django import forms
from django.core.exceptions import ValidationError
from django.http import Http404
from .models import Ad
from .form_choices import (
    football_min_experience,
    football_special_ability,
)
from hittalaget.players.models import Position
import datetime


class SportForm(forms.Form):

    SPORTS = [
        ("fotboll", "Fotboll"),
    ]

    sport = forms.CharField(
        max_length=255,
        label="Välj en sport",
        widget=forms.Select(choices=SPORTS)
    )


class AdForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.sport = kwargs.pop('sport')
        super().__init__(*args, **kwargs)

        self.fields['position'].queryset = Position.objects.filter(sport=self.sport)

        min_experience = {
            "fotboll": football_min_experience,
        }
        special_ability = {
            "fotboll": football_special_ability,
        }

        ''' Potential KeyError caused by an invalid sport should be caught
        by the view before even reaching the form. '''
        self.fields['min_experience'].widget = forms.Select(choices=min_experience[self.sport])
        self.fields['special_ability'].widget = forms.Select(choices=special_ability[self.sport])
        
        
    class Meta:
        model = Ad
        fields = [
            'description',
            'position',
            'min_experience',
            'special_ability',
            'max_age',
            'min_height',
        ]

        AGES = ([(y, y) for y in range(100, 7, -1)])
        HEIGHTS = ([(x, "{} cm".format(x)) for x in range(220, 99, -1)])

        widgets = {
            "max_age": forms.Select(choices=AGES),
            "min_height": forms.Select(choices=HEIGHTS),
        }

        help_texts = {
            "description": "Kort beskrivning av vad du söker.",
            "position": "Vilken position ska spelaren du söker spela på?",
            "min_experience": "Minst vad är den erfarenhet spelaren ska ha?",
            "special_ability": "Vilken spetsegenskap ska spelaren ha?",
            "max_age": "Max hur gammal får spelaren vara?",
            "min_height": "Minst hur lång ska spelaren vara?",
        }

        required_msg = "Du måste fylla i detta fält."
        
        error_messages = {
            "description": {
                "required": required_msg,
            },
            "position": {
                "required": required_msg,
            },
            "min_experience": {
                "required": required_msg,
            },
            "special_ability": {
                "required": required_msg,
            },
            "max_age": {
                "required": required_msg,
            },
            "min_height": {
                "required": required_msg,
            },
        }
