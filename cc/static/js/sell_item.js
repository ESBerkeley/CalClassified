$(document).ready(function(){
    /*$("#image-upload-group").hide();
    $("#facebook-share-group").hide();
    $("#submit").hide();*/
    $("#sellForm").validate({
      ignore: ":hidden:not(select)",
      rules: {
        title: {
          required: true,
          maxlength: 74
        },
        body: {
          required: true,
          maxlength: 2000
        },
        price: {
          required: true,
          number: true,
          min: 0
        },
        category: {
          required: true
        }
      },
      submitHandler: function() {
        $("#ajax-loader").show();
        $("#submit").button('loading');
        $(form).ajaxSubmit();
      }
    });


    // require price only has 2 decimals
    (function($) {
        $.fn.currencyFormat = function() {
            this.each( function( i ) {
                $(this).change( function( e ){
                    if( isNaN( parseFloat( this.value ) ) ) return;
                    if (this.value.split(".").length >1) {
                      this.value = parseFloat(this.value).toFixed(2);
                    }
                });
            });
            return this; //for chaining
        }
    })( jQuery );

    $( function() {
        $('#id_price').currencyFormat();
    });
    // end price validation

    // add * to required fields
    /**
    var required = ['title','body','price','category','circles'];
    for (index in required) {
      try {
        document.getElementById(required[index]).innerHTML += '*';
        document.getElementById(required[index]).style.fontWeight = 'bold';
      } catch (err) {}
    }
    **/

});

$(".upload-more").click(function(){
    var new_upload_html = '<div class="fileupload fileupload-new" data-provides="fileupload">'+
          '<div class="fileupload-new thumbnail" style="width: 50px; height: 50px; margin-right: 5px;">'+
          '<img src="http://www.placehold.it/50x50/EFEFEF/AAAAAA" />'+
          '</div>'+
          '<div class="fileupload-preview fileupload-exists thumbnail" style="width: 50px; height: 50px;"></div>'+
          '<span class="btn btn-file">'+
          '<span class="fileupload-new">Select image</span>'+
          '<span class="fileupload-exists">Change</span>'+
          '<input type="file" name="images" />'+
          '</span>'+
          '<a href="#" class="btn fileupload-exists" data-dismiss="fileupload">Remove</a>'+
          '</div>'
    $("#upload-images").append(new_upload_html)
  uploadImageCounter += 1;
  if (uploadImageCounter == 3){
      $(this).remove();
      var max_images = '<br>Maximum 3 images'
      $(".after-image").append(max_images)
  }
});

/*$("#next-form").click(function() {
    if($("#sellForm").valid()) {
        $("#image-upload-group").show();
        $("#facebook-share-group").show();
        $("#submit").show();
        $("#next-form").hide();
    }
});*/