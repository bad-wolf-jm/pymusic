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
