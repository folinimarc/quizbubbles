/* VUE APP */
var app = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    messages: [],
    gameStarted: false,
    awaitingAnswer: false,
    flipShowQuestion: false,
    timePassed: 0,
    loading: true,
    answersHidden: true,
    questionBody: '',
    questionExplanation: '',
    questionsAnswered: 0,
    questionDifficulty: '',
    answerA: '',
    answerB: '',
    answerC: '',
    answerD: '',
    chosenAnswer: null,
    correctAnswer: null,
    highlightClass: 'bg-warning',
  },
  mounted() {
    /* AXIOS CSRF CONFIGURATION */
    axios.defaults.xsrfCookieName = 'csrftoken'
    axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
    /* Handle window leave */
    window.addEventListener('beforeunload', this.handleLeave);
    /* make content visible */
    document.getElementById('app-wrapper').classList.remove('opacity-zero');
    /* start game */
    setTimeout(function() {
      this.nextQuestion();
      setTimeout(function() {
        this.gameStarted = true;
      }.bind(this), 2000);
    }.bind(this), 1000);
  },
  methods: {
    nextQuestion: function() {
      this.ajaxPost({'action':'nextQuestion'}, this.startNewRound);
    },
    startNewRound: function(response) {
      const data = response.data;
      this.questionBody = data['questionBody'];
      this.timePassed = data['timePassed'];
      this.questionsAnswered = data['questionsAnswered'];
      this.questionDifficulty = data['questionDifficulty'];
      this.flipShowQuestion = true;
      this.answersHidden = true;
      setTimeout(function() {
        this.answerA = data['answerA'];
        this.answerB = data['answerB'];
        this.answerC = data['answerC'];
        this.answerD = data['answerD'];
        this.answersHidden = false;
        this.awaitingAnswer = true;
        this.chosenAnswer = null;
        this.correctAnswer = null;
        this.startTimer();
      }.bind(this), 1000)
    },
    flipQuestion: function() {
      if (this.awaitingAnswer) {
        return;
      }
      this.flipShowQuestion = !this.flipShowQuestion;
    },
    addMessage: function(message) {
      this.messages.push(message);
    },
    removeMessage: function(index) {
      this.messages.splice(index, 1);
    },
    answerClicked: function($event) {
      if (!event.target.classList.contains('answer') || !this.awaitingAnswer) {
        return;
      }
      this.awaitingAnswer = false;
      this.chosenAnswer = event.target.id;
      this.stopTimer();
      this.ajaxPost({'action':'checkAnswer', 'answer': this.chosenAnswer}, this.showAnswer);
    },
    showAnswer: function(response) {
      const data = response.data;
      this.correctAnswer = data['correctAnswer'];
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
        return 'bg-primary no-pointerevents';
      } else if (this.correctAnswer == this.chosenAnswer) {
        return 'bg-success cursor-pointer';
      } else {
        return 'bg-danger cursor-pointer';
      }
    },
    questionNrAndDifficulty: function() {
      return (this.questionsAnswered + 1).toString() + ' (' + this.questionDifficulty + ')'
    },
    startTimer: function() {
      if (this.timer) {
        return
      }
      this.timer = setInterval(function(){
        this.timePassed ++;
      }.bind(this), 1000);
    },
    stopTimer: function() {
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
      this.ajaxPost({'action':'closeGame'}, function(response) {});
    },
    ajaxPost: function(data, successCallback, url='') {
      this.loading = true;
      axios.post(url, data)
      .then(function(response) {
          this.loading = false;
          if (response.data.message) {
            this.addMessage(response.data.message);
          }
          if (response.data.status === 'OK') {
            successCallback(response);
          }
        }.bind(this))
      .catch(function(error) {
        this.loading = false;
        this.addMessage('An unexpected error occured. Please report this. Error message: "' + error + '"');
      }.bind(this));
    },
  }
})