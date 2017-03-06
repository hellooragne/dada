#curl -d '{"group_id":"1","order_name":"1", "s_from":"s", "s_to":"to", "start_time":"2016:10:31 18:00:00", "phone_id":"123", "username":"123","picture":"123","seat_number":"2","s_type":"2"}' http://localhost:8027/api/order/new  -b cookie_test 


#curl -d '{"group_id":"1"}' http://localhost/api/order/get -b cookie_test


#curl -d '{"group_id":"1"}' http://localhost/api/order/get -b cookie_test


curl http://localhost/api/fake_login?id=7bfeff73c95b43fbabdd0c098e229bcc -c cookie_test


curl -d '{"group_id":"1", "city":"shanghai", "title":"test", "desc_t":"test_desc", "context":"context_test", "picture_list":"['img/1.jjpg']", "user_id":"123", "username":"hello", "picture":"img/2.jpg", "phone_id":"123"}' http://localhost/api/blog/new -b ./cookie_test
