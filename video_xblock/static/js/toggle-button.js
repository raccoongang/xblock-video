(function() {

  "use strict";

  var Button = videojs.getComponent('Button');
  var ToggleButton = videojs.extend(Button, {
    constructor: function constructor(player, options) {
      Button.call(this, player, options);
      this.on('click', this.onClick);
      this.createEl();
    },
    styledSpan: function styledSpan() {
      return this.options()['style'];
    },
    enabledEventName: function enabledEventName() {
      return this.options()['enabledEvent'];
    },
    disabledEventName: function disabledEventName() {
      return this.options()['disabledEvent'];
    },
    buildCSSClass: function buildCSSClass() {
      return this.options()['cssClasses'];
    },
    createEl: function createEl(props, attributes) {
      props = props || {};
      props['className'] = this.buildCSSClass();
      props['innerHTML'] = '<div class="vjs-control-content ' + this.styledSpan() + '"></div>';
      props['tabIndex'] = 0;
      props['role'] = 'button';
      props['aria-live'] = 'polite';

      return Button.prototype.createEl.call(this, arguments.tag, props, attributes);
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
