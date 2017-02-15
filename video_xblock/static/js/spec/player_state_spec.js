describe('Player state', function() {
    'use strict';
    var playerId = 'test_id';
    var player = {
        captionsLanguage: 'en'
    };
    window.video_player_id = playerId;
    beforeEach(function() {
        var video = document.createElement('video');
        video.id = playerId;
        video.className = 'video-js vjs-default-skin';
        document.body.appendChild(video);
    });
    it('return download transcript url', function() {
        expect(getDownloadTranscriptUrl(player)).toBe(transcripts['en'].url); // eslint-disable-line
    });
});
