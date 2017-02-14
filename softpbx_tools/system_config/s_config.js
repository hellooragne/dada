var async = require('async');
var rest = require('restler');

var log           = require('../../softpbx_tools/log/log.js')('|');
var system_config = require('../config/system.json');

var s_queue = [];

var s_config = {

    init : function() {
        
    },

    get_queue : function(callback) {
    
        rest.get('http://localhost:' + system_config['softpbx_soa']['port'] + '/softpbx_config/queue').on('complete', function(data) {
            //log.info(data);
            //var s_queue = JSON.parse(data);
            callback(data);
        });
    }

};


module.exports = s_config;
