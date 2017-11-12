
function format_plural(number, unit)
{
    if (number != 1)
    {
        unit = unit + 's';
    }
    return `<span style="font_size=25">${number}</span> <span style="font_size=15">${unit}</span>`
}

function format_seconds_long(t_seconds)
{
    var days = Math.floor(t_seconds / (3600 * 24));
    var hours = Math.floor((t_seconds % (3600 * 24)) / 3600);
    var minutes = Math.floor((t_seconds % (3600 * 24) % 3600) / 60);
    var seconds = ((t_seconds % (3600 * 24)) % 3600) % 60;

    d_f = (days != 0) ? format_plural(days, 'day') : "";

    d_f = (days != 0) ? format_plural(days, 'day') : "";
    h_f = (hours != 0) ? format_plural(hours, 'hour') : "";
    m_f = (minutes != 0) ? format_plural(minutes,'minute') : "";
    s_f = (seconds != 0) ? format_plural(seconds, 'second') : "";
    return `${d_f} ${h_f} ${m_f} ${s_f}`
}

console.log(format_seconds_long(3600));
