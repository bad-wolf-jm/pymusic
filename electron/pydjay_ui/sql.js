var mysql = require('mysql');

var db_connection = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "root",
  database:'pymusic'
});

function $QUERY(sql, with_result) {
    db_connection.query(
        sql,
        function (error, result) {
            if (error) {
                console.log(error)
                throw error;
            } else {
                with_result(result);
            }
        }
    )
}
