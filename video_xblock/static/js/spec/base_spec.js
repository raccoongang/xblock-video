describe('Base javascript', function() {
    'use strict';
    var playerId = 'test_id';
    var player = {
        captionsLanguage: 'en'
    };
    var transcripts = window.playerStateObj.transcripts_object;
    window.videoPlayerId = playerId;
    beforeEach(function() {
        var video = document.createElement('video');
        video.id = playerId;
        video.className = 'video-js vjs-default-skin';
        document.body.appendChild(video);
    });
    it('return download transcript url', function() {
        // TODO avoid the eslint shutdown for the implicity got variables
        expect(getDownloadTranscriptUrl(transcripts, player)).toBe(transcripts.en.url); // eslint-disable-line
    });
});
