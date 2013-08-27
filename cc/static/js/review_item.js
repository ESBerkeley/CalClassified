$(document).ready(function(){
    $("#star").raty({
        path: $.myproject.STATIC_URL + "raty-master/lib/img/",
        size: 24,
        starOff  : 'star-off-big.png',
        starOn   : 'star-on-big.png',
        click: function(score, evt) {
            $("input[name='score']").val(score);
        },
        score: function() {
            return $(this).attr('data-score');
        }
    });

    $("#review-form").validate({
        rules: {
            comment: {
              required: true
            },
            score: {
              required: true
            }
        },
        ignore: [], //allow hidden fields to be error handled
        submitHandler: function(form) {
            $("#ajax-loader").show();
            $("#submit").button('loading');
            form.submit()
        }
    });
})