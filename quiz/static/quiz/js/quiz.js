"use strict";

/* VUE APP */
var app = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    messages: [],
    errorOccured: false,
    quizStarted: false,
    quizActive: true,
    awaitingAnswer: false,
    flipShowQuestion: false,
    timePassed: 0,
    loading: true,
    quizesTotal: 0,
    rank: 0,
    quiztype: 'Loading...',
    question: {'header': '', 'body': ''},
    questionExplanation: '',
    questionsAnswered: 0,
    questionsTotal: 0,
    answers: {'a': '', 'b': '', 'c': '', 'd':''},
    letters: {'a': 'A', 'b': 'B', 'c': 'C', 'd':'D'},
    questionHeader: '',
    chosenAnswer: null,
    correctAnswer: null,
    jokerFiftyFiftyAvailable: true,
    jokerAudienceAvailable: true,
    jokerTimestopAvailable: true,
    hiddenAnswers: ['a', 'b', 'c', 'd'],
    sentLove: false
  },
  mounted() {
    /* AXIOS CSRF CONFIGURATION */
    axios.defaults.xsrfCookieName = 'csrftoken'
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
    /* Handle window leave */
    window.addEventListener('beforeunload', this.handleLeave);
    /* make content visible */
    document.getElementById('app-wrapper').classList.remove('opacity-zero');
    /* start quiz */
    setTimeout(function() {
      this.getQuizData();
      setTimeout(function() {
        this.quizStarted = true;
      }.bind(this), 2000);
    }.bind(this), 1000);
  },
  computed: {
    answeredCorrectly: function() {
      return this.chosenAnswer === this.correctAnswer;
    },
    heartIcon: function() {
      return this.sentLove ? 'favorite' : 'favorite_outline';
    }
  },
  methods: {
    jokerFiftyFifty: function() {
      if (!this.awaitingAnswer || !this.jokerFiftyFiftyAvailable) return;
      this.jokerFiftyFiftyAvailable = false;
      this.ajaxPost({'action':'jokerFiftyFifty'}, function(response) {
        this.hiddenAnswers = response.data['kill'];
      }.bind(this));
    },
    jokerAudience: function() {
      if (!this.awaitingAnswer || !this.jokerAudienceAvailable) return;
      this.jokerAudienceAvailable = false;
      this.ajaxPost({'action':'jokerAudience'}, function(response) {
        this.letters = response.data['chosen_answers_count'];
      }.bind(this));
    },
    jokerTimestop: function() {
      if (!this.awaitingAnswer || !this.jokerTimestopAvailable) return;
      this.jokerTimestopAvailable = false;
      this.ajaxPost({'action':'jokerTimestop'}, function(response) {
        this.timePassed = response.data['timePassed'];
        this.stopTimer();
      }.bind(this));
    },
    nextQuestion: function() {
      this.letters = {'a': 'A', 'b': 'B', 'c': 'C', 'd':'D'};
      this.ajaxPost({'action':'nextQuestion'}, this.startNewRound);
    },
    startNewRound: function(response) {
      const data = response.data;
      this.question = Object.assign(this.question, data['question']);
      this.hiddenAnswers = ['a', 'b', 'c', 'd'];
      this.flipShowQuestion = true;
      setTimeout(function() {
        this.answers = data['answers'];
        this.hiddenAnswers = [];
        this.awaitingAnswer = true;
        this.chosenAnswer = null;
        this.correctAnswer = null;
        this.startTimer();
      }.bind(this), 1000)
    },
    getQuizData: function() {
      this.ajaxPost({'action':'getQuizData'}, function(response) {
        const data = response.data;
        this.timePassed = data['timePassed'];
        this.quizesTotal = data['quizesTotal'];
        this.quiztype = data['quiztype'];
        this.rank = data['rank'];
        this.questionsAnswered = data['questionsAnswered'];
        this.questionsTotal = data['questionsTotal'];
        this.nextQuestion();
      }.bind(this));
    },
    flipQuestion: function() {
      if (this.awaitingAnswer) return;
      this.flipShowQuestion = !this.flipShowQuestion;
    },
    addMessage: function(message) {
      this.messages.push(message);
      // remove after 3 seconds
      setTimeout(function() {
        let i = this.messages.indexOf(message)
        if (i >= 0) this.messages.splice(i, 1);
      }.bind(this), 3000);
    },
    removeMessage: function(index) {
      this.messages.splice(index, 1);
    },
    answerClicked: function($event) {
      if (!event.target.classList.contains('answer') || !this.awaitingAnswer) return;
      this.awaitingAnswer = false;
      this.chosenAnswer = event.target.id;
      this.stopTimer();
      this.ajaxPost({'action':'checkAnswer', 'answer': this.chosenAnswer}, this.checkAnswer);
    },
    checkAnswer: function(response) {
      const data = response.data;
      this.timePassed = data['timePassed'];
      this.correctAnswer = data['correctAnswer'];
      this.rank = data['rank'];
      this.quizActive = data['quizActive'];
      this.questionsAnswered = data['questionsAnswered'];
      this.questionExplanation = data['questionExplanation'];
      this.flipShowQuestion = false;
    },
    getAnswerClass: function(answer) {
      if (this.correctAnswer == answer) {
        return 'bg-success text-white';
      } else if(this.chosenAnswer == answer && this.correctAnswer === null) {
        return 'bg-warning';
      } else if (this.chosenAnswer == answer && this.correctAnswer != answer) {
        return 'bg-danger text-white';
      } else {
        return 'bg-light';
      }
    },
    getQuestionClass: function() {
      if (this.correctAnswer === null) {
        return 'bg-primary';
      } else if (this.correctAnswer == this.chosenAnswer) {
        return 'bg-success cursor-pointer';
      } else {
        return 'bg-danger cursor-pointer';
      }
    },
    startTimer: function() {
      if (this.timer) return;
      this.timer = setInterval(function(){
        this.timePassed ++;
      }.bind(this), 1000);
    },
    stopTimer: function() {
      if (!this.timer) return;
      clearInterval(this.timer);
      this.timer = null;
    },
    formattedTime: function() {
      let minutes = Math.floor(this.timePassed / 60);
      let seconds = this.timePassed - minutes * 60;
      let padding = seconds < 10 ? '0' : '';
      return minutes.toString() + ':' + padding + seconds.toString();
    },
    handleLeave: function() {
      if (this.quizActive) {
        this.ajaxPost({'action':'closeQuiz'}, function(response) {});
      }
    },
    handleError: function(errorMsg) {
      this.errorOccured = true;
      this.loading = false;
      this.awaitingAnswer = true;
      this.flipShowQuestion = false;
      this.addMessage(errorMsg);
    },
    ajaxPost: function(data, successCallback, url='') {
      this.loading = true;
      axios.post(url, data)
      .then(function(response) {
          this.loading = false;
          if (response.data.status === 'ERROR') {
            this.handleError(response.data.message);
          }
          if (response.data.status === 'OK') {
            successCallback(response);
            if (response.data.message) {
              this.addMessage(response.data.message);
            }
          }
        }.bind(this))
      .catch(this.handleError);
    },
  }
})