from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=50,required=True, label=False,widget= forms.TextInput(attrs={'class':'form-control','placeholder':'User Name', 'style': 'text-align: center; border-radius: 10px;font-style: italic;'}))#,label="User Name")
    email = forms.EmailField(required=True, label=False,widget= forms.TextInput(attrs={'class':'form-control','placeholder':'E-mail', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}))#,label="")
    password = forms.CharField(max_length=32,required=True,widget= forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}), label=False) #,label="Password"
    password_confirmed = forms.CharField(max_length=32,required=True,widget= forms.PasswordInput(attrs={'class':'form-control','placeholder':'Re-enter Password', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}), label=False) #,label="Password"
    first_name = forms.CharField(max_length=75,required=True, label=False,widget= forms.TextInput(attrs={'class':'form-control','placeholder':'First Name', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}))#,label="")
    last_name = forms.CharField(max_length=75,required=True, label=False,widget= forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}))#,label="Last Name")
    #birth_date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    '''
    def clean(self):
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        password_confirmed = self.cleaned_data.get("password_confirmed")
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        print("validation: ", email, " ",validate_email(email))
        
        #Check if email is valid
        try:
            validate_email(email)
            print("email validated")
        except ValidationError:
            raise forms.ValidationError("This e-mail is not valid! Please enter a new e-mail address.")
        
        #Check if password is valid
        if 8 <= len(password):
            print("pass ok")
        else:
            raise forms.ValidationError("Password should be between 2-6 characters.")

        if password != password_confirmed:
            raise forms.ValidationError("Passwords does not match!")
        else:
            print("pass2 ok")
        try:
            user = User.objects.get(username=username)
            print("user:",user)
            raise forms.ValidationError("User already exists! Please pick another user name.")
        except:
            user_form = {
                "username" : username,
                "email" : email,
                "password" : password,
                "first_name" : first_name,
                "last_name": last_name
            }
        
        user_form = {
                "username" : username,
                "email" : email,
                "password" : password,
                "password_confirmed": password_confirmed,
                "first_name" : first_name,
                "last_name": last_name
            }
        return user_form
    '''



'''
class SignUpForm(forms.Form):
    username = forms.CharField(max_length=50,required=True, label=False,widget= forms.TextInput(attrs={'placeholder':'User Name', 'style': 'text-align: center; border-radius: 10px;font-style: italic;'}))#,label="User Name")
    email = forms.EmailField(max_length=75,required=True, label=False,widget= forms.TextInput(attrs={'placeholder':'E-mail', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}))#,label="")
    password = forms.CharField(max_length=32,required=True,widget= forms.PasswordInput(attrs={'placeholder':'Password', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}), label=False) #,label="Password"
    password_confirmed = forms.CharField(max_length=32,required=True,widget= forms.PasswordInput(attrs={'placeholder':'Re-enter Password', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}), label=False) #,label="Password"
    first_name = forms.CharField(max_length=75,required=True, label=False,widget= forms.TextInput(attrs={'placeholder':'First Name', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}))#,label="")
    last_name = forms.CharField(max_length=75,required=True, label=False,widget= forms.TextInput(attrs={'placeholder':'Last Name', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}))#,label="Last Name")
    #birth_date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))

    

    def clean(self):
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        password_confirmed = self.cleaned_data.get("password_confirmed")
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        
        #Check if email is valid
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("This e-mail is not valid! Please enter a new e-mail address.")
        
        #Check if password is valid
        if not (2 <= len(password) and 6>=len(password)):
            raise forms.ValidationError("Password should be between 2-6 characters.")

        if password != password_confirmed:
            raise forms.ValidationError("Passwords does not match!")

        try:
            user = User.objects.get(username=username)
            raise forms.ValidationError("User already exists! Please pick another user name.")
        except:
            user_form = {
                "username" : username,
                "email" : email,
                "password" : password,
                "first_name" : first_name,
                "last_name": last_name
            }

            return user_form
'''
class LoginForm(forms.Form):
    userInfo = forms.CharField(max_length=50,required=True, label=False,widget= forms.TextInput(attrs={'class':'form-control','placeholder':'User Name', 'style': 'text-align: center; border-radius: 10px;font-style: italic;'}))#,label="User Name")
    password = forms.CharField(max_length=32,required=True,widget= forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password', 'style': 'text-align: center; border-radius: 10px; font-style: italic;'}), label=False) #,label="Password"

