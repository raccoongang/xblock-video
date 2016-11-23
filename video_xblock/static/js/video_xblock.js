/* Javascript for VideoXBlock. */
function VideoXBlock(runtime, element) {

  var handlerUrl = runtime.handlerUrl(element, 'save_player_state');

  var saveState = function(state){
    $.ajax({
      type: "POST",
      url: handlerUrl,
      data: JSON.stringify(state),
    })
    .done(function() {
      console.log('Player state saved successfully');
    })
    .fail(function() {
      console.log("Failed to save player state");
    });
  };

  $(function ($) {
    window.addEventListener("message", receiveMessage, false);

    function receiveMessage(event)
    {
      var origin = event.origin || event.originalEvent.origin; // For Chrome, the origin property is in the event.originalEvent object.
      if (origin !== document.origin)
        // Discard a message received from another domain
        return;
      if (event.data && event.data.action === 'save_state') {
        saveState(event.data.state);
      }
    }
  });
}
