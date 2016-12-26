var CaptionToggleButton = videojs.getComponent('CaptionToggleButton');

var TranscriptToggleButton = videojs.extend(CaptionToggleButton, {
  styledSpan() { return "trans"},
  enabledEventName(){ return "transcriptenabled"},
  disabledEventName(){ return "transcriptdisabled"},

  buildCSSClass() {
    return 'vjs-custom-transcript-button vjs-control';
  }

});


var transcriptButton = function (options){
  this.controlBar.addChild('TranscriptToggleButton', options);
};

videojs.registerComponent('TranscriptToggleButton', TranscriptToggleButton);

videojs.plugin('transcriptButton', transcriptButton);
