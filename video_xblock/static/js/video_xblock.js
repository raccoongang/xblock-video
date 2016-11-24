/* Javascript for VideoXBlock. */
function VideoXBlock(runtime, element) {

  var handlerUrl = runtime.handlerUrl(element, 'save_player_state');
  window.videoXBlockSaveHandlers = window.videoXBlockSaveHandlers || {};
  window.videoXBlockSaveHandlers[element.attributes['data-usage-id'].value] = handlerUrl;
  window.videoXBlockListenerRegistered = window.videoXBlockListenerRegistered || false;

  function saveState(handlerUrl, state) {
    // Saves video player satate by POSTing it to VideoXBlock handler
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
  }

  if (!window.videoXBlockListenerRegistered) {
    // Make sure we register event listener only once even if there are more than
    // one VideoXBlock on a page
    window.addEventListener("message", receiveMessage, false);
    window.videoXBlockListenerRegistered = true;
  }

  function receiveMessage(event) {
    var origin = event.origin || event.originalEvent.origin; // For Chrome, the origin property is in the event.originalEvent object.
    if (origin !== document.origin)
      // Discard a message received from another domain
      return;
    if (event.data && event.data.action === 'save_state' &&
        window.videoXBlockSaveHandlers[event.data.xblockUsageId]) {
      saveState(window.videoXBlockSaveHandlers[event.data.xblockUsageId], event.data.state);
    }
  }
}
