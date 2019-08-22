from django.urls import path
from .views import *

urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('<slug:space_name>/logout', Logout.as_view(), name='logout'),
    path('<slug:space_name>', Home.as_view(), name='home'),
    path('<slug:space_name>/sendmail', SendMail.as_view(), name='send_mail'),
    path('<slug:space_name>/settings', Settings.as_view(), name='settings'),
    path('<slug:space_name>/newquestion', NewQuestion.as_view(), name='new_question'),
    path('<slug:space_name>/quiz/<int:quiz_id>', QuizView.as_view(), name='quiz'),
    path('<slug:space_name>/questionlist', QuestionList.as_view(), name='question_list'),
    path('<slug:space_name>/questionedit/<int:question_id>', EditQuestion.as_view(), name='edit_question'),
]