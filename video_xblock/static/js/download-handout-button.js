$(document).on('click', '.download-handout', function(e){
  e.preventDefault();
  window.location = $('.handout_path_file').text();
});
