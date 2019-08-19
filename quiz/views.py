from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.db.models import F
from django.contrib import messages
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
            return JsonResponse({
                'status': 'OK', 
                'successRedirectUrl': reverse('home')
                })
        return JsonResponse({
                'status': 'ERROR', 
                'message': 'Password was rejected'
                })


@method_decorator([session_authenticated], name='dispatch')
class Home(View):

    def get_sprint_question_pks(self):
        all_questions = list(Question.objects.values_list('pk', 'difficulty'))
        random.shuffle(all_questions)
        question_dict = {difficulty: [] for difficulty, _ in Question.DIFFICULTIES}
        [question_dict[difficulty].append(pk) for pk, difficulty in all_questions]
        question_list = []
        for difficulty, _ in Question.DIFFICULTIES:
            question_list.extend(question_dict[difficulty][:settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY])
        questions_total = len(Question.DIFFICULTIES * settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY)
        return questions_total, ','.join(str(pk) for pk in question_list)

    def get_marathon_question_pks(self):
        question_list = list(Question.objects.values_list('pk', flat=True))
        random.shuffle(question_list)
        questions_total = len(question_list)
        return questions_total, ','.join(str(pk) for pk in question_list)

    def get(self, request):
        ctx = {}
        ctx['nr_sprint_questions'] = settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY * len(Question.DIFFICULTIES)
        ctx['nr_marathon_questions'] = Question.objects.all().count()
        ctx['sprint_champions'] = Game.objects\
            .filter(active=False, gametype=Game.SPRINT)\
            .order_by('-questions_answered', 'duration')[:settings.NR_LEADERBOARD_ENTRIES_TO_SHOW]
        ctx['marathon_champions'] = Game.objects\
            .filter(active=False, gametype=Game.MARATHON)\
            .order_by('-questions_answered', 'duration')[:settings.NR_LEADERBOARD_ENTRIES_TO_SHOW]
        return render(request, 'quiz/home.html', ctx)

    def post(self, request):
        payload = json.loads(request.body)
        action = payload.get('action', None)
        if action not in ['startSprint', 'startMarathon']:
            return JsonResponse({
                'status': 'ERROR', 
                'message': 'No valid action was supplied. Please report this.'
                })
        form = GamePlayernameGametypeForm(payload)
        if not form.is_valid():
            return JsonResponse({
                'status': 'ERROR', 
                'message': form.get_form_errors_as_string()
                })
        # Only one game per session allowed.
        old_gameid = request.session.get('gameid', None)
        if old_gameid:
            Game.objects.filter(uuid=old_gameid).update(active=False)
        # Create new game
        if form.cleaned_data['gametype'] == Game.SPRINT:
            questions_total, question_ids = self.get_sprint_question_pks()
        elif form.cleaned_data['gametype'] == Game.MARATHON:
            questions_total, question_ids = self.get_marathon_question_pks()
        else:
            return JsonResponse({
                'status': 'ERROR', 
                'message': f'Unknown gametype {form.cleaned_data["gametype"]}'
                })
        game = Game.objects.create(
            **form.cleaned_data, 
            questions_total=questions_total,
            question_ids=question_ids
            )
        request.session['gameid'] = str(game.uuid)
        return JsonResponse({
                'status': 'OK', 
                'message': '',
                'successRedirectUrl': reverse('quiz')
                })


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
            messages.info(request, 'Thank you! Your question was added.')
            return redirect('home')
        ctx['form'] = form
        messages.info(request, 'There were problems with your form. Please check the form field messages and submit again.')
        return render(request, 'quiz/new_question.html', ctx)


@method_decorator([session_authenticated], name='dispatch')
class Quiz(View):

    def get_current_game(self, game_id):
        return get_object_or_404(Game, uuid=game_id)

    def get_current_question(self, game):
        question_pk = int(game.question_ids.split(',')[game.questions_answered])
        return get_object_or_404(Question, pk=question_pk)

    def get_ranking(self, game):
        outperform_questions = Game.objects.filter(active=False, gametype=game.gametype, questions_answered__gt=game.questions_answered).count()
        outperform_time = Game.objects.filter(active=False, gametype=game.gametype, questions_answered=game.questions_answered, duration__lt=game.duration).count()
        rank = outperform_questions + outperform_time + 1
        return rank

    def get(self, request):
        ctx = {}
        return render(request, 'quiz/quiz.html', ctx)

    def post(self, request):
        #time.sleep(0.5)
        payload = json.loads(request.body)
        action = payload.get('action', None)
        game_id = request.session.get('gameid', None)
        if not game_id:
            return JsonResponse({
                'status': 'ERROR', 
                'message': 'No game was found that corresponds to this session. Please report this.'
                })
        if action not in ['getGameData', 'checkAnswer', 'nextQuestion', 'closeGame']:
            return JsonResponse({
                'status': 'ERROR', 
                'message': 'No valid action was supplied. Please report this.'
                })
        game = self.get_current_game(game_id)
        if not game.active:
            return JsonResponse({
                'status': 'ERROR',
                'message': f'This game is not active anymore. Please start a <a class="text-warning" href=\"{reverse("home")}\">new game.</a>'
                })
        if action == 'getGameData':
            game = self.get_current_game(game_id)
            rank = self.get_ranking(game)
            total_games = Game.objects.filter(active=False, gametype=game.gametype).count()
            return JsonResponse({
                'status': 'OK',
                'gametype': game.get_gametype_display(),
                'timePassed': game.duration,
                'rank': rank,
                'gamesTotal': total_games,
                'questionsAnswered': game.questions_answered,
                'questionsTotal': game.questions_total,
                })
        if action == 'nextQuestion':
            game = self.get_current_game(game_id)
            game.helperdatetime = timezone.now()
            game.intermezzo_state = False
            game.save()
            question = self.get_current_question(game)
            return JsonResponse({
                'status': 'OK',
                'questionBody': question.question,
                'questionDifficulty': question.get_difficulty_display(),
                'answerA': question.answer_a,
                'answerB': question.answer_b,
                'answerC': question.answer_c,
                'answerD': question.answer_d,
                })
        if action == 'checkAnswer':
            answer = payload.get('answer', None)
            game = self.get_current_game(game_id)
            question = self.get_current_question(game)
            timedelta = timezone.now() - game.helperdatetime
            game.duration += timedelta.seconds
            game.intermezzo_state = True
            if answer == question.correct_answer:
                game.questions_answered += 1
                if game.questions_answered == game.questions_total:
                    game.active = False
            else:
                game.active = False
            game.save()
            rank = self.get_ranking(game)
            return JsonResponse({
                'status': 'OK',
                'timePassed': game.duration,
                'correctAnswer': question.correct_answer,
                'rank': rank,
                'gameActive': game.active,
                'questionsAnswered': game.questions_answered,
                'questionExplanation': question.explanation
                })
        if action == 'closeGame':
            game = self.get_current_game(game_id)
            if not game.intermezzo_state:
                game.active = False
                game.save()
            return JsonResponse({
                'status': 'OK'
            })
        return JsonResponse({'status': 'OK', 'message': 'NO ERROR JUHUU'})