from django.urls import path
from .views import *

urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('logout', Logout.as_view(), name='logout'),
    path('home', Home.as_view(), name='home'),
    path('newquestion', NewQuestion.as_view(), name='new_question'),
    path('quiz', Quiz.as_view(), name='quiz'),
    path('questionlist', QuestionList.as_view(), name='question_list'),
    path('questionedit/<int:question_id>', EditQuestion.as_view(), name='edit_question'),
]