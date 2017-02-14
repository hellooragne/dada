var os = require('os');  
var app = require('express')()
   , server = require('http').createServer(app)
   , io = require('socket.io').listen(server)

 
var log     = require('../softpbx_tools/log/log.js')('|');

var express = require('express');
var async = require('async');
var rest = require('restler');

var system_config = require('../softpbx_tools/config/system.json');

var httpProxy = require('http-proxy'),
	proxy = httpProxy.createProxyServer({});



io.set('log level', 1); 
server.maxConnections = 100;
server.listen(80, '0.0.0.0', 1000);

app.engine('.html', require('ejs').__express);
app.set('views', __dirname + '/views');

app.use(express.static(__dirname + '/public'));
app.set('view engine', 'html');


app.all('*', function(req, res, next) {  
    res.header("Access-Control-Allow-Origin", "*");  
    res.header("Access-Control-Allow-Headers", "X-Requested-With");  
    res.header("Access-Control-Allow-Methods","PUT,POST,GET,DELETE,OPTIONS");  
    res.header("X-Powered-By",' 3.2.1')  
    res.header("Content-Type", "application/json;charset=utf-8");  
    next();
});


proxy.on('error', function (error, req, res) {
    var json;
    console.log('proxy error', error);
    if (!res.headersSent) {
        res.writeHead(500, { 'content-type': 'application/json' });
    }

    json = { error: 'proxy_error', reason: error.message };
    res.end(JSON.stringify(json));
});


app.get('/core/*', function (req, res, next) {

    try {


                proxy.proxyRequest(req, res ,{
                        target: 'http://localhost:' + system_config['aipin_core']['port'],
                        host: system_config['aipin_core']['ip'],
                        port: system_config['aipin_core']['port']

                });
        } catch(e) {
				console.log(e);

        }
});

app.get('/api/*', function (req, res, next) {

    try {


                proxy.proxyRequest(req, res ,{
                        target: 'http://localhost:' + system_config['aipin_core']['port'],
                        host: system_config['aipin_core']['ip'],
                        port: system_config['aipin_core']['port']

                });
        } catch(e) {
				console.log(e);

        }
});

app.post('/api/*', function (req, res, next) {

    try {


                proxy.proxyRequest(req, res ,{
                        target: 'http://localhost:' + system_config['aipin_core']['port'],
                        host: system_config['aipin_core']['ip'],
                        port: system_config['aipin_core']['port']

                });
        } catch(e) {
				console.log(e);

        }
});



/*
app.get('/', function (req, res) {
	res.redirect('/view/pc.html');
});

app.get('/mobile', function (req, res) {
	res.redirect('/myapp/www/');
});
*/
