/**
 * Created with PyCharm.
 * User: ericxiao
 * Date: 7/23/13
 * Time: 10:27 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready( function() {
    $("#id_expiration_date_month").addClass("chzn-select").prop("required", true).attr("data-placeholder", "Select Month...").attr("type", "value");
    $("#id_expiration_date_year").addClass("chzn-select").prop("required", true).attr("data-placeholder", "Select Year...").attr("type", "value");
    $(".chzn-select").chosen();

    $("#credit-card-form").validate({
      ignore: ":hidden:not(select)",
      rules: {
        credit_card_number: {
          required: true,
          number: true
        },
        CSV: {
          required: true,
          number:true
        },
        expiration_date_month: {
          required: true
        },
        expiration_date_year: {
          required: true
        }
      },
     errorPlacement: function(error, element) {
         if (element.hasClass('chzn-select')) {
             error.appendTo(element.parent());
         }
         else {
             error.insertAfter(element);
         }
     },
      submitHandler: function() {
        //$("#ajax-loader").show();
        //$("#submit").button('loading');
        creditCardSubmit();
        //$(form).ajaxSubmit();
      }
    });
    $('#id_expiration_date_month').change(function() {
        $("#id_expiration_date_month").valid();
    });
    $('#id_expiration_date_year').change(function() {
        $("#id_expiration_date_year").valid();
    });
});

function creditCardSubmit() {
    //e.preventDefault();

    //this.submit();

    var $form = $('#credit-card-form');
    var creditCardData = {
        card_number: $form.find('#id_credit_card_number').val(),
        expiration_month: $form.find('#id_expiration_date_month').val(),
        expiration_year: $form.find('#id_expiration_date_year').val(),
        security_code: $form.find('#id_CSV').val()
     };

    balanced.card.create(creditCardData, createCallback);

      data = {}
      data['credit_card_data'] = creditCardData
      data['csrfmiddlewaretoken'] = csrf_token

      /*$.ajax({
        type: "POST",
        url: "/bookmark/",
        data: data,
        success: function(){
        }
      })*/
};

function createCallback(response) {
   switch (response.status) {
     case 201:
         // WOO HOO! MONEY!
         // response.data.uri == URI of the bank account resource you
         // can store this card URI in your database
         console.log(response.data);
         var $form = $("#credit-card-form");
         // the uri is an opaque token referencing the tokenized card
         var cardTokenURI = response.data['uri'];
         // append the token as a hidden field to submit to the server
         $('<input>').attr({
            type: 'hidden',
            value: cardTokenURI,
            name: 'balancedCreditCardURI'
         }).appendTo($form);
         break;
     case 400:
         // missing field - check response.error for details
         console.log(response.error);
         $(".credit-card-verification").append(responseErrorToString(response.error));
         break;
     case 402:
         // we couldn't authorize the buyer's credit card
         // check response.error for details
         console.log(response.error);
         console.log("yes");
         $(".credit-card-verification").append(responseErrorToString(response.error));
         break;
     case 404:
         // your marketplace URI is incorrect
         console.log(response.error);
         break;
     case 500:
         // Balanced did something bad, please retry the request
         break;
   }
}

function responseErrorToString(error) {
    error_string = ''
    if (error.hasOwnProperty('category_code') && error['category_code']=='card-declined') {
        error_string += 'Error, your card has been declined.<br>';
    }
    if (error.hasOwnProperty('card_number')) {
        error_string += error['card_number']+'<br>';
    }
    if (error.hasOwnProperty('security_code')) {
        error_string += error['security_code']+'<br>';
    }
    return error_string;
}