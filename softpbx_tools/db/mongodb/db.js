var db_url   = 'mongodb://pub.mongo.db.dev.sh.ctripcorp.com:28747/softpbxDatadb';

var MongoClient = require('mongodb').MongoClient
    , format = require('util').format;

var collection = {};
collection['bson'] = require('mongodb').BSONPure;

/*
MongoClient.connect(db_url, {wtimeout:200}, function(err, db) {
	collection['softpbx_event']         = db.collection('softpbx_event');
	collection['softpbx_call_list']     = db.collection('softpbx_call_list');
	collection['softpbx_abandon_list']  = db.collection('softpbx_abandon_list');
	collection['callin_statistics']  = db.collection('callin_statistics');
	collection['callout_statistics']  = db.collection('callout_statistics');
	collection['call_state']  = db.collection('call_state');
});
*/



module.exports = collection;
