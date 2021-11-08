/**
 * This part is responsible for initialization of TCPlayer.
 */

domReady(function() {
    'use strict';
    var player = TCPlayer('{{ video_player_id }}', { /** player-container-id is the player container ID, which must be the same as in html */
        fileID: "{{ video_id }}", /** Enter the fileID of the video to be played (required). */
        appID: "{{ app_id }}", /** Enter the appID of the VOD account (required). */
        psign: ""
    });
});
