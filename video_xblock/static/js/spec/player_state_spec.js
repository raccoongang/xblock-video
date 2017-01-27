describe('Player state', function() {
    'use strict';

    var player = {
        captionsLanguage: '{{transcript.lang}}'
    };
    beforeEach(function() {
        var video = document.createElement('video');
        video.id = '{{ video_player_id }}';
        video.className = 'video-js vjs-default-skin';
        video.setAttribute('data-setup', '{{ data_setup }}');
        document.body.appendChild(video);
    });
    it('return download transcript url', function() {
        expect(getDownloadTranscriptUrl(player)).toBe(transcripts['{{transcript.lang}}'].url); // eslint-disable-line
    });
});
