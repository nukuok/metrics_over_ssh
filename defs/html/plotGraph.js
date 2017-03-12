var parseTime = d3.timeParse("%H:%M:%S");
var formatTime = d3.timeFormat("%H:%M:%S");

function pgModel(){
    this.model = {};
    this.data = {};
    this.timestamp = [];


    this.upper = 100;
    this.lower = 0;
    this.startIndex = 0;
    // this.endIndex = 0;

    this.model.method = {};
    this.model.method.update={};
}

function pgView(){
    this.draw=function(){
	// console.log(this.data);
	var width = 400;
	var height = 200;
	var xScale = d3.scaleTime().range([0, width]);
	var yScale = d3.scaleLinear().range([height, 0]);

	var newTimeStamp = this.data["timestamp"].map(function(d){
	    return parseTime(d);
	})
	var value = this.data["%sys-CPU-all"]

	var valueline = d3.line()
	    .x(function(d, i) { return xScale(newTimeStamp[i]); })
	    .y(function(d, i) { return yScale(value[i]); });
	    // .x(function(d, i) { console.log(xScale(newTimeStamp[i]));return xScale(newTimeStamp[i]); })
	    // .y(function(d, i) { console.log(yScale(value[i])); return yScale(value[i]); });

	xScale.domain(d3.extent(newTimeStamp))
	yScale.domain([0, 100])

	console.log(xScale(newTimeStamp[0]))
	// console.log(xScale(newTimeStamp[1]))
	console.log(this.data["timestamp"])
	// console.log(yScale(this.data["%sys-CPU-all"][1]))
	console.log(value)

	this.nodeg.append("path")
	    .data([this.data["timestamp"]])
	    .attr("class", "line")
	    .attr("d", valueline)

	this.nodeg.append("g")
	    .attr("transform", "translate(0, " + height + ")")
	    .call(d3.axisBottom(xScale))

	this.nodeg.append("g")
	    .call(d3.axisLeft(yScale))
    };
    this.remove=function(){
	this.nodeg.remove();
    }
}

function pgController(){
}

var plotGraph = {
    init: function(nodeg){
	this.nodeg = nodeg;
	pgModel.call(this);
	pgView.call(this);
	pgController.call(this);
    }
}

var pgInstance = Object.create(plotGraph)

var testnodeg = testColumnSvg.append("g")
    .attr("transform", "translate(" + 50 + "," + 20 + ")");

pgInstance.init(testnodeg)
d3.json("/source/1/status?from_index=0&items=timestamp,%sys-CPU-all",
	function(response){
	    pgInstance.data = response;
	    pgInstance.draw();
})
