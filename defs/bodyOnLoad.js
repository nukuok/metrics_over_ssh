function bodyOnload(){
    d3.json("/source/lists", function(response) { console.log(response); metricsList =  response; });
}

window.addEventListener('DOMContentLoaded', bodyOnload, false);
