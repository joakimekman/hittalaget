from django import forms
from django.core.exceptions import ValidationError
from django.http import Http404
from .models import Player, Position, History
from .form_choices import (
    football_experiences,
    football_sides,
    football_special_abilities,
)
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


class PlayerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.sport = kwargs.pop('sport')
        super().__init__(*args, **kwargs)

        self.fields['positions'].widget = forms.CheckboxSelectMultiple()
        self.fields['positions'].queryset = Position.objects.filter(sport=self.sport)
        
        sides = {
            "fotboll": [football_sides, "Bästa fot"],
        }
        experiences = {
            "fotboll": football_experiences,
        }
        special_abilities = {
            "fotboll": football_special_abilities,
        }
        
        ''' Potential KeyError from invalid sports should be caught
        by the view before even reaching the forms. '''
        self.fields['side'].widget = forms.Select(choices=sides[self.sport][0])
        self.fields['side'].label = sides[self.sport][1]
        self.fields['experience'].widget = forms.Select(choices=experiences[self.sport])
        self.fields['special_ability'].widget = forms.Select(choices=special_abilities[self.sport])


    class Meta:
        model = Player
        fields = ['positions', 'side', 'experience', 'special_ability']

        labels = {
            "positions": "Positioner",
            "experience": "Erfarenhet",
            "special_ability": "Spetsegenskap", 
        }

        required_msg = "Du måste fylla i det här fältet."

        error_messages = {
            "positions": {
                "required": required_msg,
                "invalid_choice": "Välj ett giltigt alternativ",
            },
            "side": {
                "required": required_msg,
            },
            "experience": {
                "required": required_msg,
            },
            "special_ability": {
                "required": required_msg,
            },
        }

    def invalid_choice(self, field_name, field_data):    
        ''' Since choices for side, experience, and special_ability is set
        at the form level, we must provide a custom invalid_choice check. 

        The invalid_choice check should prevent people from changing a form
        choice to an invalid value by tampering with inspect. ''' 
        tup = (field_data, field_data.capitalize())

        if not tup in self.fields[field_name].widget.choices:
            raise ValidationError("Välj ett giltigt alternativ.")

    def clean_side(self):
        data = self.cleaned_data['side'].lower()
        self.invalid_choice('side', data)
        return data

    def clean_experience(self):
        data = self.cleaned_data['experience'].lower()
        self.invalid_choice('experience', data)
        return data

    def clean_special_ability(self):
        data = self.cleaned_data['special_ability'].lower()
        self.invalid_choice('special_ability', data)
        return data


class HistoryForm(forms.ModelForm):

    class Meta:
        model = History
        fields = ["start_year", "end_year", "team_name"]

        labels = {
            "start_year": "Året du började",
            "end_year": "Året du slutade",
            "team_name": "Lagnamn",
        }

        current_year = datetime.datetime.now().year

        year_range = [(y, y) for y in range(current_year, 1980, -1)]

        widgets = {
            "start_year": forms.Select(choices=year_range),
            "end_year": forms.Select(choices=year_range),
        }


    def invalid_year(self, year):
        ''' Raise ValidationError if year has the wrong format or is in
        the future. '''
        current_year = datetime.datetime.now().year
        if not len(str(year)) == 4:
            raise ValidationError("Du måste ha det följande formatet: YYYY")
        if year > current_year:
            raise ValidationError("Året kan inte ligga i framtiden.")

    def clean_start_year(self):
        start_year = self.cleaned_data['start_year']
        self.invalid_year(start_year)
        return start_year
    
    def clean_end_year(self):
        end_year = self.cleaned_data['end_year']
        self.invalid_year(end_year)
        return end_year

    def clean(self):
        ''' Raise ValidationError if start_year is greater than the
        end_year. '''
        cleaned_data = super().clean()
        start_year = cleaned_data.get("start_year")
        end_year = cleaned_data.get("end_year")

        if start_year and end_year:
            if start_year > end_year:
                self.add_error(
                    'start_year',
                    ValidationError("Startåret kan inte vara senare än slutåret.")
                )
        return cleaned_data

