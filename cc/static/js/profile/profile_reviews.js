$(document).ready(function(){
   $(".score").raty({
        path: $.myproject.STATIC_URL + "raty-master/lib/img/",
        readOnly : true,
        score: function() {
            return $(this).attr('data-score');
        }
    });
})
