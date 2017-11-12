
function format_plural(number, unit, pluralize = true)
{
    if (pluralize && number != 1)
    {
        unit = unit + 's';
    }
    return `<span style="font-size:25px; margin:2px">${number}</span><span style="font-size:15px; margin:2px">${unit}</span>`
}

function parse_seconds_to_time(number_of_seconds)
{
  return {
      days: Math.floor(number_of_seconds / (3600 * 24)),
      hours: Math.floor((number_of_seconds % (3600 * 24)) / 3600),
      minutes: Math.floor((number_of_seconds % (3600 * 24) % 3600) / 60),
      seconds: Math.floor(((number_of_seconds % (3600 * 24)) % 3600) % 60)
    }
}


function format_seconds(t_seconds, units, pluralize=true)
{
    var s_f, m_f, h_f, d_f;

    if (t_seconds < 60) {
      return `${t_seconds}</span><span style="font-size:15px; margin:2px">${units.seconds}</span>`;
    }

    duration = parse_seconds_to_time(t_seconds);
    s_f = (duration.seconds != 0) ? format_plural(duration.seconds, units.seconds, pluralize) : "";
    d_f = (duration.days != 0) ? format_plural(duration.days, units.days, pluralize) : "";
    if (duration.minutes != 0) {
      m_f = format_plural(duration.minutes,units.minutes, pluralize);
    }
    else {
      if (duration.seconds != 0 && (duration.hours != 0 || duration.days != 0)) {
       m_f = format_plural(duration.minutes,units.minutes, pluralize);
     }
     else {
       m_f = "";
     }
    }

    if (duration.hours != 0) {
      h_f = format_plural(duration.hours,units.hours, pluralize);
    }
    else {
      if ((duration.days != 0) && (duration.seconds != 0 || duration.minutes != 0)) {
       h_f = format_plural(duration.minutes, units.hours, pluralize);
     }
     else {
       h_f = "";
     }
    }
    return `${d_f}${h_f}${m_f}${s_f}`
}

function format_seconds_long(seconds){
  return format_seconds(seconds, {seconds:'second',
                                  minutes:'minute',
                                  hours:'hour',
                                  days:'day'}, true)
}

function format_seconds_short(seconds)
{
    return format_seconds(seconds, {seconds:'s',
                                    minutes:'m',
                                    hours:'h',
                                    days:'d'}, false)
}

function progress_chart_track(inner_radius, outer_radius, color)
{
    return {outerRadius: outer_radius,
            innerRadius: inner_radius,
            backgroundColor: color,
            borderWidth: 0}
}

var training_progress_chart;

$(document).ready(
function (){
training_progress_chart = new Highcharts.Chart({
    chart: {
        renderTo:'progress-meter',
        type: 'solidgauge',
        margin: 0,
        padding: 0,
        horizontalAlign:'center'
    },

    title: {text: ''},
    tooltip: { enabled: false },

    pane: {
        startAngle: 0,
        endAngle: 360,
              background: [{ // Track for Move
                    outerRadius: '100%',
                    innerRadius: '85%',
                    backgroundColor: Highcharts.Color(Highcharts.getOptions().colors[1])
                        .setOpacity(0.3)
                        .get(),
                    borderWidth: 0
                }, { // Track for Exercise
                    outerRadius: '80%',
                    innerRadius: '65%',
                    backgroundColor: Highcharts.Color(Highcharts.getOptions().colors[1])
                        .setOpacity(0.3)
                        .get(),
                    borderWidth: 0
                }]},

    yAxis: {
        min: 0,
        max: 100,
        lineWidth: 0,
        tickPositions: []
    },

    plotOptions: {
        solidgauge: {
            dataLabels: {
                enabled: false
            },
            linecap: 'square',
            stickyTracking: false,
            rounded: false
        }
    },

    series: [{
        name: 'Move',
        data: [{
            color: Highcharts.getOptions().colors[9],
            radius: '100%',
            innerRadius: '85%',
            y: 0
        }]
    }, {
        name: 'Exercise',
        data: [{
            color: Highcharts.getOptions().colors[1],
            radius: '80%',
            innerRadius: '65%',
            y: 0
        }]
    }]
}
);})



function update_stats()
{
    $.getJSON('http://localhost:5000/json/training_stats.json',
            function(data) {
                //console.log(data);
                $('#stats-training-loss').text(data.training.loss.toFixed(2));
                $('#stats-training-accuracy').text((100*data.training.accuracy).toFixed(2));
                $('#stats-validation-loss').text(data.validation.loss.toFixed(2));
                $('#stats-validation-accuracy').text((100*data.validation.accuracy).toFixed(2));
            }
        );
}


function update_progress()
{
    $.getJSON('http://localhost:5000/json/training_progress.json',
            function(data) {
                $('#stats-batch-time').html(format_seconds_short(data.batch_time.toFixed(2)));
                $('#stats-epoch-time').html(format_seconds_short(data.epoch_time.toFixed(2)));
                $('#elapsed-time').html(format_seconds_long(data.elapsed_time.toFixed(2)));
                $('#remaining-time').html(format_seconds_long(data.remaining_time.toFixed(2)));
                $('#epoch-number').text(data.epoch_number);
                $('#total-epochs').text(data.total_epochs);
                training_progress_chart.series[1].points[0].update(data.percent_epoch_complete);
                training_progress_chart.series[0].points[0].update(data.percent_training_complete);
            }
        );

}

function humanFileSize(bytes) {
    var thresh = 1024;
    if(Math.abs(bytes) < thresh) {
        return `<span style="font-size:20px">${bytes}</s><span style="font-size:12px">B</s>`;
    }
    var units = ['kB','MB','GB','TB','PB','EB','ZB','YB']
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return `<span style="font-size:20px">${bytes.toFixed(1)}</s><span style="font-size:12px">${units[u]}</span>`;
}

function format_memory_usage(used, total){
  return `${humanFileSize(used)}<span style="font-size:20px>">/</span>${humanFileSize(total)}`
}


function update_cpuinfo()
{
    $.getJSON('http://localhost:5000/json/system_stats.json',
            function(data) {
                cpu_percentage = data.cpu;
                memory_used = data.memory[0];
                memory_available = data.memory[1];
                $('#stats-cpu-usage').html(`${cpu_percentage.toFixed(2)}%`);
                $('#stats-memory-usage').html(format_memory_usage(memory_used, memory_available));
            }
        );

}
