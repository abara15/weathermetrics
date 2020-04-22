$(window).on('load', function(){
    function weather() {
        var locationKey = "http://api.accuweather.com/locations/v1/cities/search.json?q=melbourne&apikey=8GGqTVDqQc6P5lg3TtgT8artGzWtA9tV&language=en-us";
        $.getJSON(locationKey, function(data) {
            console.log(data);
            updateDOM(data);
        });
    }

    weather();

    function updateDOM(data) {
        var city = data.EnglishName;
        $("#locationName").html(city);
        console.log("City: " + city);
    }
});

// Do this stuff using requests in flask server