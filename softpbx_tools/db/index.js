var softpbx_db = module.exports = require('./mongodb/db');
softpbx_db.mysql = module.exports.mysql = require('./mysql/database');
softpbx_db.mysql_pool = module.exports.mysql_pool = require('./mysql/db_pool');
