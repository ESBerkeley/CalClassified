$(".bookmark-activate").click( function() {
    $("#active-bookmark").toggle()
    $("#not-active-bookmark").toggle()
  
  data = {}
  data['post_pk'] = post_pk
  data['csrfmiddlewaretoken'] = csrf_token
  
  $.ajax({
    type: "POST",
    url: "/bookmark/",
    data: data,
    success: function(){
    }
  })
})

$(".close-refresh").click (function() {
    $("#modal-send").button('reset')
    $("#modal-message").val("")
})