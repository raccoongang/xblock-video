describe('Player state', function() {
    'use strict';
    var player = {
        captionsLanguage: '{{transcript.lang}}'
    };
    it('return download transcript url', function() {
        expect(getDownloadTranscriptUrl(player)).toBe(transcripts['{{transcript.lang}}'].url); // eslint-disable-line
    });
});
