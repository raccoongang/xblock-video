/* global getHandlers */

/**
 * Tests for studio edit's utils
 */
describe('Runtime handlers', function() {
    'use strict';

    var handlersMap = {
        downloadTranscript: 'download_transcript',
        authenticateVideoApi: 'authenticate_video_api_handler',
        uploadDefaultTranscript: 'upload_default_transcript_handler',
        getTranscripts3playmediaApi: 'get_transcripts_3playmedia_api_handler',
        saveState: 'save_player_state',
        publishEvent: 'publish_event'
    };
    var invalidHandlers = {
        downloadTranscript: 'downloadTranscript',
        authenticateVideoApi: 'authenticateVideoApi',
        uploadDefaultTranscript: 'uploadDefaultTranscript',
        getTranscripts3playmediaApi: 'getTranscripts3playmediaApi',
        saveState: 'saveState',
        publishEvent: 'publishEvent'
    };
    var runtimeMock = {
        handlerUrl: function(el, handlerName) {
            return handlerName;
        }
    };

    it('returns expected handlers', function() {
        expect(getHandlers(runtimeMock, 'element'))
            .toEqual(handlersMap);
    });

    it("doesn't return invalid handlers", function() {
        expect(getHandlers(runtimeMock, 'element'))
            .not.toEqual(invalidHandlers);
    });
});
