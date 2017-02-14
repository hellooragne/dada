var mysql    = require('mysql');
var log      = require('../../log/log.js')('|');
//var settings = require('../../config/database.json');

//创建数据库连接实例并且连接数据库,保持长连接

var db = {
	connection : null,
	query : function(sql, values, callback) {

		//this.connection.query(sql, values, callback);
		var argLen = arguments.length;
		switch(argLen) {
			case 3:
				var query = this.connection.query(sql, values, function(err, results, fields) {
					callback(err, results);
				});

				log.trace(query.sql);
				break;
			case 2:
				if (typeof values == 'function') {
					var query = this.connection.query(sql, function(err, results, fields) {
						values(err, results);
					});

					//log.trace(query.sql);
				} else {
					var query = this.connection.query(sql, values);
					log.trace(query.sql);
				}
				break;
			case 1: {
				var query = this.connection.query(sql);
				log.trace(query.sql);
			}
		}

	},

	_heartbeat : function(time) {
		this.query('SELECT 1', function(err, results, fields) {
			if (err) {
				log.error(err.name + ':' + err.message);
				log.info('heatbeat fail');
				process.exit();
			}
			log.trace('database heartbeat');
		});

		var self = this;
		setInterval(function() {
			self.query('SELECT 1', function(err, results, fields) {
				if (err) {
					log.error(err.name + ':' + err.message);
					log.info('heatbeat fail');
					process.exit();
				}
				log.trace('database heartbeat');
			});
		}, time);
	},

	connect : function(settings) {
		if (this.connection) {
			this.connection.destroy();
		}

		this.connection = mysql.createConnection(settings);
		this.connection.connect();
		this.connection.on('error', function(err) {
			log.error(err.name + ':' + err.message);
			log.info('database error, Server shutdown');
			process.exit();
		});
		this._heartbeat(600000);
	}
};

module.exports = db;
