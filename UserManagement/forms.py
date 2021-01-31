from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# Sign Up Form
class SignUpForm(forms.Form):
    username = forms.CharField(max_length=50,required=True, label=False,widget= forms.TextInput(attrs={'class':'form-control','placeholder':'User Name', 'style': 'text-align: center; border-radius: 10px;font-style: italic;'}))#,label="User Name")
    email = forms.EmailField(required=True, label=False,widget= forms.TextInput(attrs={'class':'form-control','placeholder':'E-mail', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}))#,label="")
    password = forms.CharField(max_length=32,required=True,widget= forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}), label=False) #,label="Password"
    password_confirmed = forms.CharField(max_length=32,required=True,widget= forms.PasswordInput(attrs={'class':'form-control','placeholder':'Re-enter Password', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}), label=False) #,label="Password"
    first_name = forms.CharField(max_length=75,required=True, label=False,widget= forms.TextInput(attrs={'class':'form-control','placeholder':'First Name', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}))#,label="")
    last_name = forms.CharField(max_length=75,required=True, label=False,widget= forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}))#,label="Last Name")
    #birth_date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))

# Login Form
class LoginForm(forms.Form):
    username = forms.CharField(max_length=50,required=True, label=False,widget= forms.TextInput(attrs={'class':'form-control','placeholder':'User Name', 'style': 'text-align: center; border-radius: 10px;font-style: italic;'}))#,label="User Name")
    password = forms.CharField(max_length=32,required=True,widget= forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}), label=False) #,label="Password"

