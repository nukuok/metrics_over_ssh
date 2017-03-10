body = d3.select("body")

leftBarDiv = body.append("div")
    .attr("id", "div1")
leftBarSvg = leftBarDiv.append("svg")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", 200)
    .attr("height", 1000)

function addRun(svgNode, metricsObject){
    var rowCount = 0;
    var rowHeight = 20;
    var rowIndent = 3;
    var rowIndentMore = 10;
    var hostSourceId = [];

    // console.log(metricsObject);
    var monitorNames = Object.keys(metricsObject)
    var monitorNum = monitorNames.length;
    var runNames;
    var runNum;
    var hostNames;
    var hostNum;
    for (ii = 0 ; ii < monitorNum ; ii++){
	svgNode.append("rect")
	    .attr("x", 0)
	    .attr("y", (rowCount + 0.3) * rowHeight)
	    .attr("width", 200)
	    .attr("height", 20)
	    .attr("fill", "gray")
	svgNode.append("text")
	    .attr("x", rowIndent)
	    .attr("y", (1 + rowCount) * rowHeight)
	    .attr("fill", "white")
	    .attr("font-size", 10)
	    .text(monitorNames[ii])
	rowCount += 1;
	runNames = Object.keys(metricsObject[monitorNames[ii]])
	runNum = runNames.length;
	for (jj = 0 ; jj < runNum ; jj++){
	    svgNode.append("rect")
		.attr("x", 0)
		.attr("y", (rowCount + 0.3) * rowHeight)
		.attr("width", 200)
		.attr("height", 20)
		.attr("fill", d3.rgb(200,200,200))
	    svgNode.append("text")
		.attr("x", rowIndent + rowIndentMore)
		.attr("y", (1 + rowCount) * rowHeight)
		.attr("font-size", 10)
		.text(runNames[jj])
	    rowCount += 1;
	    var hostNames = Object.keys(metricsObject[monitorNames[ii]][runNames[jj]])
	    var hostNum = hostNames.length;
	    for (kk = 0 ; kk < hostNum ; kk++){
		svgNode.append("rect")
		    .attr("x", 0)
		    .attr("y", (rowCount + 0.3) * rowHeight)
		    .attr("width", 200)
		    .attr("height", 20)
		    .attr("fill", d3.rgb(240,240,240))
		svgNode.append("text")
		    .attr("x", rowIndent + rowIndentMore * 2)
		    .attr("y", (1 + rowCount) * rowHeight)
		    .attr("font-size", 10)
		    .text(hostNames[kk])
		rowCount += 1;
		hostSourceId = hostSourceId.concat([[metricsObject[monitorNames[ii]][runNames[jj]][hostNames[kk]][0],
				    rowCount]])
	    }
	}
    }
    svgNode.attr("height", (1 + rowCount) * rowHeight)
    return hostSourceId;
}

d3.json("/source/lists", function(response) {metricsList = response;
					     hostSourcePosition = addRun(leftBarSvg, metricsList);
					     showingList = hostSourcePosition.forEach(function(){return 0;});
					    });


