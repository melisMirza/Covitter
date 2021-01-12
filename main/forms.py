from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class WordSearchForm(forms.Form):
    search_words = forms.CharField(max_length=50, label=False,widget= forms.TextInput(attrs={'placeholder':'Search'}))#,label="User Name")
    