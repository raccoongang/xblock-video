(function() {

  "use strict";

var Button = videojs.getComponent('Button');
var Component = videojs.getComponent('Component');

var ToggleButton = videojs.extend(Button, {
  constructor: function constructor(player, options) {
    this._options = options;
    Button.call(this, player, options);
    this.on('click', this.onClick);
    this.createEl();
  },
  styledSpan: function styledSpan() {
    return this._options['style'];
  },
  enabledEventName: function enabledEventName() {
    return this._options['enabledEvent'];
  },
  disabledEventName: function disabledEventName() {
    return this._options['disabledEvent'];
  },
  buildCSSClass: function buildCSSClass() {
    return this._options['cssClasses'];
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

    this.trigger(this.hasClass(el, 'vjs-control-enabled') ? this.enabledEventName() : this.disabledEventName());

  },

});

var toggleButton = function(options){
  this.controlBar.addChild('ToggleButton', options);
};

videojs.registerComponent('ToggleButton', ToggleButton);
videojs.plugin('toggleButton', toggleButton);

}(window, videojs));