

var loss_graph;
var accuracy_graph;

function make_graph(height, renderTo)
{
    var g = new Highcharts.Chart(
        {chart: {   renderTo: renderTo,
                    height:height,
                    spacingLeft:0,
                    spacingBottom:0
        },
        title: {text: ''},
        xAxis: {type: 'datetime'},
        yAxis: {title: {text: ''}},
        legend: {enabled: false},
        plotOptions: {
            area: {marker: {radius: 2},
                   lineWidth: 1,
                   states: {hover: {lineWidth: 1}},
                   threshold: null}},

        series: [
                    {type: 'line',
                     data: [],
                     name: 'Training',
                     color: {linearGradient: {x1: 0,y1: 0,x2: 1, y2: 1},
                             stops: [[0, 'rgb(160,32,240)'],
                                    [1, 'rgb(160,32,240)']]}},
                    {type: 'line',
                     data: [],
                     name: 'Validation',
                     color: {linearGradient: {x1: 0,y1: 0,x2: 1, y2: 1},
                             stops: [[0, 'rgb(34,139,34)'],
                                    [1, 'rgb(34,139,34)']]}}
                ]
        });
    return g
}


var graph_time_span = 500
var max_displayed_time = -graph_time_span;

var training_loss_series_data = [];
var validation_loss_series_data = [];

var training_accuracy_series_data = [];
var validation_accuracy_series_data = [];


function update_graphs()
{
    $.getJSON('http://localhost:5000/json/training_graphs.json?min_timestamp='+Math.round(max_displayed_time),
        function(data) {
            var loss_training_timestamps = data.loss.train.map((p)=> p[0]);
            var loss_validation_timestamps = data.loss.validation.map((p)=> p[0]);
            var max_1 = Math.max.apply(null, loss_training_timestamps);
            var max_2 = Math.max.apply(null, loss_validation_timestamps);
            max_displayed_time = Math.max(max_displayed_time, max_1, max_2, 0);
            var min_displayed_time = max_displayed_time - graph_time_span

            data.loss.train.forEach((element) => training_loss_series_data.push(element));
            training_loss_series_data = training_loss_series_data.filter((element) => {return element[0] >= min_displayed_time});

            data.loss.validation.forEach((element) => validation_loss_series_data.push(element));
            validation_loss_series_data = validation_loss_series_data.filter((element) => {return element[0] >= min_displayed_time});
            loss_graph.series[0].setData(training_loss_series_data, false, false, false);
            loss_graph.series[1].setData(validation_loss_series_data,  false, false, false);
            loss_graph.redraw()

            data.accuracy.train.forEach((element) => training_accuracy_series_data.push(element));
            training_accuracy_series_data = training_accuracy_series_data.filter((element) => {return element[0] >= min_displayed_time});

            data.accuracy.validation.forEach((element) => validation_accuracy_series_data.push(element));
            validation_accuracy_series_data = validation_accuracy_series_data.filter((element) => {return element[0] >= min_displayed_time});
            accuracy_graph.series[0].setData(training_accuracy_series_data, false, false, false);
            accuracy_graph.series[1].setData(validation_accuracy_series_data, false, false, false);
            accuracy_graph.redraw()
        }
    );

}
