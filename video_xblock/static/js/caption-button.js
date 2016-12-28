(function() {

  "use strict";

var Button = videojs.getComponent('Button');
var Component = videojs.getComponent('Component');

var ToggleButton = videojs.extend(Button, {
  constructor: function constructor(player, options) {
    Button.call(this, player, options);
    this.on('click', this.onClick);
    this.createEl();
    this.options = options;
  },
  styledSpan: function styledSpan() {
    return this.options['style'];
  },
  enabledEventName: function enabledEventName() {
    return this.options['enabledEvent'];
  },
  disabledEventName: function disabledEventName() {
    return this.options['disabledEvent'];
  },
  buildCSSClass: function buildCSSClass() {
    return this.options['cssClasses'];
  },
  createEl: function createEl() {
    var tag = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 'button';
    var props = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    var attributes = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};

    props = {
      className: this.buildCSSClass(),
      innerHTML: '<div class="vjs-control-content">' + this.styledSpan() + '</div>',
      tabIndex: 0,
      role: "button",
      'aria-live': 'polite'
    };
    var el = Component.prototype.createEl.call(this, tag, props, attributes);
    return el;
  },
  onClick: function onClick(event) {
    var el = event.currentTarget;
    el.classList.toggle('vjs-control-enabled');

    //var event = document.createEvent('Event');
    this.trigger(this.hasClass(el, 'vjs-control-enabled') ? this.enabledEventName() : this.disabledEventName());

    // if (this.hasClass(el, 'vjs-control-enabled')) {
    //   event.initEvent(this.enabledEventName(), true, true);
    // } else {
    //   event.initEvent(this.disabledEventName(), true, true);
    // };

    // this.trigger(event);
  },

});

var toggleButton = function(options){
  this.controlBar.addChild('ToggleButton', options);
};

videojs.registerComponent('ToggleButton', ToggleButton);
videojs.plugin('toggleButton', toggleButton);

}(window, videojs));