function search(){
    $.mobile.loading( 'show', {
        text: 'foo',
        //textVisible: true,
        theme: 'a',
        html: ""
    });
    var send_data = {};
    var searchText = $("#search-basic").val();
    send_data['searchText'] = searchText;
    $.ajax({
               type: "GET",
               url: "/ajax/browse/",
               data: send_data,
               success: function(data){
                   var data = eval(data);
                   var browseHtml = ""
                   for (index in data) {
                       var entry = data[index];
                       browseHtml += "<li><a href='/"+entry['pk']+"'>"
                       browseHtml += "<img src='" + entry['fields']['cached_thumb'] + "' />"
                       browseHtml += "<h3>" + entry['fields']['title'] + "</h3>"
                       browseHtml += "<p>$" + entry['fields']['price'] + "</p></a></li>"
                   }
                   $.mobile.loading( 'hide', {
                       text: 'foo',
                       //textVisible: true,
                       theme: 'a',
                       html: ""
                   });
                   $("#browse-list").html(browseHtml).listview("refresh");
               }
           })

}

