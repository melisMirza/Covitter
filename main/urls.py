from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.weekly, name="weekly"),
    path('datesearch/', views.dateSearch, name="datesearch"),
    path('datesearch/results/', views.dateSearchResults, name="datesearchresults"),
    path('wordsearch/results/', views.wordSearchResults, name="wordsearchresults"),
    path('wordsearch/', views.wordSearch, name="wordsearch"),
    path('account/', views.userAccount, name="account"),
]
