$(document).ready(function(){
    $(".score").raty({
        path: $.myproject.STATIC_URL + "raty-master/lib/img/",
        readOnly : true,
        score: function() {
            return $(this).attr('data-score');
        }
    });

    $("#reviews-avg").raty({
        path: $.myproject.STATIC_URL + "raty-master/lib/img/",
        readOnly : true,
        size: 24,
        starOff  : 'star-off-big.png',
        starOn   : 'star-on-big.png',
        starHalf : 'star-half-big.png',
        score: function() {
            return $(this).attr('data-score');
        }
    });
})