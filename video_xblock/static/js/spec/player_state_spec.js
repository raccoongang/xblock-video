describe('Player state', function () {
    'use strict';
    var player_id = 'test_id';
    var player = {
        captionsLanguage: 'en'
    };
    window.video_player_id = player_id;
    beforeEach(function () {
        var video = document.createElement('video');
        video.id = player_id;
        video.className = 'video-js vjs-default-skin';
        document.body.appendChild(video);
    });
    it('return download transcript url', function () {
        expect(getDownloadTranscriptUrl(player)).toBe(transcripts['en'].url); // eslint-disable-line
    });
});
