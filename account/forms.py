from django import forms
from django.forms.fields import CharField
from django.contrib.auth.models import User
from .models import Profile

class LoginForm(forms.Form):
    username = CharField()
    # Note that you use the PasswordInput widget to render the password 
    # HTML element. This will include type="password" in the HTML so 
    # that the browser treats it as a password input.
    password = forms.CharField(widget=forms.PasswordInput)

# 2
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

# This will allow users to edit
#  their first name, last name, and email,
#  which are attributes of the built-in Django user model.
class UserEditForm(forms.ModelForm):
       class Meta:
           model = User
           fields = ('first_name', 'last_name', 'email')

# This will allow users to edit the profile data that you save in the custom 
# Profile model. Users will be able to edit their date of birth and upload a picture for their profile.
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')