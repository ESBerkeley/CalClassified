function search(pageNum){
    $.mobile.loading( 'show', {
        text: 'foo',
        //textVisible: true,
        theme: 'a',
        html: ""
    });
    var send_data = {};
    send_data['searchText'] = $("#search-basic").val();
    send_data['min_price'] = $("#min-price").val();
    send_data['max_price'] = $("#max-price").val();
    send_data['pageNum'] = pageNum;
    send_data['checked_categories'] = $('input[name=categories]:checked').map(function() {
        return $(this).val();
    }).get(); // array of checked category ids

    $.ajax({
               type: "GET",
               url: "/ajax/browse/",
               data: send_data,
               success: function(data){
                   var data = eval(data);
                   var browseHtml = ""
                   for (index in data) {
                       var entry = data[index];
                       browseHtml += "<li><a href='/"+entry['pk']+"' rel='external'>"
                       browseHtml += "<img src='" + entry['fields']['cached_thumb'] + "' style='max-height: 100%;'/>"
                       browseHtml += "<h3>" + entry['fields']['title'] + "</h3>"
                       browseHtml += "<p>$" + entry['fields']['price'] + "</p></a></li>"
                   }


                   if(data.length == 25) {
                       $("#load-more-div").show();
                   } else {
                       $("#load-more-div").hide();
                   }

                   $.mobile.loading( 'hide', {
                       text: 'foo',
                       //textVisible: true,
                       theme: 'a',
                       html: ""
                   });
                   
                   $("#cancel-button").click();

                   if (pageNum == 1) {
                       $("#browse-list").html(browseHtml).listview("refresh");
                   } else {
                       $("#browse-list").append(browseHtml).listview("refresh");
                   }
               }
           })

}


$("#message-form").submit(function(event){
    event.preventDefault();
    $('[type="submit"]').button('disable');

    $.mobile.loading( 'show', {
        text: 'Sending Message...',
        textVisible: true,
        theme: 'a',
        html: ""
    });

    data = {}
    data['recipient_pk'] = recipient_pk
    data['post_pk'] = post_pk
    data['message'] = $("#message-text").val();
    data['csrfmiddlewaretoken'] = csrfmiddlewaretoken;

    $.ajax({
        type: "POST",
        url: "/ajax/send_message/",
        data: data,
        success: function(data){

        },
        error: function(){
            alert("Oops! Something went wrong. Please contact support.")

        },
        complete: function(){
            $.mobile.loading( 'hide', {
                text: 'foo',
                //textVisible: true,
                theme: 'a',
                html: ""
            });
                if (view_thread == false){
                    alert("Message Sent!");
                }
                refreshPage();

        }

    })

    return false;

})

$("#modal-send").click(function(){

    if ($("#message-text").val() == "") {
        $("#no-modal-msg").show();
        return;
    }

    $('#modal-send').button('disable');

    $.mobile.loading( 'show', {
        text: 'Sending Message...',
        textVisible: true,
        theme: 'a',
        html: ""
    });

    data = {}
    data['recipient_pk'] = recipient_pk
    data['post_pk'] = post_pk
    data['message'] = $("#message-text").val();
    data['csrfmiddlewaretoken'] = csrfmiddlewaretoken;

    $.ajax({
        type: "POST",
        url: "/ajax/send_message/",
        data: data,

        error: function(){
            $.mobile.loading( 'hide', {
                text: 'foo',
                //textVisible: true,
                theme: 'a',
                html: ""
            });
            alert("Oops! Something went wrong. Please contact support.")

        },
        success: function(){
            $.mobile.loading( 'hide', {
                text: 'foo',
                //textVisible: true,
                theme: 'a',
                html: ""
            });
            if (view_thread == false){
                alert("Message Sent!");
            }
            //refreshPage();
            location.reload(true);
        }

    })

    return false;

})

function refreshPage() {
    $.mobile.changePage(
        window.location.href,
        {
            allowSamePageTransition : true,
            transition              : 'none',
            showLoadMsg             : false,
            reloadPage              : true
        }
    );
}

$("#comment-send").click(function(){
    send_comment();
})

function send_comment() {
    if ($('#comment-text').val()   == "") {
        $("#no-comment-msg").show();
        return;
    }
    var commentText = $('#comment-txt').val()  
    $("#comment-send").button('disable');

    $.mobile.loading( 'show', {
        text: 'Sending...',
        textVisible: true,
        theme: 'a',
        html: ""
    });

    data = {}
    data['post_pk'] = post_pk;
    data['commentText'] = commentText;
    data['csrfmiddlewaretoken'] = csrfmiddlewaretoken;

    $.ajax({
        type: "POST",
        url: "/ajax/send_comment/",
        data: data,
        cache: false,

        error: function(){
            $.mobile.loading( 'hide', {
                text: 'foo',
                //textVisible: true,
                theme: 'a',
                html: ""
            });
            alert("Oops! Something went wrong. Please contact support.")

        },
        success: function(){
            $.mobile.loading( 'hide', {
                text: 'foo',
                //textVisible: true,
                theme: 'a',
                html: ""
            });

            //refreshPage();
            location.reload(true);
        }

    })

    return false;
}

$(".reply-comment-button").click(function(){
    
    var commentID = $(this).attr('id');
    var replyText = $('#reply-comment-'+commentID).val()
    
    
    if (replyText == "") {
        alert("Please write a message")
        return;
    }
    
    $(this).button('disable');

    $.mobile.loading( 'show', {
        text: 'Replying...',
        textVisible: true,
        theme: 'a',
        html: ""
    });

    data = {}
    data['commentID'] = commentID;
    data['replyText'] = replyText;
    data['csrfmiddlewaretoken'] = csrfmiddlewaretoken;

    $.ajax({
        type: "POST",
        url: "/ajax/reply_comment/",
        data: data,

        error: function(){
            $.mobile.loading( 'hide', {
                text: 'foo',
                //textVisible: true,
                theme: 'a',
                html: ""
            });
            alert("Oops! Something went wrong. Please contact support.")

        },
        success: function(){
            $.mobile.loading( 'hide', {
                text: 'foo',
                //textVisible: true,
                theme: 'a',
                html: ""
            });

            //refreshPage();
            location.reload(true);
        }

    })

    return false;
    
})

$("#delete-notif-btn").click(function(){
    $(this).button('disable');

    $.mobile.loading( 'show', {
        text: 'Deleting...',
        textVisible: true,
        theme: 'a',
        html: ""
    });

    data = {}
    data['csrfmiddlewaretoken'] = csrfmiddlewaretoken;

    $.ajax({
        type: "POST",
        url: "/ajax/delete_notifications/",
        data: data,

        error: function(){
            $.mobile.loading( 'hide', {
                text: 'foo',
                //textVisible: true,
                theme: 'a',
                html: ""
            });
            alert("Oops! Something went wrong. Please contact support.")

        },
        success: function(){
            $.mobile.loading( 'hide', {
                text: 'foo',
                //textVisible: true,
                theme: 'a',
                html: ""
            });

            //refreshPage();
            location.reload(true);
        }

    })

    return false;
})


