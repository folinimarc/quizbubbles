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
import json
import random
from .decorators import session_authenticated, questionedit_authenticated
from .models import *
from .forms import *
from collections import OrderedDict

import time


class Login(View):
    def get(self, request):
        if (request.session.get('spaceid', False)):
            return redirect('home')
        ctx = {}
        ctx['join_form'] = SpaceJoinForm()
        ctx['create_form'] = SpaceCreateForm()
        ctx['flipShowJoin'] = True
        return render(request, 'quiz/login.html', ctx)

    @transaction.atomic
    def post(self, request):
        ctx = {}
        # handle join request
        if 'join' in request.POST:
            join_form = SpaceJoinForm(request.POST)
            if join_form.is_valid():
                space = Space.objects.filter(name=join_form.cleaned_data['name']).first()
                if space and check_password(join_form.cleaned_data['password'], space.password):
                    request.session['spaceid'] = str(space.uuid)
                    return redirect('home')
                join_form.add_error('password', 'Wrong spacename or password')
            ctx['flipShowJoin'] = True
            ctx['join_form'] = join_form
            ctx['create_form'] = SpaceCreateForm()
            return render(request, 'quiz/login.html', ctx)

        # handle create request
        if 'create' in request.POST:
            create_form = SpaceCreateForm(request.POST)
            if create_form.is_valid():
                # Enforce uniqueness of name
                if Space.objects.filter(name=create_form.cleaned_data['name']).exists():
                    create_form.add_error('name', 'Name already in use')
                else:
                    # create quizspace
                    space = Space.objects.create(
                        name = create_form.cleaned_data['name'],
                        email = create_form.cleaned_data['email'],
                        password = make_password(create_form.cleaned_data['password1'])
                    )
                    messages.info(request, f'New quizspace \"{create_form.cleaned_data["name"]}\" successfully created. Click to hide me. Have fun!')
                    request.session['spaceid'] = str(space.uuid)
                    return redirect('home')
            ctx['flipShowJoin'] = False
            ctx['join_form'] = SpaceJoinForm()
            ctx['create_form'] = create_form
            return render(request, 'quiz/login.html', ctx)

        return redirect('login')


class Logout(View):
    def get(self, request):
        request.session.pop('spaceid', None)
        request.session.pop('gameid', None)
        request.session.pop('contributor', None)
        return redirect('login')


@method_decorator([session_authenticated], name='dispatch')
class Home(View):

    def get_sprint_question_pks(self, space):
        all_questions = list(Question.objects.filter(space_id=space.id).values_list('pk', 'difficulty'))
        random.shuffle(all_questions)
        question_dict = {difficulty: [] for difficulty, _ in Question.DIFFICULTIES}
        [question_dict[difficulty].append(pk) for pk, difficulty in all_questions]
        question_list = []
        for difficulty, _ in Question.DIFFICULTIES:
            question_list.extend(question_dict[difficulty][:settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY])
        questions_total = len(question_list)
        return questions_total, ','.join(str(pk) for pk in question_list)

    def get_marathon_question_pks(self, space):
        question_list = list(Question.objects.filter(space_id=space.id).values_list('pk', flat=True))
        random.shuffle(question_list)
        questions_total = len(question_list)
        return questions_total, ','.join(str(pk) for pk in question_list)

    def get(self, request):
        ctx = {}
        space = Space.objects.get(uuid=request.session['spaceid'])
        difficulty_counts = Question.objects.filter(space_id=space.id).values('difficulty').annotate(count=Count('difficulty'))
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
        nr_questions = Question.objects.filter(space_id=space.id).count()
        ctx['nr_sprint_questions'] = len(Question.DIFFICULTIES * settings.SPRINT_NR_QUESTIONS_PER_DIFFICULTY)
        ctx['nr_questions'] = nr_questions
        ctx['sprint_champions'] = Game.objects\
            .filter(space_id=space.id, active=False, gametype=Game.SPRINT)\
            .order_by('-questions_answered', 'duration')[:settings.NR_LEADERBOARD_ENTRIES_TO_SHOW]
        ctx['marathon_champions'] = Game.objects\
            .filter(space_id=space.id, active=False, gametype=Game.MARATHON)\
            .order_by('-questions_answered', 'duration')[:settings.NR_LEADERBOARD_ENTRIES_TO_SHOW]
        ctx['nr_games'] = Game.objects.filter(space_id=space.id).count()
        ctx['space_name'] = space.name
        return render(request, 'quiz/home.html', ctx)

    @transaction.atomic
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
        space = Space.objects.get(uuid=request.session['spaceid'])
        if form.cleaned_data['gametype'] == Game.SPRINT:
            questions_total, question_ids = self.get_sprint_question_pks(space)
        elif form.cleaned_data['gametype'] == Game.MARATHON:
            questions_total, question_ids = self.get_marathon_question_pks(space)
        else:
            return JsonResponse({
                'status': 'ERROR', 
                'message': f'Unknown gametype {form.cleaned_data["gametype"]}'
                })
        game = Game.objects.create(
            **form.cleaned_data, 
            questions_total=questions_total,
            question_ids=question_ids,
            space_id=space.id
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
        ctx['form'] = QuestionModelForm(initial={'contributor': request.session.get('contributor', None)})
        return render(request, 'quiz/new_question.html', ctx)

    @transaction.atomic
    def post(self, request):
        ctx = {}
        space = Space.objects.get(uuid=request.session['spaceid'])
        form = QuestionModelForm(request.POST)
        if form.is_valid():
            Question.objects.create(
                **form.cleaned_data,
                space_id=space.id
            )
            request.session['contributor'] = form.cleaned_data['contributor']
            messages.info(request, 'Thank you! Your question was added.')
            return redirect('new_question')
        else:
            messages.info(request, 'There were problems with your form. Please check the form field messages and submit again.')
        ctx['form'] = form
        return render(request, 'quiz/new_question.html', ctx)


@method_decorator([session_authenticated], name='dispatch')
class Quiz(View):

    def get_current_game(self, game_id):
        return get_object_or_404(Game, uuid=game_id)

    def get_current_question(self, game):
        question_pk = int(game.question_ids.split(',')[game.questions_answered])
        return get_object_or_404(Question, pk=question_pk)

    def get_ranking(self, game):
        outperform_questions = Game.objects.filter(space_id=game.space_id, active=False, gametype=game.gametype, questions_answered__gt=game.questions_answered).count()
        outperform_time = Game.objects.filter(space_id=game.space_id, active=False, gametype=game.gametype, questions_answered=game.questions_answered, duration__lt=game.duration).count()
        rank = outperform_questions + outperform_time + 1
        return rank

    def get(self, request):
        ctx = {}
        return render(request, 'quiz/quiz.html', ctx)

    @transaction.atomic
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
        if action not in ['getGameData', 'checkAnswer', 'nextQuestion', 'closeGame', 'jokerFiftyFifty', 'jokerAudience', 'jokerTimestop']:
            return JsonResponse({
                'status': 'ERROR', 
                'message': 'No valid action was supplied. Please report this.'
                })
        game = self.get_current_game(game_id)
        if not game.active:
            return JsonResponse({
                'status': 'ERROR',
                'message': f'This game is not active anymore. Please start a new game.'
                })
        if action == 'getGameData':
            game = self.get_current_game(game_id)
            rank = self.get_ranking(game)
            total_games = Game.objects.filter(space_id=game.space_id, active=False, gametype=game.gametype).count()
            return JsonResponse({
                'status': 'OK',
                'gametype': game.get_gametype_display(),
                'timePassed': game.duration,
                'rank': rank,
                'gamesTotal': total_games,
                'questionsAnswered': game.questions_answered,
                'questionsTotal': game.questions_total,
                })
        if action == 'jokerAudience':
            game = self.get_current_game(game_id)
            if not game.joker_audience_available:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'Audience joker is not available anymore.',
                    })
            game.joker_audience_available = False
            game.save()
            question = self.get_current_question(game)
            chosen_answers_count = json.loads(question.chosen_answers_count)
            return JsonResponse({
                    'status': 'OK', 
                    'chosen_answers_count': chosen_answers_count
                    })
        if action == 'jokerFiftyFifty':
            game = self.get_current_game(game_id)
            if not game.joker_fiftyfifty_available:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'Fifty-fifty joker is not available anymore.',
                    })
            game.joker_fiftyfifty_available = False
            game.save()
            question = self.get_current_question(game)
            kill = random.sample({'a','b','c','d'}.difference({question.correct_answer}), 2)
            return JsonResponse({
                    'status': 'OK', 
                    'kill': kill
                    })
        if action == 'jokerTimestop':
            game = self.get_current_game(game_id)
            if not game.joker_timestop_available:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'Timestop joker is not available anymore.',
                    })
            game.joker_timestop_available = False
            game.timestop_active = True
            game.save()
            return JsonResponse({
                    'status': 'OK', 
                    'timePassed': game.duration
                    })

        if action == 'nextQuestion':
            game = self.get_current_game(game_id)
            game.helperdatetime = timezone.now()
            game.intermezzo_state = False
            game.save()
            question = self.get_current_question(game)
            return JsonResponse({
                'status': 'OK',
                'question': {
                    'header': f'Question {game.questions_answered + 1} ({question.get_difficulty_display()})',
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
            game = self.get_current_game(game_id)
            if not game.timestop_active:
                game.timestop_active = False
                timedelta = timezone.now() - game.helperdatetime
                game.duration += timedelta.seconds
            game.intermezzo_state = True
            question = self.get_current_question(game)
            # update answer count
            chosen_answers_count = json.loads(question.chosen_answers_count)
            chosen_answers_count[answer] += 1
            question.chosen_answers_count = json.dumps(chosen_answers_count)
            question.save()
            # check answer
            if answer == question.correct_answer:
                game.questions_answered += 1
                if game.questions_answered == game.questions_total:
                    game.active = False
                    game.enddatetime = timezone.now()
            else:
                game.active = False
                game.enddatetime = timezone.now()
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
                game.enddatetime = timezone.now()
                game.active = False
                game.save()
            return JsonResponse({
                'status': 'OK'
            })
        return JsonResponse({'status': 'ERROR', 'message': 'You reached a deep dark point where you should not be... There are dragons! Please report this.'})


@method_decorator([session_authenticated], name='dispatch')
class QuestionList(View):
    
    def get(self, request):
        ctx = {}
        space = Space.objects.filter(uuid=request.session.get('spaceid', None)).first()
        questions = Question.objects.filter(space_id=space.id).order_by('id')
        ctx['questions'] = questions
        return render(request, 'quiz/question_list.html', ctx)


@method_decorator([questionedit_authenticated], name='dispatch')
class EditQuestion(View):

    def get(self, request, question_id):
        ctx = {}
        question = Question.objects.get(id=question_id)
        form = QuestionModelForm(instance=question)
        ctx['form'] = form
        return render(request, 'quiz/edit_question.html', ctx)

    @transaction.atomic
    def post(self, request, question_id):
        ctx = {}
        question = Question.objects.get(id=question_id)
        if 'delete' in request.POST:
            question.delete()
            messages.info(request, f'Question {question_id} successfully deleted!')
            return redirect('question_list')
        form = QuestionModelForm(request.POST, instance=question)
        if not form.is_valid():
            messages.info(request, 'There were problems with your form. Please check the form field messages and submit again.')
            ctx['form'] = form
            return render(request, 'quiz/edit_question.html', ctx)
        form.save()
        messages.info(request, f'Question {question_id} successfully edited!')
        return redirect('question_list')

        