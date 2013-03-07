/*
$(".verify-delete").click(function(){
    $(this).button('loading');
    var thread_pk = $(this).val()
    data= {};
    //data['sender_pk'] = sender_pk; user data can be accessed in the request
    data['csrfmiddlewaretoken'] = csrf_token;
    data['thread_pk'] = thread_pk;
    $.ajax({
        type: "POST",
        url: "/ajax_delete_thread/",
        data: data,
        success: function(data){
            $("#delete-modal-"+thread_pk).modal('hide');
            $("#success-modal").modal('show');
        }
    })
})
*/

$(".close-refresh").click (function() {
    location.reload();
});

 
//$(document).ready( function() {

  $(".verify-delete").click(function(){
    $(this).button('loading');
    var post_id = $(this).val();
    data= {};
    data['csrfmiddlewaretoken'] = csrf_token;
    data['post_id'] = post_id;
    $.ajax({
      type: "POST",
      url: "/ajax_delete_post/",
      data: data,
      success: function(data){
        $("#delete-modal-"+post_id).modal('hide');
        $("#delete-success-modal").modal('show');
      }
    });
  });

//};
