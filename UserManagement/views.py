from django.shortcuts import render, redirect
from django.template import loader
from .forms import SignUpForm, LoginForm
from django.contrib.auth import login, authenticate, logout 
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect("/analytics") 
    return render(request, "UserManagement/Welcome.html",{})


def loginUser(request):
    try:
        form = LoginForm(request.POST)

        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect("/analytics")
            else:
                messages.info(request, "Username or password is incorrect!")
                return render(request, "UserManagement/Login.html" ,{"form":form})

        return render(request, "UserManagement/Login.html" ,{"form":form})
    except:
        return redirect("/error")


def signup(request):
    try:
        form = SignUpForm(request.POST or None, request.FILES or None)
        
        if request.method == "POST":
            
            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                password_confirmed = form.cleaned_data.get("password_confirmed")
                email = form.cleaned_data.get("email")
                firstname = form.cleaned_data.get("first_name")
                lastname = form.cleaned_data.get("last_name")
                print(username,password,password_confirmed,email,firstname,lastname)
                if len(password) < 8 :
                    error_message = "Password should be at least 8 characters!"
                    return render(request, "UserManagement/SignUp.html" ,{"form":form,"error_message":error_message})
                
                if password != password_confirmed:
                    error_message = "Password confirmation does not match!"
                    return render(request, "UserManagement/SignUp.html" ,{"form":form,"error_message":error_message})

                try:
                    validate_email(email)
                except ValidationError:
                    error_message = "Invalid email!"
                    return render(request, "UserManagement/SignUp.html" ,{"form":form,"error_message":error_message})

                try:
                    user = User.objects.get(username=username)
                    error_message = "User already exists!"
                    return render(request, "UserManagement/SignUp.html" ,{"form":form,"error_message":error_message})
                except:
                    
                    new_user = User(username=username,password=password,email=email,first_name=firstname,last_name=lastname)
                    new_user.set_password(password)
                    new_user.save()
                    return redirect('/user/login')

        return render(request, "UserManagement/SignUp.html" ,{"form":form})
    except:
        return redirect("/error")

def logoutUser(request):
    try:
        logout(request)
        return redirect("/")
    except:
        return redirect("/error")

'''
def loginUser(request):
    form = LoginForm(request.POST)

    if request.method == "POST":
       return redirect("/analytics")

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
            return redirect("/analytics")

    return render(request, "UserManagement/SignUp.html" ,{"form":form})



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