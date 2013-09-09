/*function restore(){
    window.setTimeout(function(){
   
        var mybox = document.getElementById("myBox");
        var sessionField = document.getElementById("sfield");
        var sessionField_scroll = document.getElementById("sfield_scroll");
        var xxxx = eval('(' + sessionField_scroll.value + ')');
        
        if(xxxx === 3){
          
            clear_restore();
            runloadBox();
            in_restore = 0;
        }
        
        else {
       
        
            mybox.innerHTML = sessionField.value;
        
            $(window).scrollTop(xxxx["scroll"]); //works despite value being a string
        
            current_page = xxxx["current_page"];
            scats(xxxx["categories"]);
            scircs(xxxx["circles"]);
            filtering_by_friends = xxxx["filtering_by_friends"];
            if (filtering_by_friends){
                $('#friends_filter_button').button('toggle');
                }
            document.getElementById('searchbar').value = xxxx["query"];
            document.getElementById('min').value = xxxx["min_price"];
            document.getElementById('max').value = xxxx["max_price"];
            flags = xxxx["flags"];
            oflags = xxxx["oflags"];
            scraps = xxxx["scraps"];

            in_restore = 0;
        
        }
        
    }, 50); 
}


function clear_restore(){
    var sessionField = document.getElementById("sfield");
    var sessionField_scroll = document.getElementById("sfield_scroll");
    sessionField.value = "3";
    sessionField_scroll.value = "3";
}


function save_state(inputurl){
    var mybox = document.getElementById("myBox");
    var sessionField = document.getElementById("sfield");
    var sessionField_scroll = document.getElementById("sfield_scroll");
    sessionField.value = mybox.innerHTML;  //prepare the batcache
    sessionField_scroll.value = JSON.stringify({
        "scroll" : $(window).scrollTop(),
        "current_page" : current_page,
        "circles" : gcircs(),
        "categories" : gcats(),
        "filtering_by_friends" : filtering_by_friends,
        "query" : document.getElementById('searchbar').value,
        "min_price" : document.getElementById('min').value,
        "max_price" : document.getElementById('max').value,
        "scraps" : scraps,
        "flags" : flags,
        "oflags" : oflags
    });
   
}*/

function clear_notif(){
  var xhr_notif;
  if(window.XMLHttpRequest){xhr_notif = new XMLHttpRequest();}
  else{xhr_notif = new ActiveXObject("Microsoft.XMLHTTP");}
    xhr_notif.onreadystatechange=function(){
      if(xhr_notif.readyState == 4 && xhr_notif.status == 200){        
        get_friend_notifications();
        window.location.reload();
      }
    };
  var notif_url = "/clear_notifications";
  xhr_notif.open("GET",notif_url,true);
  xhr_notif.send();
}

function clear_notif_number(){
  var xhr_notif; 
  if(window.XMLHttpRequest){xhr_notif = new XMLHttpRequest();}
  else{xhr_notif = new ActiveXObject("Microsoft.XMLHTTP");}
    xhr_notif.onreadystatechange=function(){
      if(xhr_notif.readyState == 4 && xhr_notif.status == 200){
        get_friend_notifications();
      }
    };
  var notif_url = "/clear_notifications?justnum=true";
  xhr_notif.open("GET",notif_url,true);
  xhr_notif.send();
}


function get_friend_notifications(){  
    var xhr;
    if(window.XMLHttpRequest){ xhr = new XMLHttpRequest();}
    else{ xhr = new ActiveXObject("Microsoft.XMLHTTP");}
    
    xhr.onreadystatechange = function(){

      var element_in_question = document.getElementById("friend_notifications_dropdown");

      if ( element_in_question){
        if (xhr.readyState==4 && xhr.status == 200){
          var obj = eval ("(" + xhr.responseText + ")");

          var count = obj.length;
          var x = "";

          if(count){
            x += "<a href=\"#\" class=\"dropdown-toggle\" data-toggle=\"dropdown\" style=\"text-decoration:none\"> <span class=\"badge badge-info\">" + obj[0].extras.num_unread + "</span> <i class=\" icon-exclamation-sign\" style=\"text-decoration:none; color:black;\"></i></a>";
            x += "<ul class=\"dropdown-menu no-collapse pull-right\">";

            for(var k = 0; k < count; k++){

              if(obj[k].fields.type == 0){
                x += "<li><a href=\"/" + obj[k].fields.post_from + "\"><strong>" + obj[k].extras.username + "</strong> posted " + obj[k].extras.title + "</a></li>";
              }

              else if(obj[k].fields.type == 1){
                x += "<li><a href=\"/" + obj[k].fields.post_from + "#comments_section\"><strong>" + obj[k].extras.second_username + "</strong> commented on " + obj[k].extras.title + "</a></li>";
              }

              else if(obj[k].fields.type == 2){
                x += "<li><a href=\"/" + obj[k].fields.post_from + "#comments_section\"><strong>" + obj[k].extras.username + "</strong> replied to your comment on " + obj[k].extras.title + "</a></li>";
              }

              else if(obj[k].fields.type == 3){
                x += "<li><a href=\"/accounts/profile/messages/" + obj[k].fields.thread_id + "\"><strong>" + obj[k].extras.second_username + "</strong> has purchased your item: " + obj[k].extras.title + "</a></li>";
              }

              else if(obj[k].fields.type == 4){
                x += "<li><a href=\"/review_item/" + obj[k].fields.post_from + "\"><strong>" + obj[k].extras.username + "</strong> has marked the sale of " + obj[k].extras.title + " as complete." + "</a></li>";
              }

              else if(obj[k].fields.type == 5){
                x += "<li><a href=\"/" + obj[k].fields.post_from + "\"><strong>" + obj[k].extras.username + "</strong> has cancelled the sale of " + obj[k].extras.title + ".</a></li>";
              }

              else if(obj[k].fields.type == 6){  //buyer "bob" has messaged you about your post "dogfood"
                x += "<li><a href=\"/accounts/profile/messages/" + obj[k].fields.thread_id + "\">Buyer <strong>" + obj[k].extras.second_username + "</strong> has sent you a message about your post  <strong>" + obj[k].extras.title + "</strong>.</a></li>";
              }
         
              else if(obj[k].fields.type == 7){   //seller "bob" has messaged you about their post "dogfood"
                x += "<li><a href=\"/accounts/profile/messages/" + obj[k].fields.thread_id + "\">Seller <strong>" + obj[k].extras.username + "</strong> has sent you a message about their post  <strong>" + obj[k].extras.title + "</strong>.</a></li>";
              }

              else if(obj[k].fields.type == 8){   //seller "bob" has confirmed your purchase
                x += "<li><a href=\"/accounts/profile/messages/" + obj[k].fields.thread_id + "\">Seller <strong>" + obj[k].extras.username + "</strong> has confirmed your purchase of <strong>" + obj[k].extras.title + "</strong>.</a></li>";
              }

              else if(obj[k].fields.type == 9){   //buyer "bob" has declined to purchase item
                x += "<li><a href=\"/accounts/profile/messages/" + obj[k].fields.thread_id + "\">Buyer <strong>" + obj[k].extras.username + "</strong> is no longer purchasing <strong>" + obj[k].extras.title + "</strong>.</a></li>";
              }

              else if(obj[k].fields.type == 10){   //buyer "bob" has reviewed your item
                x += "<li><a href='/user/" + obj[k].fields.going_to + "/reviews'>Buyer <strong>" + obj[k].extras.second_username + "</strong> has reviewed your item <strong>" + obj[k].extras.title + "</strong>.</a></li>";
              }

              else if(obj[k].fields.type == 11){   //seller "bob" has declined purchase of item from buyer
                x += "<li><a href=\"/accounts/profile/messages/" + obj[k].fields.thread_id + "\">Seller <strong>" + obj[k].extras.second_username + "</strong> declined the sale of <strong>" + obj[k].extras.title + "</strong>.</a></li>";
              }
           } 

         x+="<li> <a href = \"/accounts/profile/\">See All</a></li>";
         x += "</ul>";
         }
          else {
            x += "<a href=\"#\" class=\"dropdown-toggle\" data-toggle=\"dropdown\" style=\"text-decoration:none\"> <span class=\"badge badge-info\">"+count+"</span> <i class=\" icon-exclamation-sign\" style=\"text-decoration:none; color:black;\"></i></a>";
          }
          element_in_question.innerHTML = x;
        }
      }       
    }
    var url="/get_friend_notifications/?cap=yup";
    xhr.open("GET",url,true);
    xhr.send();
}

function date_change(oldDate) {     //returns a date with year-month-day format into "May 1, 2027"
  var newDate = "";
  var splitString = oldDate.split("-");
  var month = splitString[1];
  var day = splitString[2];
  var year = splitString[0];

  if(month == 1)
    newDate += "January ";
  else if(month == 2)
    newDate += "February ";
  else if(month == 3)
    newDate += "March ";
  else if(month == 4)
    newDate += "April ";
  else if(month == 5)
    newDate += "May ";
  else if(month == 6)
    newDate += "June ";
  else if(month == 7)
    newDate += "July ";
  else if(month == 8)
    newDate += "August ";
  else if(month == 9)
    newDate += "September ";
  else if(month == 10)
    newDate += "October ";
  else if(month == 11)
    newDate += "November ";
  else
    newDate += "December ";

  newDate += day + ", " + year;
  return newDate
}

function smartDate(time){
	var date = moment(time);
	var now = moment();
	
	var mins = now.diff(date, "minutes");
	if(mins <= 1)
		return "1 min ago";
	if(mins < 60)
		return mins + " mins ago";
	var hours = now.diff(date, "hours");
	if(hours == 1)
		return "1 hour ago";
	if(hours < 24)
		return hours + " hours ago";
	var days = now.diff(date, "days");
	if(days == 1)
		return "1 day ago";
	if(days < 7)
		return days + " days ago";
	var weeks = now.diff(date, "weeks");
	if(weeks == 1)
		return "1 week ago";
	if(days < 28)
		return weeks + " weeks ago";
	var months = now.diff(date, "months");
	if(months == 1)
		return "1 month ago";
	else
		return months + " months ago";
}

function notification_table() {
  var xhr;
  if(window.XMLHttpRequest){ xhr = new XMLHttpRequest();}
  else{ xhr = new ActiveXObject("Microsoft.XMLHTTP");}
    
  xhr.onreadystatechange = function(){
    var element = document.getElementById("notification-table");
    if ( element){
      if (xhr.readyState==4 && xhr.status == 200){
        var obj = eval ("(" + xhr.responseText + ")");
        var count = obj.length;
        var html = "";
        var notif;

        if(count){
            for(var k = 0; k < count; k++){
              notif = notification_sentence(obj, k);
                /*HTML FORMAT
                  <tr>
                  <td><a href="{{ post.get_absolute_url }}"> {{ post.title }}</a></td>
                  <td>{{ post.time_created }}</td>
                  <td ><center><a class="icon-trash"></a></center></td>
                  </tr>*/
              html += "<tr>";
              html += "<td><a href=\" "+notif[1]+" \"> "+notif[0]+" </a></td>";
              html += "<td> "+ date_change(notif[2]) +" </td>";
              //html += "<td><center><a class=\"icon-trash\"></a></center></td>";
              html += "</tr>";
            }
            $('.notification-hide').show();     //reveals table "delete all" button if there are notifications
            
        }
        else {
            $(".notification-show").show()      //shows "No notifications" text
        }
        element.innerHTML = html;
      }
    }       
  }
  var url="/get_friend_notifications/";
  xhr.open("GET",url,true);
  xhr.send();
}

function notification_sentence(obj, k) {    //list of notifications, position in list. Returns the notification in tuple form.
  var notif = new Array();  //tuple containing a sentence string and the url. Includes html strong tagging.
  notif[0] = "";
  notif[1] = "";
  notif[2] = obj[k].fields.time_created.substring(0, 10);

  if(obj[k].fields.type == 0){ // friend posted _____
    notif[0] += obj[k].extras.username + " posted " + obj[k].extras.title;
    notif[1] += "/" +obj[k].fields.post_from;
  }
  else if(obj[k].fields.type == 1){ // user commented on ______
    notif[0] += "<strong>" + obj[k].extras.second_username + "</strong> commented on " + obj[k].extras.title;
    notif[1] += "/" +obj[k].fields.post_from + "#comments_section";
  }
  else if(obj[k].fields.type == 2){ // Seller replied to comment _____
    notif[0] += "<strong>" + obj[k].extras.username + "</strong> replied to your comment on " + obj[k].extras.title;
    notif[1] += "/" +obj[k].fields.post_from + "#comments_section";
  }
  else if(obj[k].fields.type == 3){ // Buyer has purchased item
    notif[0] += "<strong>" + obj[k].extras.second_username + "</strong> has purchased your item: " + obj[k].extras.title;
    notif[1] += "/accounts/profile/selling/";
  }
  else if(obj[k].fields.type == 4){ //Marked sale complete
    notif[0] += "<strong>" + obj[k].extras.username + "</strong> has marked the sale of " + obj[k].extras.title + " as complete.";
    notif[1] += "/" +obj[k].fields.post_from;
  }
  else if(obj[k].fields.type == 5){ // Cancelled sale of _____
    notif[0] += "<strong>" + obj[k].extras.username + "</strong> has cancelled the sale of " + obj[k].extras.title;
    notif[1] += "/" +obj[k].fields.post_from;
  }
  else if(obj[k].fields.type == 6){  //buyer "bob" has messaged you about your post "dogfood"
    notif[0] += "Buyer <strong>" + obj[k].extras.second_username + "</strong> has sent you a message about your post  <strong>" + obj[k].extras.title + "</strong>.";
    notif[1] += "/accounts/profile/messages/" + obj[k].fields.thread_id;
  }
  else {   //seller "bob" has messaged you about their post "dogfood"
    notif[0] += "Seller <strong>" + obj[k].extras.username + "</strong> has sent you a message about their post  <strong>" + obj[k].extras.title + "</strong>";
    notif[1] += "/accounts/profile/messages/" + obj[k].fields.thread_id;
  }
  return notif;
}

$("#modal-send").on("click", function(){
  $(this).button('loading');
  var message = $("#modal-message").val();
  data= {};
  data['recipient_pk'] = recipient_pk;
  data['message'] = message;
  data['csrfmiddlewaretoken'] = csrf_token;
  data['post_pk'] = post_pk;
  $.ajax({
    type: "POST",
    url: "/ajax_contact_seller/",
    data: data,
    success: function(data){
      $(".msg-modal").modal('hide');
      $("#success-modal").modal('show');
    }
  });
});

//Sets "isBoxActive" false for all pages except in "view item". Used to on runloadBox for "back".
$(window).on('beforeunload', function(){
  localStorage["isBoxActive"] = JSON.stringify(false);
});