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

    this.toggleButton({
      style: "icon fa fa-cc",
      enabledEvent: "captionenabled",
      disabledEvent: "captiondisabled",
      cssClasses: "vjs-custom-caption-button vjs-control",
    });
    this.toggleButton({
      style: "icon fa fa-quote-left",
      enabledEvent: "transcriptenabled",
      disabledEvent: "transcriptdisabled",
      cssClasses: "vjs-custom-transcript-button vjs-control",
    });
  });
});
