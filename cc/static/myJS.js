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
        "flags" : flags,
        "oflags" : oflags
    });
    
    //document.location = inputurl;
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
           var imageHeight=(height*hh)-pfactor-36; //got rid of -36. !!PUT BACK THE 36

           var imageWidth=(width*ww)-pfactor;

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
        if(obj.length < fitx_small*fity_small){ //very few results. let's promote everything to max size (when doing a restrictive search)
        
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
                fail_threshold = 100;
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
            $("#contact-modal").modal('hide');
            $("#success-modal").modal('show');
        }
    })
})
