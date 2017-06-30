/* global parseRelativeTime validateTranscripts*/
/**
 * Tests for transcripts manual upload
 */

describe('Transcripts manual upload', function() {
    'use strict';
    it('return parseRelativeTime', function() {
        var tests = {
            0: '00:00:00',
            1234: '00:20:34',
            12345: '03:25:45',
            86399: '23:59:59',
            99999: '23:59:59',
            '-1': '00:00:00',
            '0:0:0': '00:00:00',
            '0:12:34': '00:12:34',
            '12:30': '00:12:30'
        };
        Object.keys(tests).forEach(function(value) {
            expect(parseRelativeTime(value)).toBe(tests[value]);
        });
    });
    it('return getTranscriptUrl', function() {
        var transcriptsArray = [
            {
                lang: 'en',
                url: 'http://test.en/'
            },
            {
                lang: 'ru',
                url: 'http://test.ru/'
            }
        ];
        expect(getTranscriptUrl(transcriptsArray, 'en')).toBe('http://test.en/');
        expect(getTranscriptUrl(transcriptsArray, 'ru')).toBe('http://test.ru/');
        expect(getTranscriptUrl(transcriptsArray)).toBe('');
    });

    it('return validateTranscripts', function() {
        var $testTranscriptsBlock;
        var e = {
            preventDefault: function() {}
        };
        $('body').append('<ol id="test-transcript-block" class="list-settings language-transcript-selector">' +
            '<li class="list-settings-item">' +
            '<div class="list-settings-buttons">' +
            '<a href="#" class="download-transcript download-setting is-hidden">Download</a>' +
            '</div>' +
            '</li>' +
            '</ol>');

        $testTranscriptsBlock = $('#test-transcript-block');
        expect(validateTranscripts(e, $testTranscriptsBlock)).toBeFalsy();
        $testTranscriptsBlock.first('li').find('.download-setting').removeClass('is-hidden');
        expect(validateTranscripts(e, $testTranscriptsBlock)).toBeTruthy();
    });
});

describe('Function "pushTranscript"', function() {
    'use strict';
    var newTranscriptAdded;
    var transcriptsValue;
    var testData = {
        lang: 'en',
        label: 'English',
        url: 'testUrl',
        source: 'manual',
        oldLang: ''
    };
    var oldData = {
        lang: 'en',
        label: 'English',
        url: 'otherTestUrl',
        source: 'default'
    };

    afterEach(function() {
        newTranscriptAdded = null;
        transcriptsValue = null;
    });


    it('called with empty "transcriptsValue"', function() {
        transcriptsValue = [];
        // eslint-disable-next-line no-undef
        newTranscriptAdded = pushTranscript(
            testData.lang,
            testData.label,
            testData.url,
            testData.source,
            testData.oldLang,
            transcriptsValue
        );
        expect(newTranscriptAdded).toBeTruthy();
        expect(transcriptsValue).toEqual([{
            lang: testData.lang,
            url: testData.url,
            label: testData.label,
            source: testData.source
        }]);
    });

    it('called with the "transcriptsValue" that already contains pushed language', function() {
        transcriptsValue = [oldData];
        // eslint-disable-next-line no-undef
        newTranscriptAdded = pushTranscript(
            testData.lang,
            testData.label,
            testData.url,
            testData.source,
            testData.oldLang,
            transcriptsValue
        );
        expect(newTranscriptAdded).toBeFalsy();
        expect(transcriptsValue).toEqual([{
            lang: testData.lang,
            url: testData.url,
            label: testData.label,
            source: testData.source
        }]);
    });
});
