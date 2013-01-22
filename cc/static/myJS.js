function restore(){
    window.setTimeout(function(){
   
        var mybox = document.getElementById("myBox");
        var sessionField = document.getElementById("sfield");
        var sessionField_scroll = document.getElementById("sfield_scroll");
        var xxxx = eval('(' + sessionField_scroll.value + ')');
        
        if(xxxx === 3){
            clear_restore();
            runloadBox();
        }
        
        else{
        
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
            x += "<a href=\"#\" class=\"dropdown-toggle\" data-toggle=\"dropdown\" style=\"text-decoration:none\"> <span class=\"badge badge-warning\">" + obj[0].extras.num_unread + "</span> <i class=\" icon-exclamation-sign\" style=\"margin-top:3px;\"></i></a>";
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
x += "<a href=\"#\" class=\"dropdown-toggle\" data-toggle=\"dropdown\" style=\"text-decoration:none\"> <span class=\"badge badge-success\">"+count+"</span> <i class=\" icon-exclamation-sign\" style=\"margin-top:3px;\"></i></a>";
          }
          element_in_question.innerHTML = x;
        }
      }       
    }
    var url="/get_friend_notifications/?cap=yup";
    xhr.open("GET",url,true);
    xhr.send();
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
              html += "<td> "+notif[2]+" </td>";
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

  function toggler(control) {  //should really be renamed to togglr . this is web 2.0 you know....
    var id = document.getElementById(control);
    $(id).toggle();
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
    

    flags = "_" + query + min_price + max_price + cs + ccs + filtering_by_friends;


    if(oflags != flags) {
        $(window).scrollTop(0);
        oflags = flags; 
        $("#myBox").empty(); //accidentally the posts
        scraps=[];
        current_page=0;
        loadBox(query,min_price,max_price,cat_status,cir_status,filtering_by_friends,0);
    } else {
        loadBox(query,min_price,max_price,cat_status,cir_status,filtering_by_friends,pg);
    }
  }

  function loadBox(query,min_price,max_price,cat_status,cir_status,filtering_by_friends,page){

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

    var xmlhttp;
    if (window.XMLHttpRequest){
      xmlhttp=new XMLHttpRequest();
    }
    else{
      xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange=function(){
      if(xmlhttp.readyState==4 && xmlhttp.status==200){
        var string1 = xmlhttp.responseText;

        //alert(string1);
        if(!(string1 == old_obj) || 100){	//broken code here!!!!!!!!!!!!!!

        old_obj = string1;

        var obj = eval ("(" + string1 + ")");

   //     var sizes = [[2,2],[1,1]];  //gogo tetris mode
        var sizes = [[1,1],[1,1]];
        var w = 916;
        var h = 1400;

    //    var numx = 6;
    //    var numy = 12;
        var numx = 3;
        var numy = 6;
        var width = (w-(w%numx))/numx;
        var height = (h-(h%numy))/numy;
        ogrid = [];
        var sc = 0;

        var lenk = scraps.length;
        if(page){
          if(lenk > 0){
              for(var i = 0; i < lenk; i++){
                  scraps[i].extras.boxsize=0;
                  scraps[i].priority=1;
                  obj.unshift(scraps[i]);
              }
              scraps=[];
          }
        }
        else scraps=[];

        var idid = "myBox" + page;
        var boxxy = document.getElementById(idid); 

        if(boxxy == null) {$("#myBox").append("<div id = \"myBox" + page + "\"style=\"position:relative; top: " + page * h + "px;\"></div>");}
        document.getElementById(idid).innerHTML="";

        function render(x,y,obj,grid){
           ind3x = 0;
           var ww = sizes[obj.extras.boxsize][0];
           var hh = sizes[obj.extras.boxsize][1];
           var pfactor = 12;
           var stylin = "";
           if(obj.extras.friend){stylin+="class=\"friend_boxxx\"";}
           else{stylin += 'class="boxxx '+obj.pk+' "';}
           stylin += "style=\"left: " + x*width + "px; top: " + y*height + "px; height: " + ((height*hh)-pfactor) + "px; width: "+ ((width*ww)-pfactor) + "px\"";

           var moar = "<a OnClick=\"save_state('/" + obj.pk + "')\" class='empty-link' value='"+obj.pk+"' href='/"+obj.pk+"'><div "+stylin+">";
           moar += "<div class=\"box-div\">";

           var imageHeight=(height*hh)-pfactor-36; //got rid of -36. !!PUT BACK THE 36
           var imageWidth=(width*ww)-pfactor;

           if(!(obj.extras.get_thumbnail_url == null)){
               var thumbnail = obj.extras.get_thumbnail_url;
               thumbnail = thumbnail.replace(/'/g,"");
               //moar += "<img class=\"box-image\" style=\"width:"+imageWidth+"px; height:" +imageHeight+ "px;\" alt=\"\" src=\"" + thumbnail + "\" />";
               moar += "<img class=\"box-image\" style=\"max-width:"+imageWidth+"px; height:" +imageHeight+ "px;\" alt=\"\" src=\"" + thumbnail + "\" />";
               //moar += "<img class=\"box-image\" style=\"\" alt=\"\" src=\"" + thumbnail + "\" />";
           }/* explanation incoming */

           moar += " <div class=\"box-text-div\"><p class=\"box-text\">";
           if(obj.extras.pending_flag){moar += "[Sale Pending] ";}
           moar += obj.fields.title;
           if(obj.extras.friend == 1){moar += "<br>" + obj.extras.friendname;}
           moar += " - $" + obj.fields.price + " </p></div>";
           moar += "</div> </div></a>";
           return moar;
        }


        for(var i = 0; i < numx; i++){
            var tmp = [];
            for(var j = 0; j < numy; j++){
                tmp.push(0);
            }
            ogrid.push(tmp);
        }

        for(var i = 0; i < obj.length; i++){
            obj[i].priority = 0;
        }

        var failing,fail_threshold,force_x,force_y, demoting;

        function check(x,y,obj,grid){
            var ffail = 0;
            var osize = obj.extras.boxsize;
            var ww = sizes[osize][0];
            var hh = sizes[osize][1];
            if(x+ww > numx || y+hh > numy) return 666;
            for(var xxx = 0; xxx < ww; xxx++){
                for(var yyy = 0; yyy < hh; yyy++){
                    if(grid[x+xxx][y+yyy])return 666;
                }
            }
            return ffail;
        }

        function set(x,y,obj,grid){
            var ww = sizes[obj.extras.boxsize][0];
            var hh = sizes[obj.extras.boxsize][1];
            $("#myBox"+page).append(render(x,y,obj,grid));
            for(var xx = 0; xx < ww; xx++){
                for(var yy = 0; yy < hh; yy++){
                    grid[x+xx][y+yy] = obj.pk;
                }
            }
        }

        function randfit(obj,grid){
            while(failing < fail_threshold){
                var xtar = Math.floor((rand0m()*(numx - sizes[obj.extras.boxsize][0])));
                var ytar = Math.floor((rand0m()*(numy - sizes[obj.extras.boxsize][1])));
                if(check(xtar,ytar,obj,grid) > 0){
                    failing = failing + 1;
                }
                else{
                    set(xtar,ytar,obj,grid);
                    return 1;
                }
            }
            return 0;
        }

        function forcefit(obj,grid){
            var x,y;
            for(x = force_x; x < numx; x++){
                for(y = (!x)*force_y; y < numy; y++){
                    if(!(check(x,y,obj,grid))){  //true on success
                        set(x,y,obj,grid);
                        force_x = x;
                        force_y = y;
                        return 1;
                    }
                }
            }
            return 0;
        }        

        var fitx = (numx - (numx % sizes[0][0])) / sizes[0][0];
        var fity = (numy - (numy % sizes[0][1])) / sizes[0][1];
        
        var fitx_small = (numx - (numx % sizes[1][0])) / sizes[1][0];
        var fity_small = (numy - (numy % sizes[1][1])) / sizes[1][1];
        
        var onum = 0; 

        if((current_page<1) && obj.length == 0){
            $("#myBox").html("<h2>Sorry, there were no items that matched your search.</h2>");
        }


        if(obj.length < fitx_small*fity_small && 0){ //very few results. let's promote everything to max size (when doing a restrictive search)
        
            for(var y = 0; y < fity; y++){
                for(var x = 0; x < fitx; x++){ 
                    if(onum >= obj.length){x = fitx; y =fity;} //bail if no more objects to place down..
                    else{obj[onum].extras.boxsize = 0; set(x*sizes[0][0],y*sizes[0][1],obj[onum],ogrid);}
                    onum++; 
                }
            }
        }

        else{                                        // there are more than a few results, so use multi-size standard boxfitting technique (most of the time)
            for(var i = 0; i < sizes.length; i++){ 
                failing = 0;
                fail_threshold = -100;
                force_x = 0;
                force_y = 0;
                demoting = 0;
    
                for(var j = 0; j < obj.length*2; j++){ 
                    var jj = j % obj.length; 
                    if(obj[jj].extras.boxsize == i && (obj[jj].priority == (j<obj.length))){  //is the object of the size we are considering?
                        if(demoting){
                            obj[jj].extras.boxsize += 1;
                            obj[jj].extras.priority = 1;
                        }
                        else{
                            if(failing < fail_threshold){
                                randfit(obj[jj],ogrid);
                            }
                            else{
                                if(!forcefit(obj[jj],ogrid)){
                                    demoting = 1;
                                    obj[jj].extras.boxsize += 1;
                                    obj[jj].priority = 1;
                                }
                            } 
                        } 
                    }  //descend the bracket mountain
                }
            }  
        }  

        for(var j = 0; j < obj.length; j++){
            if(obj[j].extras.boxsize == sizes.length){ 
                scraps.push(obj[j]);
            }
        }

       
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
        //document.getElementById("active-filter").innerHTML = filters;
      }
    }
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
  xmlhttp.open("GET",url,true);
  xmlhttp.send();
}

$("#modal-send").on("click", function(){
    $(this).button('loading');
    var message = $("#modal-message").val();
    data= {};
    //data['sender_pk'] = sender_pk; user data can be accessed in the request
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

