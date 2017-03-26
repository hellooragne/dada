angular.module('starter.controllers', [])

.controller('AppCtrl', function($rootScope, $scope, $ionicModal, $timeout, $http, myweixin) {

  $scope.$on('$ionicView.enter', function(e) {

	  
  });

  $scope.loginData = {};
  $scope.registerData = {};

  $scope.result = "";	
  $scope.register_result = "";

  // Create the login modal that we will use later
  $ionicModal.fromTemplateUrl('templates/login.html', {
    scope: $scope
  }).then(function(modal) {
    $rootScope.modal = modal;
  });

  // Triggered in the login modal to close it
  $rootScope.closeLogin = function() {
    $rootScope.modal.hide();

    $rootScope.loginData = {};
    $rootScope.registerData = {};

    $rootScope.result = ""
    $rootScope.register_result = "";
  };

  $rootScope.login = function() {

	  if (myweixin.is_login() == true) {
		  $rootScope.Islogin  = 1;
		  $rootScope.user_data = myweixin.get_user_data();
	  }

	  $scope.modal.show();
  };

  if (myweixin.is_login() == true) {

	  $rootScope.Islogin  = 1;
	  $rootScope.user_data = myweixin.get_user_data();
  }

  $rootScope.doLogin = function() {

  };

  $rootScope.login_out = function() {
	  
	  myweixin.weixin_logout();

	  $rootScope.phone_id = "";
	  $rootScope.password=  "";
	  $rootScope.username = "";
	  $rootScope.picture  = "";

	  $scope.loginData = {};

	  $rootScope.Islogin  = 0;
  };


  $scope.my_bill = function() {

	  if ($rootScope.Islogin != 1) {
		$rootScope.login();
  	  } else {
		  window.location.href = "#/app/mybill";
	  }
  };
})


/*33333333333*/
.controller('PlaylistCtrl', function($rootScope, $scope, $stateParams, $timeout, $http) {

	console.log($stateParams.playlistId);

	$scope.playlist = {};

	$scope.bill = {};
	$scope.bill_join_list = {};

  	$scope.bill.group_id = 1;

	

    $scope.init_bill_show = function() {

		
		$http.post("/api/order/getone", '{"order_id":"' + $stateParams.playlistId + '"}').success(function(data) {
			console.log("order get");
			console.log(data);

			$scope.playlist = data[0];
		});
	
	};

	$scope.init_bill_join_show = function() {
	
		$http.post("/api/order_join/get", '{"order_id":"' + $stateParams.playlistId + '"}').success(function(data) {
			console.log(data);
			$scope.bill_join_list = data;
		});

	};


	$scope.init_bill_show();
	$scope.init_bill_join_show();

	$scope.bill_join = function() {

		console.log("bill join");

		if ($rootScope.Islogin != 1) {
			$rootScope.login();
		} else {

			var post_data = {
				bill_id : $stateParams.playlistId,
			};

			$http.post("/api/order_join/new", post_data).success(function(data) {
				console.log(data);
				$scope.init_bill_join_show();
			});

		}
	};


	$scope.cancel_bill = function(order_id) {

		if ($rootScope.Islogin != 1) {
			$rootScope.login();
		} else {

			var post_data = {
				order_id : order_id,
			};

			$http.post("/api/order/cancel", post_data).success(function(data) {
				console.log(data);
				$scope.init_bill_show();
			});

		}

	};

	$scope.cancel_bill_join = function(order_id) {

		if ($rootScope.Islogin != 1) {
			$rootScope.login();
		} else {

			var post_data = {
				order_join_id : order_id,
			};

			$http.post("/api/order_join/cancel", post_data).success(function(data) {
				console.log(data);
				$scope.init_bill_join_show();
			});

		}
	
	};

})

/*4444444444*/

.controller('mybill', function($rootScope, $scope, $ionicModal, $timeout, $http) {
  $scope.playlists = [
    
  ];

  $scope.bill_join = [];


  $scope.bill = {};
  $scope.bill.group_id = 1;

  $scope.bill_init = function() {
  
	  var url = encodeURI("/core/bill/get_my?group_id=" + $scope.bill.group_id) + "&phone_id=" + $rootScope.phone_id;
	  console.log(url)

	  $http.get(url).success(function(data) {
		  console.log(data);
		  $scope.playlists = data;
	  })
      .finally(function() {
		  // 停止广播ion-refresher
		  $scope.$broadcast('scroll.refreshComplete');
	  });



	  var url = encodeURI("/core/bill/get_my_join?group_id=" + $scope.bill.group_id) + "&phone_id=" + $rootScope.phone_id;
	  console.log(url)

	  $http.get(url).success(function(data) {
		  console.log(data);
		  $scope.bill_join = data;
	  })
      .finally(function() {
		  // 停止广播ion-refresher
		  $scope.$broadcast('scroll.refreshComplete');
	  });
  };

  $scope.bill_init();

  $scope.getData = function() {
  	$scope.bill_init();
  };

    // Create the login modal that we will use later
  $ionicModal.fromTemplateUrl('templates/bill_create.html', {
    scope: $scope
  }).then(function(modal) {
    $scope.modal = modal;
  });

  // Triggered in the login modal to close it
  $scope.closeBill = function() {
    $scope.modal.hide();
  };



  if ($rootScope.Islogin != 1) {
		$rootScope.login();
  }

})

//55555555555555555

.controller('tabs', function($rootScope, $scope, $ionicModal, $stateParams, $ionicTabsDelegate, $timeout, $http, myweixin) {

	myweixin.weixin_login(function(user_id) {
		$http.get("/api/fake_login?id=" + user_id).success(function(data) {
			myweixin.set_user_data(data);
		});
	});

	console.log($stateParams.pId);

	$scope.info_type  = $stateParams.pId;

	$scope.change_info_type = function(g) {
		$scope.info_type = g;
	};

	$scope.jump = function(url) {

		$rootScope.jumpurl = url;
		window.location.href = "#/app/search/1";
	};
})


.controller('blog_show', function($rootScope, $scope, $ionicModal, $stateParams, $ionicTabsDelegate, $timeout, $http, $sce, myweixin) {

  console.log($stateParams.pId);

  $scope.playlist = [];


  $scope.init_bill_show = function() {

	  $http.post("/api/blog/getone", '{"id":"' + $stateParams.pId + '"}').success(function(data) {
		  console.log("order get");
		  console.log(data);

		  $scope.playlist = data[0];

		  myweixin.set_title($scope.playlist.title);
	
		  myweixin.set_desc($scope.playlist.desc_t);

		  myweixin.set_imgurl($scope.playlist.picture);

		  $scope.playlist.picture_list = JSON.parse($scope.playlist.picture_list);
	  });

  };

  $scope.init_bill_show(); 


  $scope.jump = function(url) {

	    console.log(url);

		$rootScope.jumpurl = url;
		window.location.href = "#/app/search/1";
  };

  $scope.bill = {};

  $scope.blog_commit = function() {

	  var commit = {
		  group_id : $scope.playlist.group_id,
		  blog_id  : $stateParams.pId,
		  commit_t : $scope.bill.commit_t,
	  };
 
	  $http.post("/api/blog/addcommit", commit).success(function(data) {
  		$scope.bill = {};
  		$scope.commit_show();
	  });
  };


  $scope.commit_list = [];

  $scope.commit_show = function() {
  
	  var commit = {
		  blog_id  : $stateParams.pId,
	  };
 
	  $http.post("/api/blog/getcommit", commit).success(function(data) {
			$scope.commit_list = data;
	  });
  };

  $scope.commit_show();
})

.controller('search', function($rootScope, $scope, $ionicModal, $stateParams, $ionicTabsDelegate, $timeout, $http, $sce) {

	console.log($stateParams.pId);

	//$scope.jumpurl = $stateParams.pId;

    $scope.jumpurl = $sce.trustAsResourceUrl($rootScope.jumpurl);
})


.controller('order', function($rootScope, $scope, $stateParams, $ionicModal, $timeout, $http, myweixin) {

	console.log($stateParams.pId);
	console.log($stateParams.location);

	$scope.info_type  = "2";
	$scope.group_id = $stateParams.pId;


	$scope.$on('$ionicView.enter', function(e) {

		myweixin.set_title("萌搭搭 群聊搭友");
		myweixin.set_desc("这里有你想要的圈子和搭友，快来看看吧");
		myweixin.set_imgurl("http://app.doubilol.com/img/my.jpg");

	});

	$scope.change_info_type = function(g) {

		$scope.info_type = g;

		$scope.bill_init();
	};

	/*order*/

	$scope.bill = {};

	$scope.bill_list = [

	];

	$scope.create_result = "";
 
	$scope.bill_init = function() {

		$scope.playlists = [];

	
		$http.post("/api/order/get", '{"group_id":"' + $scope.group_id + '"}').success(function(data) {
			console.log("order get");
			console.log(data);

			$scope.bill_list = data;
		});
	};

	$scope.bill_init();
  

	$scope.getData = function() {
		$scope.bill_init();
	};

	$ionicModal.fromTemplateUrl('templates/bill_create.html', {
		scope: $scope
	}).then(function(modal) {
		$scope.modal = modal;
	});

	$scope.closeBill = function() {
		$scope.modal.hide();
	};

	$scope.create_bill = function() {

		$scope.modal.show();
	};

	$scope.create_bill_on = function() {

		console.log(Date.parse($scope.bill.start_time));
		console.log(Date.parse(Date()));

		$scope.bill.group_id = $scope.group_id;

		console.log(parseInt(Date.parse($scope.bill.start_time)) - parseInt(Date.parse(Date())));

		if ((parseInt(Date.parse($scope.bill.start_time)) - parseInt(Date.parse(Date()))) >=  (24 * 60 * 60 * 1000000 * 2)) {

			$scope.create_result = "请输入两天内时间";	
			return;
		}

		if ((parseInt(Date.parse($scope.bill.start_time)) - parseInt(Date.parse(Date()))) <=  0) {
			$scope.create_result = "请输入两天内时间";	
			return;
		}



		if ($scope.bill.group_id == undefined || $scope.bill.order_name == undefined || $scope.bill.s_from == undefined || $scope.bill.s_to == undefined || $scope.bill.seat_number == undefined) {

			$scope.create_result = "请输入全部信息";	
			return;
		}

		console.log($scope.bill.start_time);


		if ($rootScope.phone_id == null) {
			$scope.bill.phone_id = "";
		} else {
			$scope.bill.phone_id = $rootScope.phone_id;
		}


		//$scope.bill.start_time = moment($scope.bill.start_time).subtract(8, 'hour').format("YYYY-MM-DD HH:mm:ss");
		$scope.bill.start_time = moment($scope.bill.start_time).format("YYYY-MM-DD HH:mm:ss");

		$scope.bill.s_type = "driver";

		$http.post("/api/order/new", $scope.bill).success(function(data) {
			console.log(data);

			$scope.closeBill();
			$scope.bill_init();

		});
	};


	$scope.doRefresh = function() {
		$scope.bill_init();
	};
 

	/*blog*/

	$scope.blog_list = [];

	$scope.picture_list = [];


	$scope.blog = {};
	$scope.blog.group_id   = $stateParams.pId;


	$scope.create_result = "";

	$scope.blog_init = function() {

		$scope.blog_list = [];


		$http.post("/api/blog/get", '{"group_id":"' + $scope.group_id + '"}').success(function(data) {
			console.log("order get");
			console.log(data);

			$scope.blog_list = data;

			for (var i = 0; i < $scope.blog_list.length; i++) {
			
				$scope.blog_list[i].picture_list = JSON.parse($scope.blog_list[i].picture_list);
			}
		});
	};

	$scope.blog_init();


	$ionicModal.fromTemplateUrl('templates/blog_create.html', {
		scope: $scope
	}).then(function(modal) {
		$scope.blog_modal = modal;
	});

	$scope.closeblog = function() {
		$scope.blog_modal.hide();
	};


	$scope.create_blog = function() {

		$scope.blog_modal.show();
	};


	$scope.set_pic = function() {
		myweixin.set_pic(function(res) {
			$scope.picture_list =  res;
		});
	};

	$scope.blog.s_url = "";

	$scope.submit_f = function() {
		console.log("submit_f");

		var data = {
			city : "shanghai",
			group_id : $stateParams.pId,
			title :  $scope.blog.title,
			desc_t : $scope.blog.context.substring(0, 20),
			context : $scope.blog.context,
			s_url : $scope.blog.s_url,
			picture_list : JSON.stringify($scope.picture_list),
			phone_id : "" 

		};

		$http.post("/api/blog/new", data).success(function(data) {
			console.log("order get");
			console.log(data);

		});

		$scope.closeblog();
		$scope.blog_init();
	};

	$scope.BlogRefresh = function() {
		$scope.blog_init();
	};

	$scope.create_common = function() {
		if (myweixin.is_login() == false) {
		
			window.location.href = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx7f638d2d85dc480f&redirect_uri=http%3a%2f%2fapp.doubilol.com%2f&response_type=code&scope=snsapi_userinfo&state=123#wechat_redirect";
		}

		if ($scope.info_type  == "1") {
			$scope.create_bill();
		}

		if ($scope.info_type  == "2") {
			$scope.create_blog();
		}
	};


	/*chat*/

	$scope.join_chat = function() {
	
		var data = {
			group_id : $scope.group_id,
		};

		$http.post("/api/weixin_join", data).success(function(data) {

		});
	};

	$scope.exit_chat = function() {
	
		var data = {
			group_id : $scope.group_id,
		};

		$http.post("/api/weixin_exit", data).success(function(data) {

		});
	};
})
