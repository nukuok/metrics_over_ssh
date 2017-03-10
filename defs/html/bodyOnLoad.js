function bodyOnload(){
    d3.json("/source/lists", function(response) { metricsList =  response; });
}
