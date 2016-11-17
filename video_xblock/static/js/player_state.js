var domReady = function(callback) {
    document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
};

var player_state = {
  'volume': {{ player_state.volume }},
  'currentTime': {{ player_state.current_time }},
  'playbackRate': {{ player_state.playback_rate }},
  'muted': {{ player_state.muted | yesno:"true,false" }}
};

var saveState = function(){
  var player = this;
  console.log('Save state');
  var new_state = {
    'volume': player.volume(),
    'currentTime': player.ended()? 0 : player.currentTime(),
    'playbackRate': player.playbackRate(),
    'muted': player.muted()
  };
  if (JSON.stringify(new_state) !== JSON.stringify(player_state)) {
    player_state = new_state;
    parent.postMessage({'action': 'save_state', 'state': new_state}, document.origin)
  };
};

var saveCurrentTime = function() {

};

domReady(function() {
  videojs('{{ video_player_id }}').ready(function() {
    var player = this;

    // Restore default or previously saved player state
    player.volume({{ player_state.volume }});
    player.muted({{ player_state.muted | yesno:"true,false" }});
    player.playbackRate({{ player_state.playback_rate }})

    player
      .on('volumechange', saveState)
      .on('ratechange', saveState);
      // .on('timeupdate', saveState);
  });
});
