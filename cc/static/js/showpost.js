$(document).ready( function() {


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

    //$("#post-icon").tooltip();
        $("#what-happens").popover({template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><div class="popover-content"><p></p></div></div></div>'});     //craziness that creates a popover with no title
        $(".delete-comment").tooltip();
        $(".delete-response").tooltip();

        $('.carousel').carousel();

        $(".fb-publish").click(function() {
            publishStream();
        })

        $("#comment-form").validate({
            rules: {
                body: {
                    required: true
                }
            },
            submitHandler: function() {
                $("#comment-btn").button('loading');
                $(form).ajaxSubmit();
            }
        });

        function streamPublish(name, description, caption, hrefLink, picLink){
            FB.ui(
            {
                method: 'feed',
                name: name,
                link: hrefLink,
                picture: picLink,
                caption: caption,
                description: description
            },

            function(response) {
              if (response && response.post_id) {
                $("#new-post-alert").alert('close');
                $("#new-post-success").fadeIn();
              } else {
                //alert('Post was not published.');
              }
            }

            );
        }
        function publishStream(){
            var post_body = $("#post-body").html();
            var fb_title = $("#post-title").html() + " - ${{ post.price }}"; //instatiate as a variable to be safe in case text contains quotes

            streamPublish(fb_title,
            post_body,
            "Buy and sell with your friends!",
            'http://buynear.me{{ post.get_absolute_url }}',
            "http://buynear.me{{ post.get_first_image_url }}");
        }

          $(".close-refresh").click (function() {
              location.reload();
          });


          $(".delete-post").click(function(){
            if (confirm("Are you sure you want to delete this post?")) {
                window.location.href="/delete/{{ post.pk }}"
            }
          });

          $(".delete-comment").click(function(){
            if (confirm("Are you sure you want to delete your comment?")) {
                var comment_id = $(this).attr('comment-id');
                var data = {};
                data['csrfmiddlewaretoken'] = csrfmiddlewaretoken;
                $.ajax({
                    type: "POST",
                    url: "/ajax/delete_comment/"+comment_id+"/",
                    data: data,

                    error: function(){
                        alert("Oops! Something went wrong. Please contact support.")
                    },
                    success: function(){
                        location.reload();
                    }

                })
            }
          });

          $(".delete-response").click(function(){
            if (confirm("Are you sure you want to delete your response?")) {
                var comment_id = $(this).attr('comment-id');
                var data = {};
                data['csrfmiddlewaretoken'] = csrfmiddlewaretoken;
                $.ajax({
                    type: "POST",
                    url: "/ajax/delete_response/"+comment_id+"/",
                    data: data,

                    error: function(){
                        alert("Oops! Something went wrong. Please contact support.")
                    },
                    success: function(){
                        location.reload();
                    }

                })
            }
          });

          $("#flag-post").click(function(){
            if (confirm("Are you sure you want to flag this post?")) {
                window.location.href="/flag/{{ post.pk }}"
            }
          });

          $('#buynow-modal').on('shown', function () {
              $('#modal-message').focus();
          });

        $('#modal-response').on('shown', function () {
            $('#id_seller_response').focus();
        });

        $.cookie('onpost',null);
        $.cookie('onpost','t', { expires: 1, path: '/' } );

});