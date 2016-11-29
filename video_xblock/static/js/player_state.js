/**
 * This part is responsible for loading and saving player state.
 * State includes:
 * - Current time
 * - Playback rate
 * - Volume
 * - Muted
 *
 * State is loaded after VideoJs player is fully initialized.
 * State is saved at certain events.
 */
var domReady = function(callback) {
  /** Run a callback when DOM is fully loaded */
  if (document.readyState === "interactive" || document.readyState === "complete") {
    callback();
  } else {
    document.addEventListener("DOMContentLoaded", callback);
  }
};

var player_state = {
  'volume': {{ player_state.volume }},
  'currentTime': {{ player_state.current_time }},
  'playbackRate': {{ player_state.playback_rate }},
  'muted': {{ player_state.muted | yesno:"true,false" }},
};

var xblockUsageId = window.location.hash.slice(1);

var setInitialState = function(player, state) {
  /** Restore default or previously saved player state */
  if (state.currentTime > 0) {
    player.currentTime(state.currentTime);
  };
  player
    .volume(state.volume)
    .muted(state.muted)
    .playbackRate(state.playbackRate);
};

var saveState = function(){
  /**
   * Save player stat by posting it in a message to parent frame.
   * Parent frame passes it to a sever by calling VideoXBlock.save_state() handler
   */
  var player = this;
  var new_state = {
    'volume': player.volume(),
    'currentTime': player.ended()? 0 : Math.floor(player.currentTime()),
    'playbackRate': player.playbackRate(),
    'muted': player.muted(),
  };

  if (JSON.stringify(new_state) !== JSON.stringify(player_state)) {
    console.log('Starting saving player state');
    player_state = new_state;
    parent.postMessage({'action': 'save_state', 'state': new_state, 'xblockUsageId': xblockUsageId}, document.origin)
  };
};

domReady(function() {
  videojs('{{ video_player_id }}').ready(function() {
    var player = this;

    // Restore default or previously saved player state
    setInitialState(player, player_state);

    player
      .on('volumechange', saveState)
      .on('ratechange', saveState)
      .on('play', saveState)
      .on('pause', saveState)
      .on('ended', saveState);
  });
});
