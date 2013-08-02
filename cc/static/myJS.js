function restore(){
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
   
}

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
            x += "<a href=\"#\" class=\"dropdown-toggle\" data-toggle=\"dropdown\" style=\"text-decoration:none\"> <span class=\"badge badge-warning\">" + obj[0].extras.num_unread + "</span> <i class=\" icon-exclamation-sign\" style=\"text-decoration:none; color:black;\"></i></a>";
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
                x += "<li><a href=\"/accounts/profile/selling/\"><strong>" + obj[k].extras.second_username + "</strong> has purchased your item: " + obj[k].extras.title + "</a></li>";
              }

              else if(obj[k].fields.type == 4){
                x += "<li><a href=\"/" + obj[k].fields.post_from + "\"><strong>" + obj[k].extras.username + "</strong> has marked the sale of " + obj[k].extras.title + " as complete." + "</a></li>";
              }

              else if(obj[k].fields.type == 5){
                x += "<li><a href=\"/" + obj[k].fields.post_from + "\"><strong>" + obj[k].extras.username + "</strong> has cancelled the sale of " + obj[k].extras.title + ".</a></li>";
              }

              else if(obj[k].fields.type == 6){  //buyer "bob" has messaged you about your post "dogfood"
                x += "<li><a href=\"/accounts/profile/messages/" + obj[k].fields.thread_id + "\">Buyer <strong>" + obj[k].extras.second_username + "</strong> has sent you a message about your post  <strong>" + obj[k].extras.title + "</strong>.</a></li>";
              }
         
              else{   //seller "bob" has messaged you about their post "dogfood"
                x += "<li><a href=\"/accounts/profile/messages/" + obj[k].fields.thread_id + "\">Seller <strong>" + obj[k].extras.username + "</strong> has sent you a message about their post  <strong>" + obj[k].extras.title + "</strong>.</a></li>";
              }
           } 

         x+="<li> <a href = \"/accounts/profile/\">See All</a></li>";
         x += "</ul>";
         }
          else {
            x += "<a href=\"#\" class=\"dropdown-toggle\" data-toggle=\"dropdown\" style=\"text-decoration:none\"> <span class=\"badge badge-success\">"+count+"</span> <i class=\" icon-exclamation-sign\" style=\"text-decoration:none; color:black;\"></i></a>";
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

  if(obj[k].fields.type == 0){
    notif[0] += obj[k].extras.username + " posted " + obj[k].extras.title;
    notif[1] += "/" +obj[k].fields.post_from;
  }
  else if(obj[k].fields.type == 1){
    notif[0] += "<strong>" + obj[k].extras.second_username + "</strong> commented on " + obj[k].extras.title;
    notif[1] += "/" +obj[k].fields.post_from + "#comments_section";
  }
  else if(obj[k].fields.type == 2){
    notif[0] += "<strong>" + obj[k].extras.username + "</strong> replied to your comment on " + obj[k].extras.title;
    notif[1] += "/" +obj[k].fields.post_from + "#comments_section";
  }
  else if(obj[k].fields.type == 3){
    notif[0] += "<strong>" + obj[k].extras.second_username + "</strong> has purchased your item: " + obj[k].extras.title;
    notif[1] += "/accounts/profile/selling/";
  }
  else if(obj[k].fields.type == 4){
    notif[0] += "<strong>" + obj[k].extras.username + "</strong> has marked the sale of " + obj[k].extras.title + " as complete.";
    notif[1] += "/" +obj[k].fields.post_from;
  }
  else if(obj[k].fields.type == 5){
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


function search(){
    var q = document.getElementById('searchbar').value;
    url = "/browse/?q="+q
    window.location = url;
}

function searchbarCancel(pg) {   //cancel for the search bar
    document.getElementById('searchbar').value = '';
    runloadBox(pg);
}

function priceboxCancel(pg) {   //cancel for the price box
    document.getElementById('max').value = '';
    document.getElementById('min').value = '';
    runloadBox(pg);
}

//only toggles categories
function toggler(control) {   //hides everything, shows specific icon
    $("li.side-item.category").removeClass("active");
    $("#"+control).addClass("active");
}

//Toggles searchbar text
function searchToggle(name) {
    var id = document.getElementById('searchbar');
    id.placeholder = 'Search in ' + name;
}

function runloadBox(pg) {
    if(typeof(pg) == "undefined"){pg=0;}
    var cat_status = getCats();
    var cir_status = getCircs(); 
    var cs = gcats();
    var ccs = gcircs();
    var query = document.getElementById('searchbar').value;
    var min_price = document.getElementById('min').value;
    var max_price = document.getElementById('max').value;
    var order = getOrder();

    flags = "_" + query + min_price + max_price + cs + ccs + filtering_by_friends;

    if(oflags != flags) {
        $(window).scrollTop(0);
        oflags = flags; 
        $("#myBox").empty(); //accidentally the posts
        scraps=[];
        current_page=0;
        loadBox(query,min_price,max_price,cat_status,cir_status,filtering_by_friends,0, order);
    } else {
        loadBox(query,min_price,max_price,cat_status,cir_status,filtering_by_friends,pg, order);
    }
}

function loadBox(query,min_price,max_price,cat_status,cir_status,filtering_by_friends,page, order){
    //load pacman
    $("#pac-ajax").show();

    //going first makes sure icons are hidden so the page doesnt look weird during the load
    if(query) {      //hides and shows cancel button in search bar
      $("#search-cancel-nav").show();
      $("#search-go-nav").hide();
    } else {
      $("#search-cancel-nav").hide();
      $("#search-go-nav").show();
    }
    if(max_price || min_price) {      //hides and shows price icons
      $("#price-go").hide();
      $("#price-cancel").show();
    } else {
      $("#price-go").show();
      $("#price-cancel").hide();
    }
    

  var url="/ajax_box/";
  var first = true;

  if(!(typeof query === 'undefined')){
    if (first) {
    url = url + "?q=" + query;
    first = false;
    } else {
    url = url + "&q=" + query;
    }
  }

  if(!(typeof max_price === 'undefined')){
    if (first) {
    url = url + "?max_price=" + max_price;
    first = false;
    } else {
    url = url + "&max_price=" + max_price;
    }
  }

  if(!(typeof min_price === 'undefined')){
    if (first) {
    url = url + "?min_price=" + min_price;
    first = false;
    } else {
    url = url + "&min_price=" + min_price;
    }
  }
  
  for (key in cat_status) {
    if (cat_status[key]==true) {
      cat_pk = cat2num(key)
      if (first) {
        url = url + "?category="+cat_pk;
        first = false;
      } else {
        url = url + "&category="+cat_pk;
     }
    }
  }
  
  for (key in cir_status) {
    if (cir_status[key]==true) {
      //cir_pk = cir2num(key)
      cir_pk = key
      if (first) {
        url = url + "?" + "circle=" + cir_pk;
        first = false;
      } else {
        url = url + "&" + "circle=" + cir_pk;
     }
    }
  }
  
  if(filtering_by_friends){
    if(first){
        first=false;
        url=url+"?"+"fbf=1";
    }else{
        url=url+"&fbf=1";
    }
  }

  if(first){
    first=false;
    url += "?p=" + page;
  }

  else{
    url += "&p=" + page;
  }

  if(first) {
    first = false;
    url += "?order=" + order;
  } else {
    url += "&order=" + order;
  }

    $.ajax({
        type: "GET",
        url: url,
        dataType: "json",
        success: function(data){
            console.log(data)
            if(data.length !== 0) {
                var $container = $('#box');
                // initialize
                $container.masonry({
                    columnWidth: 200,
                    itemSelector: '.item'
                });

                var html = "";
                for(i = 0; i < data.length; i++) {
                    html += "<div class='item'>"+data[i].fields.title+data[i].fields.category+"</div>";
                    
                    //console.log(data[i])
                }
                //$("#box").html(html);
                var $html = $(html);
                $container.append($html).masonry('appended', $html);
                
                //Calvin's random unimportant sidebar crap
                var filters = "";          
                if(query) {
                filters = "<li>" + "Search: " + query + "</li>";
                }
                if(min_price || max_price) {
                filters = filters + "<li>" + "Price: $" + min_price + " to $" + max_price + "<li>";
                }
                
                if((typeof filters === 'undefined') || (filters === "")) {
                filters = "<li> None </li>";
                }
            }
            
            //go away pacman
            $("#pac-ajax").hide();
        }
    });
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

