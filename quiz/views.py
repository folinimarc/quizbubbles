from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.db import transaction
from django.db.models import F, Count
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.core.signing import Signer, BadSignature
import time
import json
import random
from datetime import timedelta
from .decorators import *
from .models import *
from .forms import *
from collections import OrderedDict


class About(View):
    def get(self, request):
        ctx = {}
        ctx['captcha_form'] = CaptchaForm()
        return render(request, 'quiz/about.html', ctx)

    def post(self, request):
        ctx = {}
        captcha_form = CaptchaForm(request.POST)
        if not captcha_form.is_valid():
            ctx['captcha_form'] = captcha_form
        return render(request, 'quiz/about.html', ctx)
        

class Login(View):

    def get_public_bubbles(self):
        return Bubble.objects\
            .filter(public=True)\
            .annotate(questions_total=Count('questions', distinct=True))\
            .annotate(quizes_total=Count('quizes', distinct=True))\
            .order_by('last_access', 'questions_total')

    def get(self, request):
        ctx = {}
        ctx['join_form'] = BubbleJoinForm()
        ctx['create_form'] = BubbleCreateForm()
        ctx['flipShowJoin'] = True
        ctx['bubbles'] = self.get_public_bubbles()
        return render(request, 'quiz/login.html', ctx)

    @transaction.atomic
    def post(self, request):
        ctx = {}
        ctx['wrong_password'] = False
        # handle join request
        if 'join' in request.POST:
            join_form = BubbleJoinForm(request.POST)
            if join_form.is_valid():
                bubble = Bubble.objects.filter(name=join_form.cleaned_data['name']).first()
                password = join_form.cleaned_data.get('password', None)
                if not bubble:
                    join_form.add_error('name', 'Bubblename does not exist')
                elif not password:
                    if bubble.public:
                        return redirect('home', bubble_name=bubble.name)
                    else:
                        join_form.add_error('password', 'This bubble requires a password')
                else:
                    if check_password(password, bubble.password):
                        request.session[bubble.name] = str(bubble.id)
                        request.session.set_expiry(0)
                        return redirect('home', bubble_name=bubble.name)
                    else:
                        join_form.add_error('password', 'Invalid password.')
                        ctx['wrong_password'] = True
                        ctx['bubble_name'] = bubble.name
            ctx['flipShowJoin'] = True
            ctx['join_form'] = join_form
            ctx['create_form'] = BubbleCreateForm()
            ctx['bubbles'] = self.get_public_bubbles()
            return render(request, 'quiz/login.html', ctx)

        # handle create request
        if 'create' in request.POST:
            create_form = BubbleCreateForm(request.POST)
            if create_form.is_valid():
                # create quizebubble
                bubble = Bubble.objects.create(
                    name = create_form.cleaned_data['name'],
                    email = create_form.cleaned_data['email'],
                    password = make_password(create_form.cleaned_data['password1']),
                    public = create_form.cleaned_data['public']
                )
                messages.info(request, f'New quizebubble \"{create_form.cleaned_data["name"]}\" successfully created. Have fun!')
                request.session[bubble.name] = str(bubble.id)
                request.session.set_expiry(0)
                return redirect('home', bubble_name=bubble.name)
            ctx['flipShowJoin'] = False
            ctx['join_form'] = BubbleJoinForm()
            ctx['create_form'] = create_form
            ctx['bubbles'] = self.get_public_bubbles()
            return render(request, 'quiz/login.html', ctx)
        return redirect('login')


@method_decorator([close_quiz(methods=['GET'])], name='dispatch')
class Logout(View):
    def get(self, request, bubble_name):
        request.session.pop(bubble_name, None)
        request.session.pop('username', None)
        return redirect('login')


class ForgotPassword(View):
    def get(self, request, bubble_name):
        ctx = {}
        ctx['bubble'] = get_object_or_404(Bubble, name=bubble_name)
        ctx['captcha_form'] = CaptchaForm()
        return render(request, 'quiz/forgot_password.html', ctx)

    def post(self, request, bubble_name):
        ctx = {}
        captcha_form = CaptchaForm(request.POST)
        if not captcha_form.is_valid():
            ctx['bubble'] = get_object_or_404(Bubble, name=bubble_name)
            ctx['captcha_form'] = captcha_form
            return render(request, 'quiz/forgot_password.html', ctx)
        request.session['human_confirmed'] = True
        return redirect('request_password', bubble_name=bubble_name)


@method_decorator([human_confirmed], name='dispatch')
class RequestPassword(View):
    def get(self, request, bubble_name):
        ctx = {}
        ctx['bubble'] = get_object_or_404(Bubble, name=bubble_name)
        return render(request, 'quiz/request_password.html', ctx)

    @transaction.atomic
    def post(self, request, bubble_name):
        ctx = {}
        bubble = get_object_or_404(Bubble, name=bubble_name)
        timestamp = str(int(time.time()))
        token = Signer().sign('-'.join([timestamp, bubble.name]))
        bubble.reset_token = token
        bubble.save()
        formatted_time_now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        subject = f'Password reset request of quizbubble {bubble.name} on {formatted_time_now} UTC'
        reset_link = request.build_absolute_uri(reverse('reset_password', kwargs={'token': token}))
        body = f'The following link will be valid for one hour to reset your password of bubble {bubble.name}:\n\n{reset_link}\n\nKind regards from the quizbubbles team'
        send_mail(
            subject,
            body,
            'team@quizbubbles.com',
            [bubble.email],
            fail_silently=False,
        )
        messages.info(request, f'A password reset link was sent to {bubble.email}. Be sure to also check the spam folder.')
        return redirect('logout', bubble_name=bubble_name)


class PasswordReset(View):
    def get(self, request, token):
        ctx = {}
        try:
            timestamp, bubble_name = Signer().unsign(token).split('-')
            bubble = get_object_or_404(Bubble, name=bubble_name)
            if bubble.reset_token != token:
                messages.info(request, f'This password reset link was already used.')
                return redirect('login')
            if int(time.time()) - int(timestamp) > 3600: # 1 hour
                messages.info(request, f'This password reset link is older than 1 hour and has expired.')
                return redirect('login')
        except BadSignature:
            messages.info(request, f'A problem occured while processing this reset link. Please try again or report this.')
            return redirect('login')
        ctx['bubble_name'] = bubble_name
        ctx['reset_form'] = BubblePasswordResetForm()
        return render(request, 'quiz/reset_password.html', ctx)

    @transaction.atomic
    def post(self, request, token):
        ctx = {}
        try:
            timestamp, bubble_name = Signer().unsign(token).split('-')
            bubble = get_object_or_404(Bubble, name=bubble_name)
            if bubble.reset_token != token:
                messages.info(request, f'This password reset link was already used.')
                return redirect('login')
            if int(time.time()) - int(timestamp) > 3600: # 1 hour
                messages.info(request, f'This password reset link is older than 1 hour and has expired.')
                return redirect('login')
        except BadSignature:
            messages.info(request, f'A problem occured while processing your reset link. Please try again or report this.')
            return redirect('login')
        reset_form = BubblePasswordResetForm(request.POST)
        if not reset_form.is_valid():
            ctx['reset_form'] = reset_form
            return render(request, 'quiz/reset_password.html', ctx)
        bubble.password = make_password(reset_form.cleaned_data['password1'])
        bubble.reset_token = None
        bubble.save()
        messages.info(request, f'Your password was reset.')
        return redirect('login')


@method_decorator([check_bubble_permission(authenticated_only=True)], name='dispatch')
class Settings(View):
    def get(self, request, bubble_name):
        ctx = {}
        ctx['bubble_name'] = bubble_name
        bubble = Bubble.objects.get(name=bubble_name)
        ctx['change_form'] = BubbleChangeForm(instance=bubble)
        ctx['delete_form'] = BubbleDeleteForm()
        return render(request, 'quiz/settings.html', ctx)

    @transaction.atomic
    def post(self, request, bubble_name):
        ctx = {}
        ctx['bubble_name'] = bubble_name
        bubble = Bubble.objects.get(name=bubble_name)
        if 'delete' in request.POST:
            delete_form = BubbleDeleteForm(request.POST)
            if delete_form.is_valid():
                bubble.delete()
                messages.info(request, f'Bubble {bubble_name} was successfully deleted!')
                return redirect('logout', bubble_name=bubble_name)
            else:
                ctx['change_form'] = BubbleChangeForm(instance=bubble)
                ctx['delete_form'] = delete_form
                return render(request, 'quiz/settings.html', ctx)
        if 'change' in request.POST:
            change_form = BubbleChangeForm(request.POST, instance=bubble)
            if change_form.is_valid():
                new_bubble_name = change_form.cleaned_data['name']
                if new_bubble_name != bubble_name:
                    request.session[new_bubble_name] = str(bubble.id)
                    request.session.pop(bubble_name, None)
                bubble = change_form.save(commit=False)
                if change_form.cleaned_data.get('password1', False) and change_form.cleaned_data.get('password2', False) and change_form.cleaned_data.get('password1', False) == change_form.cleaned_data.get('password2', False):  
                    bubble.password = make_password(change_form.cleaned_data['password1'])
                bubble.save()
                messages.info(request, f'Edits were successfully applied!')
                return redirect('home', bubble_name=new_bubble_name)
            else: 
                ctx['change_form'] = change_form
                ctx['delete_form'] = BubbleDeleteForm()
                return render(request, 'quiz/settings.html', ctx)
        messages.info(request, f'You reached a deep dark point where you should not be... There are dragons! Please report this.')
        return redirect('home', bubble_name=bubble_name)


@method_decorator([check_bubble_permission(authenticated_only=False), close_quiz(methods=['GET'])], name='dispatch')
class Home(View):

    def get_sprint_question_ids(self, bubble):
        all_questions = list(Question.objects.filter(bubble_id=bubble.id).values_list('id', 'difficulty'))
        random.shuffle(all_questions)
        question_dict = {difficulty: [] for difficulty, _ in Question.DIFFICULTIES}
        [question_dict[difficulty].append(id) for id, difficulty in all_questions]
        question_list = []
        for difficulty, _ in Question.DIFFICULTIES:
            question_list.extend(question_dict[difficulty][:settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY])
        questions_total = len(question_list)
        return questions_total, ','.join(str(id) for id in question_list)

    def get_marathon_question_ids(self, bubble):
        question_list = list(Question.objects.filter(bubble_id=bubble.id).values_list('id', flat=True))
        random.shuffle(question_list)
        questions_total = len(question_list)
        return questions_total, ','.join(str(id) for id in question_list)

    @transaction.atomic
    def get(self, request, bubble_name):
        ctx = {}
        ctx['bubble_name'] = bubble_name
        ctx['username'] = request.session.get('username', '')
        bubble = Bubble.objects.get(name=bubble_name)
        time_since_cleanup = timezone.now() - bubble.last_cleanup
        if time_since_cleanup.seconds > 3600:
            time_treshold = timezone.now() - timedelta(minutes=1)
            a = Quiz.objects.filter(bubble_id=bubble.id, heartbeat_timestamp__lt=time_treshold).update(
                quizstate=Quiz.FINISHED,
                enddatetime=F('heartbeat_timestamp') + timedelta(seconds=10)
                )
            bubble.last_cleanup = timezone.now()
        bubble.save()
        ctx['authenticated'] = request.session.get(bubble_name, None) == str(bubble.id)
        difficulty_counts = Question.objects.filter(bubble_id=bubble.id).values('difficulty').annotate(count=Count('difficulty'))
        difficulty_dict = OrderedDict()
        for db_val, verbose in sorted(Question.DIFFICULTIES, key=lambda x: x[0]):
            difficulty_dict[verbose] = 0
        for obj in difficulty_counts:
            verbose = Question.get_verbose_difficulty_from_dbvalue(obj['difficulty'])
            difficulty_dict[verbose] = obj['count']
        enough_questions = all(v >= settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY for v in difficulty_dict.values())
        ctx['enough_questions'] = enough_questions
        if not enough_questions:
            difficulty_list = [{
                'difficulty': verbose,
                'count': count,
                'max': settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY,
                'missing': count < settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY
                } for verbose, count in difficulty_dict.items()]
            ctx['difficulty_list'] = difficulty_list
        nr_questions = Question.objects.filter(bubble_id=bubble.id).count()
        ctx['nr_sprint_questions'] = len(Question.DIFFICULTIES * settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY)
        ctx['nr_questions'] = nr_questions
        ctx['nr_hearts'] = bubble.hearts
        ctx['sprint_champions'] = Quiz.objects\
            .filter(bubble_id=bubble.id, quizstate=Quiz.FINISHED, quiztype=Quiz.SPRINT)\
            .order_by('-questions_answered', 'duration', '-enddatetime')[:settings.NR_LEADERBOARD_ENTRIES_TO_SHOW]
        ctx['marathon_champions'] = Quiz.objects\
            .filter(bubble_id=bubble.id, quizstate=Quiz.FINISHED, quiztype=Quiz.MARATHON)\
            .order_by('-questions_answered', 'duration', '-enddatetime')[:settings.NR_LEADERBOARD_ENTRIES_TO_SHOW]
        ctx['nr_quizes'] = Quiz.objects.filter(bubble_id=bubble.id).count()
        return render(request, 'quiz/home.html', ctx)

    @transaction.atomic
    def post(self, request, bubble_name):
        payload = json.loads(request.body)
        action = payload.get('action', None)
        if action not in ['startSprint', 'startMarathon']:
            return JsonResponse({
                'status': 'ERROR', 
                'message': 'No valid action was supplied. Please report this.'
                })
        form = QuizUsernamenameQuiztypeForm(payload)
        if not form.is_valid():
            return JsonResponse({
                'status': 'ERROR', 
                'message': form.get_form_errors_as_string()
                })
        # Create new quiz
        bubble = Bubble.objects.get(name=bubble_name)
        if form.cleaned_data['quiztype'] == Quiz.SPRINT:
            questions_total, question_ids = self.get_sprint_question_ids(bubble)
        elif form.cleaned_data['quiztype'] == Quiz.MARATHON:
            questions_total, question_ids = self.get_marathon_question_ids(bubble)
        else:
            return JsonResponse({
                'status': 'ERROR', 
                'message': f'Unknown quiztype {form.cleaned_data["quiztype"]}'
                })
        quiz = Quiz.objects.create(
            **form.cleaned_data, 
            questions_total=questions_total,
            question_ids=question_ids,
            bubble_id=bubble.id
            )
        request.session['session_quiz_id'] = str(quiz.id)
        request.session['username'] = form.cleaned_data['username']
        return JsonResponse({
                'status': 'OK', 
                'message': '',
                'successRedirectUrl': reverse('quiz',  kwargs={'bubble_name':bubble_name, 'quiz_id':quiz.id})
                })


@method_decorator([check_bubble_permission(authenticated_only=True)], name='dispatch')
class NewQuestion(View):
    def get(self, request, bubble_name):
        ctx = {}
        ctx['bubble_name'] = bubble_name
        ctx['form'] = QuestionModelForm(initial={'contributor': request.session.get('username', None)})
        return render(request, 'quiz/new_question.html', ctx)

    @transaction.atomic
    def post(self, request, bubble_name):
        ctx = {}
        ctx['bubble_name'] = bubble_name
        bubble = Bubble.objects.get(name=bubble_name)
        form = QuestionModelForm(request.POST)
        if form.is_valid():
            Question.objects.create(
                **form.cleaned_data,
                bubble_id=bubble.id
            )
            request.session['username'] = form.cleaned_data['contributor']
            messages.info(request, 'Thank you! Your question was added.')
            return redirect('new_question', bubble_name=bubble_name)
        else:
            messages.info(request, 'There were problems with your form. Please check the form field messages and submit again.')
        ctx['form'] = form
        return render(request, 'quiz/new_question.html', ctx)


@method_decorator([check_bubble_permission(authenticated_only=False), check_quiz_permission], name='dispatch')
class QuizView(View):

    def get_quiz(self, quiz_id):
        return get_object_or_404(Quiz, id=quiz_id)

    def get_question(self, quiz):
        question_id = int(quiz.question_ids.split(',')[quiz.questions_index])
        return get_object_or_404(Question, id=question_id)

    def get_ranking(self, quiz):
        outperform_questions = Quiz.objects.filter(bubble_id=quiz.bubble_id, quizstate=Quiz.FINISHED, quiztype=quiz.quiztype, questions_answered__gt=quiz.questions_answered).count()
        outperform_time = Quiz.objects.filter(bubble_id=quiz.bubble_id, quizstate=Quiz.FINISHED, quiztype=quiz.quiztype, questions_answered=quiz.questions_answered, duration__lt=quiz.duration).count()
        rank = outperform_questions + outperform_time + 1
        return rank

    @transaction.atomic
    def get(self, request, bubble_name, quiz_id):
        ctx = {}
        ctx['bubble_name'] = bubble_name
        return render(request, 'quiz/quiz.html', ctx)

    @transaction.atomic
    def post(self, request, bubble_name, quiz_id):
        payload = json.loads(request.body)
        action = payload.get('action', None)
        if action not in ['sendHeartbeat', 'getQuizData', 'checkAnswer', 'nextQuestion', 'jokerFiftyFifty', 'jokerAudience', 'jokerTimestop', 'sendLove']:
            return JsonResponse({
                'status': 'ERROR', 
                'message': 'No valid action was supplied. Please report this.'
                })
        quiz = self.get_quiz(quiz_id)
        if action == 'sendHeartbeat':
            quiz.heartbeat_timestamp = timezone.now()
            return JsonResponse({
                'status': 'OK',
                })
        if action == 'sendLove':
            if quiz.quiztype != Quiz.SPRINT or not quiz.can_send_love or quiz.questions_answered != quiz.questions_total:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'There was a problem with sending love :(',
                    })
            quiz.can_send_love = False
            quiz.save()
            bubble = get_object_or_404(Bubble, name=bubble_name)
            bubble.hearts += 1
            bubble.save()
            return JsonResponse({
                    'status': 'OK',
                    'message': 'You added a heart to the quizbubble.'
            })
        if quiz.quizstate != Quiz.IN_PROGRESS:
            return JsonResponse({
                'status': 'ERROR',
                'message': f'This quiz is not active anymore. Please start a new quiz.'
                })
        if action == 'getQuizData':
            rank = self.get_ranking(quiz)
            quizes_total = Quiz.objects.filter(bubble_id=quiz.bubble_id, quizstate=Quiz.FINISHED, quiztype=quiz.quiztype).count() + 1
            return JsonResponse({
                'status': 'OK',
                'quiztype': quiz.get_quiztype_display(),
                'timePassed': quiz.duration,
                'rank': rank,
                'quizesTotal': quizes_total,
                'questionsIndex': quiz.questions_index,
                'questionsAnswered': quiz.questions_answered,
                'questionsTotal': quiz.questions_total,
                })
        if action == 'jokerAudience':
            if not quiz.joker_audience_available:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'Audience joker is not available anymore.',
                    })
            quiz.joker_audience_available = False
            quiz.save()
            question = self.get_question(quiz)
            chosen_answers_count = json.loads(question.chosen_answers_count)
            return JsonResponse({
                    'status': 'OK', 
                    'message': 'Audience joker: See what others have chosen.',
                    'chosen_answers_count': chosen_answers_count
                    })
        if action == 'jokerFiftyFifty':
            if not quiz.joker_fiftyfifty_available:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'Fifty-fifty joker is not available anymore.',
                    })
            quiz.joker_fiftyfifty_available = False
            quiz.save()
            question = self.get_question(quiz)
            kill = random.sample({'a','b','c','d'}.difference({question.correct_answer}), 2)
            return JsonResponse({
                    'status': 'OK',
                    'message': 'Fifty-fifty joker: Removed two wrong answers.',
                    'kill': kill
                    })
        if action == 'jokerTimestop':
            if not quiz.joker_timestop_available:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'Timestop joker is not available anymore.',
                    })
            quiz.joker_timestop_available = False
            quiz.timestop_active = True
            quiz.save()
            return JsonResponse({
                    'status': 'OK',
                    'message': 'Timestop joker: Timer reset and stopped.',
                    'timePassed': quiz.duration
                    })

        if action == 'nextQuestion':
            quiz.helperdatetime = timezone.now()
            quiz.save()
            question = self.get_question(quiz)
            return JsonResponse({
                'status': 'OK',
                'question': {
                    'header': f'Question {quiz.questions_index + 1} ({question.get_difficulty_display()})',
                    'body': question.question,
                },
                'answers': {
                    'a': question.answer_a,
                    'b': question.answer_b,
                    'c': question.answer_c,
                    'd': question.answer_d,
                    }
                })
        if action == 'checkAnswer':
            answer = payload.get('answer', None)
            if not answer:
                return JsonResponse({
                        'status': 'ERROR', 
                        'message': 'No answer supplied in request. Please report this.'
                        })
            if not quiz.timestop_active:
                quiz.timestop_active = False
                timedelta = timezone.now() - quiz.helperdatetime
                quiz.duration += timedelta.seconds
            question = self.get_question(quiz)
            # update answer count
            chosen_answers_count = json.loads(question.chosen_answers_count)
            chosen_answers_count[answer] += 1
            question.chosen_answers_count = json.dumps(chosen_answers_count)
            question.save()
            # check answer
            quiz.questions_index += 1
            if quiz.questions_index == quiz.questions_total:
                quiz.quizstate = Quiz.FINISHED
                quiz.enddatetime = timezone.now()
            if answer == question.correct_answer:
                quiz.questions_answered += 1
            elif quiz.quiztype == Quiz.SPRINT:
                quiz.quizstate = Quiz.FINISHED
                quiz.enddatetime = timezone.now()
            quiz.save()
            rank = self.get_ranking(quiz)
            return JsonResponse({
                'status': 'OK',
                'timePassed': quiz.duration,
                'correctAnswer': question.correct_answer,
                'rank': rank,
                'quizActive': quiz.quizstate == Quiz.IN_PROGRESS,
                'questionsIndex': quiz.questions_index,
                'questionsAnswered': quiz.questions_answered,
                'questionExplanation': question.explanation
                })
        return JsonResponse({'status': 'ERROR', 'message': 'You reached a deep dark point where you should not be... There are dragons! Please report this.'})


@method_decorator([check_bubble_permission(authenticated_only=True)], name='dispatch')
class QuestionList(View):
    
    def get(self, request, bubble_name):
        ctx = {}
        ctx['bubble_name'] = bubble_name
        bubble = Bubble.objects.get(name=bubble_name)
        questions = Question.objects.filter(bubble_id=bubble.id).order_by('id')
        ctx['questions'] = questions
        return render(request, 'quiz/question_list.html', ctx)


@method_decorator([check_bubble_permission(authenticated_only=True), check_question_permission], name='dispatch')
class EditQuestion(View):

    def get(self, request, bubble_name, question_id):
        ctx = {}
        ctx['bubble_name'] = bubble_name
        question = Question.objects.get(id=question_id)
        form = QuestionModelForm(instance=question)
        ctx['form'] = form
        return render(request, 'quiz/edit_question.html', ctx)

    @transaction.atomic
    def post(self, request, bubble_name, question_id):
        ctx = {}
        ctx['bubble_name'] = bubble_name
        question = Question.objects.get(id=question_id)
        if 'delete' in request.POST:
            question.delete()
            messages.info(request, f'Question {question_id} successfully deleted!')
            return redirect('question_list', bubble_name=bubble_name)
        form = QuestionModelForm(request.POST, instance=question)
        if not form.is_valid():
            messages.info(request, 'There were problems with your form. Please check the form field messages and submit again.')
            ctx['form'] = form
            return render(request, 'quiz/edit_question.html', ctx)
        form.save()
        messages.info(request, f'Question {question_id} successfully edited!')
        return redirect('question_list', bubble_name=bubble_name)

        