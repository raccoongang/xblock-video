/**
 * Get python context and fill in js global variables with it
 */
window.videoPlayerId = '{{ video_player_id }}';
window.playerStateObj = JSON.parse('{{ player_state }}');
window.playerStartTime = JSON.parse('{{ start_time }}');
window.playerEndTime = JSON.parse('{{ end_time }}');
