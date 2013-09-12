/*****************************
 * Boxview
 * 
 * States are stored using "localstorage" which is persistent until a cache/cookie clear.
 * 
 * isRemoveHtml: Boolean that determines if I want to clear out the boxes, e.g., clicking on a new category, I want to keep it true so the boxes get cleared out. On a scroll down load, I want to preserve my current html.
 * isLoadingMiddle: Boolean that determines where the ajax loading box is, the middle or bottom.
 * isBoxActive: Boolean, saved in localStorage. Indicates if we want the saved state. Set to false on every page except "viewitem" using the beforeunload and unload functions. Also, force a false on all "browse" clicks. That way, we only load an old session on a "back" from an item view.
 * isRunning: Boolean that returns true while loadbox is running, false otherwise.
 * 
 * 
 * 1. Check isRemoveHtml and reset page value if true, otherwise page will get incremented and is stored.
 * 2. Check isBoxActive and if a session is stored. Then, set all variables based on what is in storage if true.
 * 3. Query and price filter icon stuff.
 * 4. Set URLS. Category is actually an id integer. "Everything" is hardcoded to -1.
 * 5. Setting up the box: Check if active and if a session is stored. If so, populate the the box using HTML in storage and scroll to the proper position.
 * Otherwise: Do the get. Check to isRemoveHtml, and possibly clear out old masonry boxes. The new HTML and saved HTML are added to each other. Check strings, display box warning text if empty. Then HTML time. Populate the box with masonry. !!! Load the current variables into storage.
 * 6. Since we have just run loadbox, a session must be stored, so we mark the boolean as true. We also force isBoxActive false and the animation so the user can navigate after a session load normally.
 * 
 * Functions that are running alongside:
 * 1. A scroll function that monitors the position and increments the page and fires a loadbox if we scroll down. (Located in box.html)
 * 2. A function fires on page exit which saves the current scroll position in storage. (Located in box.html)
 * 3. Functions that fire on page "unloads" and "beforeunloads" that set isBoxActive.
 * 
 *****************************/

// initialize masonry
var $container = $('#box');
var containerHtml = "";
var $containerHtml = $("");
var savedHtml = "";
$container.masonry({
  gutter: 13,
  itemSelector: '.box-item',
});

//sets isBoxActive if not yet set to prevent JSON conversion errors later
if(localStorage["isBoxActive"] === null) {
  localStorage["isBoxActive"] = JSON.stringify(false);
}

//Set animation. Ignore animation if we are loading a session to make the transition seem more "seamless".
if (JSON.parse(localStorage["isBoxActive"])) {
  $container.masonry({
    transitionDuration: 0
  })
} else {
  $container.masonry({
    transitionDuration: '0.6s'      //default 0.4s
  })
}

var query = "";
var minPrice = null;
var maxPrice = null;
var category = "Everything";
var categoryObject;
var page = 0;
var order = 'dateNew';
var isFilterFriends = false;
var isRunning = false;
var isDone = false;

function runloadBox(isRemoveHtml, isLoadingMiddle) {
  isRunning = true;
  isBoxActive = JSON.parse(localStorage["isBoxActive"])
  if(isRemoveHtml) {
    page = 0;
  }
  
  if (isBoxActive && getIsLoaded()) {
    revertState();
    setCategory(category);
    setOrder(order);
    setPricebox(minPrice, maxPrice);
    $("#searchbar").val(query);
  } else {
    query = document.getElementById('searchbar').value;
    minPrice = document.getElementById('min').value;
    maxPrice = document.getElementById('max').value;
  }
  
  var cir_status = getCircs();

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
  
  if (category === -1) {
    //Everything, do nothing
  } else {
    url = url + "&category="+category;
  }

  /*for (key in categoryObject) {
    if (categoryObject[key]==true) {
      cat_pk = cat2num(key)
      url = url + "&category="+cat_pk;
    }
  }*/
  
  /*for (key in cir_status) {
    if (cir_status[key]==true) {
      cir_pk = key
      url = url + "&" + "circle=" + cir_pk;
    }
  }*/
  
  if(isFilterFriends){
    url = url+"&fbf=1";
  }
  
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
  
  $containerHtml = $(savedHtml);        //Sets new HTML to any saved HTML
  if(isBoxActive && getIsLoaded()) {
    $container.append($containerHtml).masonry('appended', $containerHtml);
    $container.masonry();
    $(window).scrollTop(getScroll())
    //$("#pac-ajax").hide();
    isRunning = false;
  } else {
    //load pacman
    if(isLoadingMiddle) {
      $("#pac-ajax-mid").show();
    } else {
      $("#pac-ajax").show();
    }
    
    $.ajax({
      type: "GET",
      url: url,
      dataType: "json",
      success: function(data){
        if(data.length < 39) {
          isDone = true;
          //$("#box-done").show();
        } else {
          isDone = false;
          //$("#box-done").hide();
        }
        
        if(isRemoveHtml) {
          var elements = $container.masonry('getItemElements')
          if(elements.length > 0)
            $container.masonry('remove', elements);
          savedHtml = "";
          $(window).scrollTop(0)
        }
        containerHtml = "";
        for(i = 0; i < data.length; i++) {
          var thumbnailUrl = data[i].extras.get_thumbnail_url;
          var price = "$"+data[i].fields.price;
          var title = data[i].fields.title;
          var date = smartDate(data[i].fields.time_created);
          var username = data[i].extras.get_seller_first_name;
          var profilePictureUrl = data[i].extras.get_seller_profile_picture;
          containerHtml += "<a href='/"+data[i].pk+"'><div class='box-item'><img class='box-image' src='"+thumbnailUrl+"' /> <div class='box-text'> <div class='box-title'>"+title+"</div> <div class='box-hr'></div> <span class='box-left'><div class='box-price'>"+price+"</div><div class='box-date'>posted "+date+" by "+username+"</div></span> <div class='box-right'><img class='box-profile' src='"+profilePictureUrl+"'></div> </div> </div></a>";
        }
        savedHtml += containerHtml;
        $containerHtml = $(containerHtml);
        
        if(!savedHtml && !containerHtml) {
          $("#box-empty").show();
        } else {
          $("#box-empty").hide();
        }
        
        //Masonry errors if you attempt to append an empty. First check if if the string is not empty before appending.
        if(containerHtml) {
          $container.append($containerHtml).masonry('appended', $containerHtml);
        }
        
        $container.masonry();
        $("#pac-ajax").hide();
        $("#pac-ajax-mid").hide();
        setNewState();
        isRunning = false;
      }
    });
  }
  setIsLoaded(true);
  localStorage["isBoxActive"] = JSON.stringify(false);
  $container.masonry({
    transitionDuration: '0.6s'
  });
}

function getScroll() {
  return JSON.parse(localStorage["scroll"]);
}

function search(){
  q = document.getElementById('searchbar').value;
  url = "/browse/?q="+q
  window.location = url;
}

function searchbarCancel() {   //cancel for the search bar
  document.getElementById('searchbar').value = '';
  runloadBox(true);
}

function priceboxCancel() {   //cancel for the price box
  document.getElementById('max').value = null;
  document.getElementById('min').value = null;
}

function setPricebox(min, max) {
  document.getElementById('min').value = min;
  document.getElementById('max').value = max;
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

function setCategory(catid) {
  category = catid;
  //Search Bar Text
  document.getElementById('searchbar').placeholder = "Search in " + num2cat(catid);
  //Sidebar stylings
  $("li.side-item.category").removeClass("active");
  $("#"+catid+"-category").addClass("active");
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

function toggleFriendsFilter(){
  isFilterFriends = !isFilterFriends;
  if (isFilterFriends) {
      $("#friends-li").addClass("active");
  } else {
      $("#friends-li").removeClass("active");
  }
  runloadBox(true);
}

function getIsRunning() {
  return isRunning;
}