from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
    SetPasswordForm,
)  
from django.core.exceptions import ValidationError
import datetime


User = get_user_model()


class MetaMixin:
    fields = ["first_name", "last_name", "birthday", "city", "email", "height"]

    current_year = datetime.datetime.now().year

    MONTHS = {
        1: "januari",
        2: "februari",
        3: "mars",
        4: "april",
        5: "maj",
        6: "juni",
        7: "juli",
        8: "augusti",
        9: "september",
        10: "oktober",
        11: "november",
        12: "december",
    }

    HEIGHTS = ([(x, "{} cm".format(x)) for x in range(220, 99, -1)])

    widgets = {
        "birthday": forms.SelectDateWidget(
            years=range(current_year, current_year - 80, -1), months=MONTHS
        ),
        "height": forms.Select(choices=[("", "-")] + HEIGHTS),
    }

    error_messages = {
        "email": {
            "unique": "Emailadressen existerar redan! Prova en annan och försök igen.",
            "invalid": "Ange en riktig email.",
        },
    }


class UserCreateForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = "Lösenord"
        self.fields['password2'].label = "Bekräfta lösenord"
        self.fields['password2'].help_text = ""

    class Meta(MetaMixin):
        model = User
        fields = ['username'] + MetaMixin.fields

        MetaMixin.error_messages.update({
            "username": {
                "unique": "Användarnamnet existerar redan! Prova ett annat och försök igen.",
            }
        })

    def clean_username(self):
        ''' Converting username to lowercase to make the unique check
        case insensitive. '''
        username = self.cleaned_data['username']
        return username.lower()
    
    def clean_email(self):
        ''' Converting email to lowercase to make the unique check
        case insensitive. '''
        email = self.cleaned_data['email']
        return email.lower()
    

class UserUpdateForm(forms.ModelForm):
    class Meta(MetaMixin):
        model = User


class AuthenticationForm2(AuthenticationForm):
    '''
    Override AuthenticationForm to provide custom labels, and
    error messages.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # username label is pulled from verbose_name
        self.fields['password'].label = "Lösenord"
    
    error_messages = {
        'invalid_login': ("Fel användarnamn eller lösenord."),
        'inactive': ("Kontot du försöker att logga in med är inaktivt."),
    }


class PasswordChangeForm2(PasswordChangeForm):
    '''
    Override PasswordChangeForm to provide custom labels, and
    error messages.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = "Gammalt lösenord"
        self.fields['new_password1'].label = "Nytt lösenord"
        self.fields['new_password2'].label = "Bekräfta nytt lösenord"
    
    error_messages = {
        'password_mismatch': ('Lösenorden stämmer inte överens med varandra.'),
        'password_incorrect': ('Ditt gamla lösenord är fel. Prova igen.'), 
    }


class SetPasswordForm2(SetPasswordForm):
    ''' Override SetPasswordForm to provide custom labels, and error
    messages. '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = "Nytt lösenord"
        self.fields['new_password2'].label = "Bekräfta nytt lösenord"

    error_messages = {
        'password_mismatch': ('Lösenorden stämmer inte överens med varandra.'),
    }