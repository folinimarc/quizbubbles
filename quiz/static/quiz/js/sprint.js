/* VUE APP */
var app = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    messages: [],
    flipShowQuestion: false,
    timePassed: 0,
    loading: true,
    correctAnswer: false,
    answersHidden: true,
    questionBody: '',
    questionExplanation: '',
    questionsAnswered: 0,
    answerA: '',
    answerB: '',
    answerC: '',
    answerD: '',
    chosenAnswer: '',
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
    }.bind(this), 1000)
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
      this.flipShowQuestion = true;
      this.answersHidden = true;
      setTimeout(function() {
        this.answerA = data['answerA'];
        this.answerB = data['answerB'];
        this.answerC = data['answerC'];
        this.answerD = data['answerD'];
        this.answersHidden = false;
        this.startTimer();
      }.bind(this), 1000)
    },
    addMessage: function(message) {
      this.messages.push(message);
    },
    removeMessage: function(index) {
      this.messages.splice(index, 1);
    },
    answerClicked: function($event) {
      if (!event.target.classList.contains('answer')) {
        return;
      }
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