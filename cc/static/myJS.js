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
            heights = xxxx["heights"];
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
        "heights" : heights,
        "current_page" : current_page,
        "circles" : gcircs(),
        "categories" : gcats(),
        "filtering_by_friends" : filtering_by_friends,
        "query" : document.getElementById('searchbar').value,
        "min_price" : document.getElementById('min').value,
        "max_price" : document.getElementById('max').value,
        "flags" : flags,
        "oflags" : oflags
    });
    
    //document.location = inputurl;
}
/*
function toggle_friends_filter(){
    filtering_by_friends = !filtering_by_friends;
    
    runloadBox(current_page);
    
}*/


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


     //      x =  " <li id=\"fat-menu\" class=\"dropdown\">";
           x += "   <a href=\"#\" class=\"dropdown-toggle\" data-toggle=\"dropdown\">" + "<span class=\"badge badge-warning\">" + count + "</span>" + "Notifications<b class=\"caret\"></b></a>";
           x += "   <ul class=\"dropdown-menu no-collapse\">";

           for(var k = 0; k < count; k++){
             x += "     <li><a href=\"/" + obj[k].fields.post_from + "\">" + obj[k].extras.username + " posted " + obj[k].extras.title + "</a></li>";
           }

           x += "   </ul>";
          // x += " </li>";
         }

         element_in_question.innerHTML = x;

       }       
     }
   };


  var url="/get_friend_notifications/";
  xhr.open("GET",url,true);
  xhr.send();
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
    if(max_price && min_price) {      //hides and shows price icons
      $("#price-cancel").hide();
      $("#price-go").show();
    } else {
      $("#price-cancel").show();
      $("#price-go").hide();
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

        if(!(string1 == old_obj) || 100){	//broken code here!!!!!!!!!!!!!!

        old_obj = string1;

        var obj = eval ("(" + string1 + ")");
        
        var w = 916;
        var h = 1400;


        var width = (w-(w%numx))/numx;




        var sc = 0;

        
        
        function render(x,y,ww,hh,obj){
           ind3x = 0;

           var pfactor = 12;
           var stylin = "";
           if(obj.extras.friend){stylin+="class=\"friend_boxxx\"";}
           else{stylin += 'class="boxxx '+obj.pk+' "';}
           stylin += "style=\"left: " + x + "px; top: " + y + "px; height: " + (hh-5) + "px; width: "+ (ww-5) + "px\"";

           var moar = "<a OnClick=\"save_state('/" + obj.pk + "')\" class='empty-link' value='"+obj.pk+"' href='/"+obj.pk+"'><div "+stylin+">";
           moar += "<div class=\"box-div\">";
           /*moar += "OnClick=\"document.location='/" + obj.pk + "'\"><b>" + obj.fields.title;
           moar +=  "</b></br>" + num2cat(obj.fields.category) + "</br>$";
           moar += obj.fields.price + "</br>" + obj.fields.time_created + "</br>";
           if(obj.extras.friend){
               moar += "From your friend <b>" + obj.extras.friendname + "</b>";
           }
           if(!(obj.extras.get_image_set_urls == null)){
               var urls = obj.extras.get_image_set_urls.split(",");
               var filename = urls[0];
               filename = filename.replace(/'/g,"").replace("[","").replace("]","");
               var thumbnail = obj.extras.get_thumbnail_set_urls.split(",");
               thumbnail = thumbnail[0];
               thumbnail = thumbnail.replace(/'/g,"").replace("[","").replace("]",""); 
               moar += "<a href=\"" + filename + "\"><img alt=\"\" src=\"" + thumbnail + "\" /></a>";
           }*/
           var imageHeight=hh-pfactor-36; //got rid of -36. !!PUT BACK THE 36

           var imageWidth=ww-pfactor;

           if(!(obj.extras.get_thumbnail_url == null)){
               var thumbnail = obj.extras.get_thumbnail_url;
               thumbnail = thumbnail.replace(/'/g,"");
               //moar += "<img class=\"box-image\" style=\"width:"+imageWidth+"px; height:" +imageHeight+ "px;\" alt=\"\" src=\"" + thumbnail + "\" />";
               moar += "<img class=\"box-image\" style=\"max-width:"+imageWidth+"px; height:" +imageHeight+ "px;\" alt=\"\" src=\"" + thumbnail + "\" />";
               //moar += "<img class=\"box-image\" style=\"\" alt=\"\" src=\"" + thumbnail + "\" />";
           }/* explanation incoming */

           moar += " <div class=\"box-text-div\"><p class=\"box-text\">"+obj.fields.title;
           if(obj.extras.friend == 1){moar += "<br>" + obj.extras.friendname;}
           moar += " - $" + obj.fields.price + " </p></div>";
           moar += "</div> </div></a>";
           return moar;
        }


        for(var i = 0; i < obj.length; i++){
          var curheight = 250 + 50*Math.random();

          var mindex = 0;
          for(var j = 0; j < numx; j++){
            if(heights[mindex] > heights[j]){
              mindex = j;
            }
          }

          var y = heights[mindex];
          heights[mindex] = heights[mindex] + curheight;
          var x = width*mindex;
    
          $("#myBox").append(render(x,y,width,curheight,obj[i]));

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
            $("#contact-modal").modal('hide');
            $("#success-modal").modal('show');
        }
    })
})
