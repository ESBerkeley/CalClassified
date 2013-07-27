$('button#first-upload').click(function(){
    $(this).button('loading');
    var formData = new FormData($('#temp-photo-form')[0]);
    $.ajax({
        url: '/ajax/upload_temp_photo/',  //server script to process data
        type: 'POST',
        //Ajax events
        success: function(temp_image_url) {
            $(".crop-inject").html("<img id='crop-photo' src='"+temp_image_url+"'/>");
//            $(".preview-wrapper").html("<img id='preview-photo' src='"+imgUrl+"'/>");
            $('img#crop-photo').Jcrop({
                aspectRatio: 1,
                setSelect: [0,0,200,200],
                minSize: [200, 200],
                boxWidth: 600,
                boxHeight: 400,
                onSelect: updateForm,
                onChange: updateForm
//                onSelect: showPreview,
//                onChange: showPreview
            });

            $("#change-photo-modal").modal('hide');
            $("#crop-photo-modal").modal('show');
            $('button#first-upload').button('reset');
        },
        error: function(data) {
            $('button#first-upload').button('reset');
            alert("Oops, something went wrong. Please try again!");
        },
        // Form data
        data: formData,
        //Options to tell JQuery not to process data or worry about content-type
        cache: false,
        contentType: false,
        processData: false
    });
});

$("button#upload").click(function(){
    $(this).button('loading');
    var formData = new FormData($('#coords-form')[0]);
    $.ajax({
        url: '/ajax/upload_profile_photo/',  //server script to process data
        type: 'POST',
        // Form data
        data: formData,
        //Options to tell JQuery not to process data or worry about content-type
        cache: false,
        contentType: false,
        processData: false,
        //Ajax events
        success: function(data) {
            location.reload();
        },
        error: function(data) {
            $('button#upload').button('reset');
            alert("Oops, something went wrong. Please try again!");
        }
    });
})

function updateForm(coords){
    $('input[name="x1"]').val(Math.round(coords.x));
    $('input[name="y1"]').val(Math.round(coords.y));
    $('input[name="x2"]').val(Math.round(coords.x2));
    $('input[name="y2"]').val(Math.round(coords.y2));
    $('input[name="width"]').val(Math.round(coords.w));
};

//DOESNT WORK
function showPreview(coords)
{
	var rx = 100 / coords.w;
	var ry = 100 / coords.h;

	$('img#preview-photo').css({
		width: Math.round(rx * 300) + 'px',
		height: Math.round(ry * 400) + 'px',
		marginLeft: '-' + Math.round(rx * coords.x) + 'px',
		marginTop: '-' + Math.round(ry * coords.y) + 'px'
	});
};

$("#delete-photo").click(function(){
    $.ajax({
        url: '/ajax/delete_profile_photo/',  //server script to process data
        data: {"csrfmiddlewaretoken": csrfToken}, //defined on template
        type: 'POST',
        success: function(data) {
            location.reload();
        }
    })
})