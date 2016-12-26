var Button = videojs.getComponent('Button');
var Component = videojs.getComponent('Component');

var CaptionToggleButton = videojs.extend(Button, {
  constructor: function(player, options){
    Button.call(this, player, options);
    this.on('click', this.onClick);
    this.createEl();
  },
  styledSpan() { return "capt"},
  enabledEventName(){ return "captionenabled"},
  disabledEventName(){ return "captiondisabled"},
  buildCSSClass() {
    return 'vjs-custom-caption-button vjs-control';
  },
  createEl(tag='button', props={}, attributes={}){
    props = {
      className: this.buildCSSClass(),
      innerHTML: '<div class="vjs-control-content">' + this.styledSpan() + '</div>',
      tabIndex: 0,
      role: "button",
      'aria-live': 'polite'
    };
    let el = Component.prototype.createEl.call(this, tag, props, attributes);
    return el;
  },
  onClick(event) {
    let el = event.currentTarget;
    el.classList.toggle('vjs-control-enabled');

    var event = document.createEvent('Event');

    if (this.hasClass(el, 'vjs-control-enabled')){
      event.initEvent(this.enabledEventName(), true, true);
    } else {
      event.initEvent(this.disabledEventName(), true, true);
    };

    el.dispatchEvent(event);
  },

  hasClass(element, cls) {
    return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
  }
});

var captionButton = function(options){
  this.controlBar.addChild('CaptionToggleButton', options);
};

videojs.registerComponent('CaptionToggleButton', CaptionToggleButton);
videojs.plugin('captionButton', captionButton);
