from django.shortcuts import render, redirect
from django.template import loader
from .forms import SignUpForm, LoginForm
from django.contrib.auth import login, authenticate, logout 
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

# Create your views here.
def home(request):
    return render(request, "UserManagement/Welcome.html",{})

def loginUser(request):
    form = LoginForm(request.POST)

    if request.method == "POST":
       return render(request, "UserManagement/Welcome.html",{})

    return render(request, "UserManagement/Login.html" ,{"form":form})

def signup(request):
    form = SignUpForm(request.POST or None, request.FILES or None)
    
    if request.method == "POST":
        
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            email = form.cleaned_data.get("email")
            firstname = form.cleaned_data.get("first_name")
            lastname = form.cleaned_data.get("last_name")

            new_user = User(username=username,password=password,email=email,first_name=firstname,last_name=lastname)
            new_user.save()
            return render(request, "UserManagement/Welcome.html",{})

    return render(request, "UserManagement/SignUp.html" ,{"form":form})


'''
from django.core.mail import send_mail

if form.is_valid():
    subject = form.cleaned_data['subject']
    message = form.cleaned_data['message']
    sender = form.cleaned_data['sender']
    cc_myself = form.cleaned_data['cc_myself']

    recipients = ['info@example.com']
    if cc_myself:
        recipients.append(sender)

    send_mail(subject, message, sender, recipients)
    return HttpResponseRedirect('/thanks/')
'''