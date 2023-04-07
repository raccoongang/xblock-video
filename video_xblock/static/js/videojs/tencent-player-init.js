/**
 * This part is responsible for initialization of TCPlayer.
 */

domReady(function() {
    'use strict';
    var player = TCPlayer('{{ video_player_id }}', {
        fileID: "{{ video_id }}",
        appID: "{{ app_id }}",
        psign: "",
        language: "{{ lang_code }}",
    });
});
