from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.db.models import F
import json
import random
from .decorators import session_authenticated
from .models import *
from .forms import *

import time


class Login(View):
    def get(self, request):
        ctx = {}
        return render(request, 'quiz/login.html', ctx)

    def post(self, request):
        response_json = {'status': 'ERROR'}
        payload = json.loads(request.body)
        if payload.get('password', None) == settings.PASSWORD:
            request.session['authenticated'] = True
            request.session.set_expiry(0)
            response_json['status'] = 'OK'
            response_json['successRedirectUrl'] = reverse('home')
        return JsonResponse(response_json)


@method_decorator([session_authenticated], name='dispatch')
class Home(View):

    def get_question_pks(self):
        all_questions = list(Question.objects.values_list('pk', 'difficulty'))
        random.shuffle(all_questions)
        question_dict = {difficulty: [] for difficulty, _ in Question.DIFFICULTIES}
        [question_dict[difficulty].append(pk) for pk, difficulty in all_questions]
        question_list = []
        for difficulty, _ in Question.DIFFICULTIES:
            question_list.extend(question_dict[difficulty][:settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY])
        return ','.join(str(pk) for pk in question_list)

    def get(self, request):
        ctx = {}
        ctx['sprint_champions'] = Game.objects\
            .filter(active=False, gametype=Game.SPRINT)\
            .order_by('-questions_answered', '-duration')[:5]
        ctx['marathon_champions'] = Game.objects\
            .filter(active=False, gametype=Game.MARATHON)\
            .order_by('-questions_answered')[:5]
        return render(request, 'quiz/home.html', ctx)

    def post(self, request):
        response_json = {
            'status': 'ERROR',
            'message': 'An unknown error occured, please report this.',
            'successRedirectUrl': '',
        }
        payload = json.loads(request.body)
        form = GamePlayernameGametypeForm(payload)
        if form.is_valid():
            # Only one game per session allowed.
            old_gameid = request.session.get('gameid', None)
            if old_gameid:
                Game.objects.filter(uuid=old_gameid).update(active=False)
                print('CLOSED GAME: ' + old_gameid)
            # Create new game
            game = Game.objects.create(**form.cleaned_data, question_ids=self.get_question_pks())
            print('CREATED GAME: ' + str(game.uuid))
            request.session['gameid'] = str(game.uuid)
            response_json['status'] = 'OK'
            response_json['message'] = ''
            response_json['successRedirectUrl'] = reverse('sprint')
        else:
            message = ' '.join([' '.join(x for x in l) for l in list(form.errors.values())])
            response_json['status'] = 'ERROR'
            response_json['message'] = message
        return JsonResponse(response_json)


@method_decorator([session_authenticated], name='dispatch')
class NewQuestion(View):
    def get(self, request):
        ctx = {}
        ctx['form'] = QuestionModelForm()
        return render(request, 'quiz/new_question.html', ctx)

    def post(self, request):
        ctx = {}
        form = QuestionModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        ctx['form'] = form
        return render(request, 'quiz/new_question.html', ctx)


@method_decorator([session_authenticated], name='dispatch')
class Sprint(View):

    def get_current_game(self, game_id):
        return get_object_or_404(Game, uuid=game_id)

    def get_current_question(self, game):
        question_pk = int(game.question_ids.split(',')[game.questions_answered])
        return get_object_or_404(Question, pk=question_pk)

    def get(self, request):
        ctx = {}
        return render(request, 'quiz/sprint.html', ctx)

    def post(self, request):
        time.sleep(0.5)
        payload = json.loads(request.body)
        action = payload.get('action', None)
        game_id = request.session.get('gameid', None)
        if not game_id:
            return JsonResponse({
                'status': 'ERROR', 
                'message': 'Error: No game was found that corresponds to this session. Please report this.'
                })
        if action not in ['checkAnswer', 'nextQuestion', 'closeGame']:
            return JsonResponse({
                'status': 'ERROR', 
                'message': 'Error: No valid action was supplied. Please report this.'
                })
        game = self.get_current_game(game_id)
        if not game.active:
            return JsonResponse({
                'status': 'ERROR',
                'message': f'Error: This game is not active anymore. Please start a <a class="text-warning" href=\"{reverse("home")}\">new game.</a>'
                })
        if action == 'nextQuestion':
            game = self.get_current_game(game_id)
            game.helperdatetime = timezone.now()
            game.save()
            question = self.get_current_question(game)
            return JsonResponse({
                'status': 'OK',
                'questionBody': question.question,
                'timePassed': game.duration,
                'questionsAnswered': game.questions_answered,
                'answerA': question.answer_a,
                'answerB': question.answer_b,
                'answerC': question.answer_c,
                'answerD': question.answer_d,
                })
        if action == 'checkAnswer':
            game = self.get_current_game(game_id)
            question = self.get_current_question(game)
            answer = payload.get('answer', None)
            timedelta = timezone.now() - game.helperdatetime
            game.duration += (timedelta.seconds - 1)
            correctly_answered = answer == question.correct_answer
            if correctly_answered:
                game.questions_answered += 1
            else:
                game.active = False
            game.save()
            return JsonResponse({
                'status': 'OK',
                'correctAnswer': correctly_answered,
                'questionExplanation': question.explanation
                })
        if action == 'closeGame':
            game.active = False
            game.save()
            return JsonResponse({
                'status': 'OK'
            })
        return JsonResponse({'status': 'OK', 'message': 'NO ERROR JUHUU'})