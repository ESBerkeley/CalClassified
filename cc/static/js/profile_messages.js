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


$(".close-refresh").click (function() {
    location.reload();
})