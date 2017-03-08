angular.module('starter.controllers', [])

.controller('AppCtrl', function($rootScope, $scope, $ionicModal, $timeout, $http) {

  // With the new view caching in Ionic, Controllers are only called
  // when they are recreated or on app start, instead of every page change.
  // To listen for when this page is active (for example, to refresh data),
  // listen for the $ionicView.enter event:
  //$scope.$on('$ionicView.enter', function(e) {
  //});

  // Form data for the login modal
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

  // Open the login modal
  $rootScope.login = function() {
    $scope.modal.show();
  };

  // Perform the login action when the user submits the login form
  $rootScope.doLogin = function() {
    console.log('Doing login', $scope.loginData);

    // Simulate a login delay. Remove this and replace with your login
    // code if using a login system
	/*
    $timeout(function() {
      $scope.closeLogin();
    }, 1000);
	*/

	/*
	var url = encodeURI("/core/user/login?phone_id=" + $scope.loginData.phone_id + "&password=" + $scope.loginData.password);
	console.log(url)

	$http.get(url).success(function(data) {
		console.log(data[0].is_match);

		if (data[0].is_match == 1) {

			$rootScope.phone_id = $scope.loginData.phone_id;
			$rootScope.password=  $scope.loginData.password;
			$rootScope.username = data[0].username;
			$rootScope.picture  = data[0].picture;
			$rootScope.Islogin  = 1;


      		$scope.closeLogin();

			console.log($rootScope.phone_id);
		} else {
			$scope.result = "用户名或密码错误";	
		}
	});
	*/

	
  };

  $rootScope.login_out = function() {

	  $rootScope.phone_id = "";
	  $rootScope.password=  "";
	  $rootScope.username = "";
	  $rootScope.picture  = "";

	  $scope.loginData = {};

	  $rootScope.Islogin  = 0;
  };



  $rootScope.doRegister = function() {

	console.log($scope.registerData.sex);
	var picture_id = 0;
	var myDate = new Date();

	if ($scope.registerData.sex == 'male') {

		picture_id = parseInt(myDate.getMilliseconds())%10; 
	} else {
	
		$scope.registerData.sex = 'female';

		picture_id = parseInt(myDate.getMilliseconds())%10 + 10000; 
	}
  
	if ($scope.registerData.phone_id == ""  || $scope.registerData.phone_id.length != 11) {
	
		$scope.register_result = "请输入正确的手机号码";	
		return;
	}

	if ($scope.registerData.password == "") {
	
		$scope.register_result = "请输入正确的密码";	
		return;
	}

	/*
	var url = encodeURI("/core/user/add?phone_id=" + $scope.registerData.phone_id + "&password=" + $scope.registerData.password 
		+ "&username=" + $scope.registerData.username + "&picture=img/" + picture_id + ".jpg" + "&sex=" + $scope.registerData.sex);
	console.log(url)

	$http.get(url).success(function(data) {
		console.log(data);

		if (data.affectedRows == 1) {

			$rootScope.phone_id = $scope.registerData.phone_id;
			$rootScope.password = $scope.registerData.password;
			$rootScope.username = $scope.registerData.username;
			$rootScope.picture  = "img/" + picture_id + ".jpg";
			$rootScope.Islogin  = 1;

      		$scope.closeLogin();
		} else {
			$scope.register_result = "用户名重复注册";	
		}
	});
	*/
  };



  $scope.my_bill = function() {

	  if ($rootScope.Islogin != 1) {
		$rootScope.login();
  	  } else {
		  window.location.href = "#/app/mybill";
	  }
  };
})


/*222222222222*/

.controller('PlaylistsCtrl', function($rootScope, $scope, $stateParams, $ionicModal, $timeout, $http) {

  console.log($stateParams.pId);
  console.log($stateParams.location);

  $scope.playlists = [
    
  ];


  $scope.bill = {};
  $scope.bill.group_id   = $stateParams.pId;


  $scope.create_result = "";


  $scope.change_location = function(g) {
			
  		$scope.bill.group_id = g;

  		$scope.bill_init();
  };

  $scope.bill_init = function() {

	  $scope.playlists = [];
  

	 $http.get("/api/fake_login?id=7bfeff73c95b43fbabdd0c098e229bcc").success(function(data) {
	 	console.log("fake login");
		console.log(data);

		$rootScope.user_id = "7bfeff73c95b43fbabdd0c098e229bcc";
	  	$rootScope.Islogin  = 1;
  	});


	$http.post("/api/order/get", '{"group_id":"' + $scope.bill.group_id + '"}').success(function(data) {
	 	console.log("order get");
		console.log(data);

		$scope.playlists = data;
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

  /*
  $scope.login = function() {
    $scope.modal.show();
  };
  */

  $scope.create_bill = function() {

	$scope.modal.show();
	/*
	if ($rootScope.Islogin != 1) {
		$rootScope.login();
	} else {
	
		$scope.modal.show();
	}
	*/
  };

  $scope.create_bill_on = function() {

	/*
    $timeout(function() {
      $scope.closeBill();
  	  $scope.bill_init();
    }, 2000);
	*/

	console.log(Date.parse($scope.bill.start_time));
	console.log(Date.parse(Date()));

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


	console.log($stateParams.pId);

	$scope.info_type  = "1";

	$scope.change_info_type = function(g) {
		$scope.info_type = g;
	};

	$scope.jump = function(url) {

		$rootScope.jumpurl = url;
		window.location.href = "#/app/search/1";
	};

})

.controller('blog_list', function($rootScope, $scope, $ionicModal, $stateParams, $ionicTabsDelegate, $timeout, $http, $sce, myweixin) {

  console.log($stateParams.pId);
  console.log($stateParams.location);

  $scope.playlists = [
    
  ];

  $scope.picture_list = [];


  $scope.bill = {};
  $scope.bill.group_id   = $stateParams.pId;


  $scope.create_result = "";


  $scope.change_location = function(g) {
			
  		$scope.bill.group_id = g;

  		$scope.bill_init();
  };

  $scope.bill_init = function() {

	 $scope.playlists = [];
  

	 $http.get("/api/fake_login?id=7bfeff73c95b43fbabdd0c098e229bcc").success(function(data) {
	 	console.log("fake login");
		console.log(data);

		$rootScope.user_id = "7bfeff73c95b43fbabdd0c098e229bcc";
	  	$rootScope.Islogin  = 1;
  	});


	$http.post("/api/blog/get", '{"group_id":"' + $scope.bill.group_id + '"}').success(function(data) {
	 	console.log("order get");
		console.log(data);

		$scope.playlists = data;
  	});
  };

  $scope.bill_init();


  $ionicModal.fromTemplateUrl('templates/blog_create.html', {
    scope: $scope
  }).then(function(modal) {
    $scope.modal = modal;
  });

  // Triggered in the login modal to close it
  $scope.closeBill = function() {
    $scope.modal.hide();
  };

  /*
  $scope.login = function() {
    $scope.modal.show();
  };
  */

  $scope.create_bill = function() {

	$scope.modal.show();
  };


  $scope.set_pic = function() {
	  myweixin.set_pic(function(res) {
	  	$scope.picture_list =  res;
		alert("get res");
		alert($scope.picture_list);
	  });
  };

  $scope.submit_f = function() {
	  console.log("submit_f");
  
	  var data = {
	 	city : "shanghai",
		group_id : $stateParams.pId,
		title :  $scope.bill.title,
		desc_t : $scope.bill.context,
		context : $scope.bill.context,
		picture_list : JSON.stringify($scope.picture_list),
		phone_id : "123456789" 

	  };

	  $http.post("/api/blog/new", data).success(function(data) {
	 	console.log("order get");
		console.log(data);

  	  });
  };
  
})

.controller('blog_show', function($rootScope, $scope, $ionicModal, $stateParams, $ionicTabsDelegate, $timeout, $http, $sce, myweixin) {

  console.log($stateParams.pId);

  $scope.playlist = {};

  $scope.bill = {};
  $scope.bill_join_list = {};

  $scope.bill.group_id = 1;



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
  
})

.controller('search', function($rootScope, $scope, $ionicModal, $stateParams, $ionicTabsDelegate, $timeout, $http, $sce) {

	console.log($stateParams.pId);

	//$scope.jumpurl = $stateParams.pId;

    $scope.jumpurl = $sce.trustAsResourceUrl($rootScope.jumpurl);
	

})


.controller('order', function($rootScope, $scope, $stateParams, $ionicModal, $timeout, $http, myweixin) {

	console.log($stateParams.pId);
	console.log($stateParams.location);

	$scope.info_type  = "1";
	$scope.group_id = $stateParams.pId;

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

		$http.get("/api/fake_login?id=7bfeff73c95b43fbabdd0c098e229bcc").success(function(data) {
			console.log("fake login");
			console.log(data);

			$rootScope.user_id = "7bfeff73c95b43fbabdd0c098e229bcc";
			$rootScope.Islogin  = 1;
		});


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


		$http.get("/api/fake_login?id=7bfeff73c95b43fbabdd0c098e229bcc").success(function(data) {
			console.log("fake login");
			console.log(data);

			$rootScope.user_id = "7bfeff73c95b43fbabdd0c098e229bcc";
			$rootScope.Islogin  = 1;
		});


		$http.post("/api/blog/get", '{"group_id":"' + $scope.group_id + '"}').success(function(data) {
			console.log("order get");
			console.log(data);

			$scope.blog_list = data;
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

	$scope.submit_f = function() {
		console.log("submit_f");

		var data = {
			city : "shanghai",
			group_id : $stateParams.pId,
			title :  $scope.blog.title,
			desc_t : $scope.blog.context,
			context : $scope.blog.context,
			picture_list : JSON.stringify($scope.picture_list),
			phone_id : "123456789" 

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
		if ($scope.info_type  == "1") {
			$scope.create_bill();
		}

		if ($scope.info_type  == "2") {
			$scope.create_blog();
		}
	};
})
