/* VUE APP */
var app = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    messages: [],
    flipShowQuestion: false,
    gameStarted: false,
    timePassed: 0,
    loading: false,
    questionBody: '',
    questionExplanation: '',
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
  },
  methods: {
    startGame: function() {
      this.loading = true;
      this.ajaxPost({'action':'startGame'}, this.roundStart);
    },
    addMessage: function(message) {
      this.messages.push(message);
    },
    removeMessage: function(index) {
      this.messages.splice(index, 1);
    },
    roundStart: function(response) {
      const data = response.data;
      this.questionBody = data['questionBody'];
      this.answerA = data['answerA'];
      this.answerB = data['answerB'];
      this.answerC = data['answerC'];
      this.answerD = data['answerD'];
      this.loading = false;
      this.flipShowQuestion = true;
      this.startTimer();
      setTimeout(function() {
        this.gameStarted = true;
      }.bind(this), 1000);
    },
    answerClicked: function($event) {
      if (!event.target.classList.contains('answer')) {
        return;
      }
      this.chosenAnswer = event.target.id;
      this.loading = true;
      this.ajaxPost({'action':'checkAnswer', 'answer': this.chosenAnswer}, this.showAnswer);
    },
    showAnswer: function(response) {
      this.loading = false;
      this.flipShowQuestion = false;
      console.log(response.data)
    },
    startTimer: function() {
      this.timer = setInterval(function(){
        this.timePassed ++;
      }.bind(this), 1000);
    },
    stopTimer: function() {
      clearInterval(this.timer)
    },
    formattedTime: function() {
      let minutes = Math.floor(this.timePassed / 60);
      let seconds = this.timePassed - minutes * 60;
      let padding = seconds < 10 ? '0' : '';
      return minutes.toString() + ':' + padding + seconds.toString();
    },
    handleLeave: function() {
    },
    ajaxPost: function(data, successCallback, url='') {
      axios.post(url, data)
      .then(function(response) {
          if (response.data.message) {
            this.addMessage(response.data.message);
          }
          if (response.data.status === 'OK') {
            successCallback(response);
          }
        }.bind(this))
      .catch(function(error) {
        this.addMessage('An unexpected error occured. Please report this. Error message: "' + error + '"');
      }.bind(this));
    },
  }
})