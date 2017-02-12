import {dispatch} from './studio-edit-utils';

/**
 * Submit video for a retranscode to Brightcove Video Cloud API.
 */
export function submitBCReTranscode(profile, runtime, element) {
    $.when(
        dispatch('POST', 'submit_retranscode_' + profile, runtime, element)
    ).then((response) => {
        $('#brightcove-retranscode-status').html(
            'Your retranscode request was successfully submitted to Brightcove VideoCloud. ' +
            'It takes few minutes to process it. Job id ' + response.id);
    });
}

/**
 * Get tech info for a video and display it to teacher.
 *
 * @param  {Object} runtime
 * @param  {Object} element
 * @return {XMLHttpRequest}
 */
export function bcLoadVideoTechInfo(runtime, element) {
    $.when(
        dispatch('POST', 'get_video_tech_info', runtime, element)
    ).then((response) => {
        $('#bc-tech-info-renditions').html(response.renditions_count);
        $('#bc-tech-info-autoquality').html(response.auto_quality);
        $('#bc-tech-info-encryption').html(response.encryption);
    });
}

/**
 * Get ReTranscode status for a video
 *
 * @param  {Object} runtime
 * @param  {Object} element
 * @return {XMLHttpRequest}
 */
export function getReTranscodeStatus(runtime, element) {
    $.when(
        dispatch('POST', 'retranscode-status', runtime, element)
    ).then((data) => {
        $('#brightcove-retranscode-status').html(data);
    });
}
