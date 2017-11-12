function format_nanoseconds (ts) {
    var sec_num = Math.round(ts / 1000000000);
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}

    if (hours == 0){
        return minutes+':'+seconds;
    }
    return hours+':'+minutes+':'+seconds;
}

function format_plural(number, unit, pluralize = true)
{
    if (pluralize && number != 1)
    {
        unit = unit + 's';
    }
    return `${number} ${unit}`
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
    return `${d_f} ${h_f} ${m_f} ${s_f}`
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

function humanFileSize(bytes) {
    var thresh = 1024;
    console.log("FOOBARBAR");

    if(Math.abs(bytes) < thresh) {
        return `<span style="font-size:16px">${bytes}</span><span style="font-size:11px"></span>`;
    }
    var units = ['kB','MB','GB','TB','PB','EB','ZB','YB']
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return `<span style="font-size:16px">${bytes.toFixed(1)}</span><span style="font-size:11px">${units[u]}</span>`;
}

function format_memory_usage(used, total){
  console.log("FOOBAR");
  return `${humanFileSize(used)}<span style="font-size:15px>">/</span>${humanFileSize(total)}`
}
