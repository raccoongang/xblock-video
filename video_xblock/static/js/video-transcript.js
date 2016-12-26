domReady(function() {
  var player = videojs('{{ video_player_id }}').ready(function(){
    // fire up the plugin
    var transcript = this.transcript({
      followPlayerTrack: true,
      showTrackSelector: true
    });
    // attach the widget to the page
    var transcriptContainer = document.querySelector('#transcript');
    transcriptContainer.appendChild(transcript.el());

});
player.captionButton();
player.transcriptButton();
})
// initialize video.js
