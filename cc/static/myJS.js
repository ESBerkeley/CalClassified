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

/*****************************
 * Boxview
 * 
 * 
 *****************************/


// initialize masonry
var $container = $('#box');
var containerHtml = "";
var $containerHtml = $("");
$container.masonry({
  gutter: 5,
  itemSelector: '.box-item',
  transitionDuration: '0.6s'      //default 0.4
});
var savedHtml = "";

var query = "";
var minPrice = null;
var maxPrice = null;
var category = "Everything";
var categoryObject;
var page = 0;
var order = 'dateNew';

function search(){
  var q = document.getElementById('searchbar').value;
  url = "/browse/?q="+q
  window.location = url;
}

function searchbarCancel() {   //cancel for the search bar
  document.getElementById('searchbar').value = '';
  runloadBox(true, false);
}

function priceboxCancel() {   //cancel for the price box
  document.getElementById('max').value = null;
  document.getElementById('min').value = null;
}

function setPricebox(min, max) {
  document.getElementById('min').value = min;
  document.getElementById('max').value = max;
}

function createCategoryObject(category) {
  if(category === "Everything") {
    return {"Apparel": true, "Appliances": true, "Automotive": true, "Books": true, "Electronics": true, "Furniture": true, "Movies and Games": true, "Music": true, "Tickets": true, "Other": true}
  } else if(category === "Apparel") {
    return {"Apparel": true}
  } else if(category === "Appliances") {
    return {"Appliances": true}
  } else if(category === "Automotive") {
    return {"Automotive": true}
  } else if(category === "Books") {
    return {"Books": true}
  } else if(category === "Electronics") {
    return {"Electronics": true}
  } else if(category === "Furniture") {
    return {"Furniture": true}
  } else if(category === "Movies and Games") {
    return {"Movies and Games": true}
  } else if(category === "Music") {
    return {"Music": true}
  } else if(category === "Tickets") {
    return {"Tickets": true}
  } else {
    return {"Other": true}
  }
}

$(window).scroll(function(){
  if($(window).scrollTop() + $(window).height() >= $(document).height()) {
    page++;
    runloadBox(false, false);
  }
});

function getScroll() {
  return JSON.parse(localStorage["scroll"]);
}

function getPage() {
  return page;
}
  
function setPage(pageValue) {
  page = pageValue;
}
  
//sort order assigner. UI change AND server notifier
function setOrder(newOrder) {
  order = newOrder //assigned to make server filter properly
  $('.side-item.sort').removeClass("active");
  $('#'+newOrder+"-li").addClass("active");        //html ids for icons equivalent to the order values
}

function getCategory() {
  return category;
}

function setCategory(cat) {
  category = cat;
  categoryObject = createCategoryObject(cat);
  //Search Bar Text
  document.getElementById('searchbar').placeholder = "Search in " + cat;
  //Sidebar stylings
  $("li.side-item.category").removeClass("active");
  $("#"+cat+"-category").addClass("active");
}

function setNewState() {
  localStorage["query"] = JSON.stringify(query);
  localStorage["minPrice"] = JSON.stringify(minPrice);
  localStorage["maxPrice"] = JSON.stringify(maxPrice);
  localStorage["category"] = JSON.stringify(category);
  localStorage["page"] = JSON.stringify(page);
  localStorage["order"] = JSON.stringify(order);
  localStorage["savedHtml"] = JSON.stringify(savedHtml);
}

function setIsLoaded(bool) {
  localStorage["isLoaded"] = JSON.stringify(bool);
}

function getIsLoaded() {
  return localStorage["isLoaded"] === "true";
}

function revertState() {
  query = JSON.parse(localStorage["query"]);
  minPrice = JSON.parse(localStorage["minPrice"]);
  maxPrice = JSON.parse(localStorage["maxPrice"]);
  category = JSON.parse(localStorage["category"]);
  page = JSON.parse(localStorage["page"]);
  order = JSON.parse(localStorage["order"]);
  savedHtml = JSON.parse(localStorage["savedHtml"]);
}

function runloadBox(isRemoveHtml, isActive) {
  console.log(getScroll())
  if(isRemoveHtml) {
    page = 0;
  }
  if (isActive && getIsLoaded()) {
    revertState();
    setCategory(category);
    setOrder(order);
    setPricebox(minPrice, maxPrice);
  } else {
    query = document.getElementById('searchbar').value;
    minPrice = document.getElementById('min').value;
    maxPrice = document.getElementById('max').value;
  }
  console.log('query:'+query+' minprice:'+minPrice+' maxprice:'+maxPrice+' category:'+category+' page:'+page+' order:'+order);
  var cir_status = getCircs();
  
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
  
  if(maxPrice || minPrice) {      //hides and shows price icons
    $("#price-go").hide();
    $("#price-cancel").show();
  } else {
    $("#price-go").show();
    $("#price-cancel").hide();
  }

  var url="/ajax_box/?";
  var params = {
    q: query,
    max_price: maxPrice,
    min_price: minPrice,
    p: page,
    order: order
  };
  url = url + $.param(params);

  for (key in categoryObject) {
    if (categoryObject[key]==true) {
      cat_pk = cat2num(key)
      url = url + "&category="+cat_pk;
    }
  }
  
  for (key in cir_status) {
    if (cir_status[key]==true) {
      cir_pk = key
      url = url + "&" + "circle=" + cir_pk;
    }
  }
  
  if(filtering_by_friends){
    url = url+"&fbf=1";
  }
  
  $containerHtml = $(savedHtml);
  if(isActive && getIsLoaded()) {
    $container.append($containerHtml).masonry('appended', $containerHtml);
    $container.masonry();
    $(window).scrollTop(getScroll())
    $("#pac-ajax").hide();
  } else {
    $.ajax({
      type: "GET",
      url: url,
      dataType: "json",
      success: function(data){
        if(isRemoveHtml) {
          var elements = $container.masonry('getItemElements')
          if(elements.length > 0)
            $container.masonry('remove', elements);
          savedHtml = "";
          $(window).scrollTop(0)
        }
        if(data.length !== 0) {
          containerHtml = "";
          for(i = 0; i < data.length; i++) {
            var title = data[i].fields.title;
            var thumbnailUrl = data[i].extras.get_thumbnail_url;
            containerHtml += "<a href='/"+data[i].pk+"'><div class='box-item'><div class='box-image' style='background:url("+thumbnailUrl+") center center no-repeat;'> </div></div></a>"
            //containerHtml += "<img class='box-image' src='"+thumbnailUrl+"'></a></div>";
          }
          savedHtml += containerHtml;
          $containerHtml = $(containerHtml);
          $container.append($containerHtml).masonry('appended', $containerHtml);
          $container.masonry();
          
          //Calvin's random unimportant sidebar crap
          var filters = "";          
          if(query) {
            filters = "<li>" + "Search: " + query + "</li>";
          }
          if(minPrice || maxPrice) {
            filters = filters + "<li>" + "Price: $" + minPrice + " to $" + maxPrice + "<li>";
          }
          if((typeof filters === 'undefined') || (filters === "")) {
            filters = "<li> None </li>";
          }
        }
        $("#pac-ajax").hide();
        setNewState();
      }
    });
  }
  setIsLoaded(true);
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

