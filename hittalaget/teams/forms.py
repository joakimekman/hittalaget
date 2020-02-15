from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, Http404, HttpResponse
from .models import Team
from .form_choices import football_levels
import datetime
import re


def alphanumeric_validator(str):
    if not re.match(r'[a-zåäöA-ZÅÄÖ0-9 ]*$', str):
        raise ValidationError("Du kan bara använda alfanumeriska tecken.")


class SportForm(forms.Form):

    SPORTS = [
        ("fotboll", "Fotboll"),
    ]

    sport = forms.CharField(
        max_length=255,
        label="Välj en sport",
        widget=forms.Select(choices=SPORTS)
    )
    

class TeamForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.sport = kwargs.pop("sport")
        super().__init__(*args, **kwargs)

        level = {
            "fotboll": football_levels,
        }        
        
        ''' Potential KeyError caused by an invalid sport should be caught
        by the view before even reaching the form. '''
        self.fields['level'].widget = forms.Select(choices=level[self.sport])
    

    class Meta:
        model = Team
        fields = ['founded', 'home', 'city', 'website', 'level']

        current_year = datetime.datetime.now().year + 1
        year_range = [(str(year), year) for year in range(1880, current_year)[::-1]]

        widgets = {
            "founded": forms.Select(choices=year_range),
        }

        labels = {
            'founded': 'Grundades:',
            'home': 'Hemmaplan:',
            'city': 'Stad:',
            'website': 'Hemsida:',
            'level': 'Liga:',
        }

        help_texts = {
            'website': "http://example.com"
        }

        required_msg = "Du måste fylla i detta fält."

        error_messages = {
            'founded': {
                'required': required_msg,
            },
            'home': {
                'required': required_msg,
            },
            'city': {
                'required': required_msg,
            },
            'level': {
                'required': required_msg,
            },
            'website': {
                'required': required_msg,
                'invalid': 'Ange en korrekt email.'
            },
        }

    def clean_home(self):
        ''' Home must only have alphanumeric characters. '''
        home = self.cleaned_data['home']
        alphanumeric_validator(home)
        return home


class TeamCreateForm(TeamForm):
    
    ''' Adds support for the name field. '''

    class Meta(TeamForm.Meta):
        fields = ['name'] + TeamForm.Meta.fields

        TeamForm.Meta.labels.update({
            'name': 'Namn:',
        })
        
        TeamForm.Meta.error_messages.update({
            'name': {
                'required': TeamForm.Meta.required_msg,
            },
        })
    
    
    def clean_name(self):
        ''' Name must only have alphanumeric characters. '''
        name = self.cleaned_data['name']
        alphanumeric_validator(name)
        return name


