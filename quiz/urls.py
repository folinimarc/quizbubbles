from django.urls import path
from .views import *

urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('home', Home.as_view(), name='home'),
    path('newquestion', NewQuestion.as_view(), name='new_question'),
    path('sprint', Sprint.as_view(), name='sprint')
]