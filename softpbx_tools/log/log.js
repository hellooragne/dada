var log4js   = require('log4js');
var path     = require('path');
var os 		 = require('os');
var settings = require('../config/log.json');

var basepath = '';
var layout = {
	"type": "pattern",
	"pattern": "[%d] [%p] %x{line} %c %m%n%",
	"tokens": {
		"line": function() {
			var err = new Error();
			var stack = err.stack;
			var stackLines = stack.split('\n');
			var lastLine = stackLines[stackLines.length - 1];
			var linePos = '';
			if (basepath == '') {
				var cells;
				if (os.type() == 'Windows_NT') {
					cells = lastLine.split('\\');
				} else {
					cells = lastLine.split('/');
				}

				linePos = cells[cells.length - 1];
			} else {
				var beginIdx = lastLine.indexOf(basepath);
				if (beginIdx != -1) {
					linePos = lastLine.substring(beginIdx + basepath.length);
					if (linePos[0] == '\\' || linePos[0] == '/') {
						linePos = linePos.substring(1);
					}
				}
			}

			linePos = linePos.replace(')', '');
			return linePos;
		}
	}
};

var colorLayout = {
	"type": "pattern",
	"pattern": "%[[%d] [%p] %x{line} %c %m%n%]",
	"tokens": {
		"line": function() {
			var err = new Error();
			var stack = err.stack;
			var stackLines = stack.split('\n');
			var lastLine = stackLines[stackLines.length - 1];
			var linePos = '';
			if (basepath == '') {
				var cells;
				if (os.type() == 'Windows_NT') {
					cells = lastLine.split('\\');
				} else {
					cells = lastLine.split('/');
				}

				linePos = cells[cells.length - 1];
			} else {
				var beginIdx = lastLine.indexOf(basepath);
				if (beginIdx != -1) {
					linePos = lastLine.substring(beginIdx + basepath.length);
					if (linePos[0] == '\\' || linePos[0] == '/') {
						linePos = linePos.substring(1);
					}
				}
			}

			linePos = linePos.replace(')', '');
			return linePos;
		}
	}
};


function getLogger(category) {
	if (settings) {
		var appenders = settings.appenders;
		for (var idx in appenders) {
			if (appenders[idx].type == 'console') {
				appenders[idx].layout = colorLayout;
			} else {
				appenders[idx].layout = layout;
			}
		}

		log4js.configure(settings);
	}

	if (category && typeof category == 'string') {
		return log4js.getLogger(category);
	} else {
		return log4js.getLogger('default');
	}
}

/**
 * 创建一个logger，logger标志为category
 * @param  {string} category logger的标志
 * @return {object}          logger
 */
function createLogger(category) {
	var logger = new Object;
	logger._inner = getLogger(category);

	logger.trace = function(message) {
		this._inner.trace(message);
	};
	logger.info  = function(message) {
		this._inner.info(message);
	};
	logger.warn  = function(message) {
		this._inner.warn(message);
	};
	logger.error = function(message) {
		this._inner.error(message);
	};
	logger.fatal = function(message) {
		this._inner.fatal(message);
	};

	logger.setGlobalPath = function(path) {
		basepath = path;
	};

	return logger;
}

module.exports = createLogger;
