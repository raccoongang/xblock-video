describe('Base javascript', function() {
    'use strict';
    var playerId = 'test_id';
    var player = {
        captionsLanguage: 'en'
    };
    var testXblcokUsageId = 'block-v1:test+test+test+type@video_xblock+block@test';
    var transcripts = window.playerStateObj.transcripts_object;
    window.videoPlayerId = playerId;
    window.location.hash = '#' + testXblcokUsageId;
    beforeEach(function() {
        var video = document.createElement('video');
        video.id = playerId;
        video.className = 'video-js vjs-default-skin';
        document.body.appendChild(video);
    });
    it('return getXblockUsageId', function() {
        expect(getXblockUsageId(), testXblcokUsageId);
    });
    it('return download transcript url', function() {
        // TODO avoid the eslint shutdown for the implicity got variables
        expect(getDownloadTranscriptUrl(transcripts, player)).toBe(transcripts.en.url); // eslint-disable-line
    });
});
