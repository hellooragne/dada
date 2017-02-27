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

	  $scope.playlists = {};
  
	  var url = encodeURI("/core/bill/get?group_id=" + $scope.bill.group_id);
	  console.log(url)

	  $http.get(url).success(function(data) {
		  console.log(data);
		  $scope.playlists = data;
	  })
	 .finally(function() {
		  // 停止广播ion-refresher
		  $scope.$broadcast('scroll.refreshComplete');
	  })


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

	/*
	var url = encodeURI("/core/bill/add?group_id=" + $scope.bill.group_id+ "&bill_name=" + $scope.bill.bill_name + "&s_from=" + $scope.bill.s_from + "&s_to=" + $scope.bill.s_to + "&seat_number=" + $scope.bill.seat_number + "&start_time=" + new Date($scope.bill.start_time) + "&s_type=driver"
		+ "&phone_id=" + $rootScope.phone_id);
	console.log(url)



	$http.get(url).success(function(data) {
		console.log(data);

		$scope.closeBill();
  	  	$scope.bill_init();
	});
	*/

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
//
.controller('tabs', function($rootScope, $scope, $ionicModal, $stateParams, $ionicTabsDelegate, $timeout, $http, myweixin) {

	/*

	wx.config({
				debug: true, 
				appId: 'wx7f638d2d85dc480f', 
				signature: '25e7cd39957ae919a74f04eb6b800879519be89a',
				timestamp: 1488188721, 
				nonceStr: '4kGw2IQWrgme4tm', 
				jsApiList: ['onMenuShareTimeline', 'onMenuShareAppMessage'] 
			});



	console.log("rest");

	wx.error(function(res){
		alert(location.href.split('#')[0])
		console.log(res);
	});

	wx.ready(function(){

		wx.onMenuShareAppMessage({
			title: 'test', // 分享标题
			desc: 'test', // 分享描述
			link: 'http://app.doubilol.com/myapp/www/#/app/tabs/1', // 分享链接
			imgUrl: '', // 分享图标
			type: 'link', // 分享类型,music、video或link，不填默认为link
			dataUrl: '', // 如果type是music或video，则要提供数据链接，默认为空
			success: function () { 
				// 用户确认分享后执行的回调函数

				alert('success');
			},
			cancel: function () { 
				// 用户取消分享后执行的回调函数
			}
		});
	});

	*/

	myweixin.set_title("test title");
	myweixin.set_desc("test new desc");

	console.log($stateParams.pId);

	/*
	console.log($ionicTabsDelegate.selectedIndex());
	*/

	$scope.$on("$ionicView.loaded", function(event, data){

		console.log("loaded");

		$ionicTabsDelegate.select(parseInt($stateParams.pId));

		console.log($ionicTabsDelegate.selectedIndex());
	});

	$scope.selectTabWithIndex = function(index) {
		$ionicTabsDelegate.select(index);
	}

	$scope.jump = function(url) {

		$rootScope.jumpurl = url;
		window.location.href = "#/app/search/1";
	};

})

.controller('search', function($rootScope, $scope, $ionicModal, $stateParams, $ionicTabsDelegate, $timeout, $http, $sce) {

	console.log($stateParams.pId);

	//$scope.jumpurl = $stateParams.pId;

    $scope.jumpurl = $sce.trustAsResourceUrl($rootScope.jumpurl);
	

})

/*sport*/

.controller('sport', function($rootScope, $scope, $ionicModal, $timeout, $http) {
  $scope.playlists = [
    
  ];


  $scope.bill = {};
  $scope.bill.group_id   = "100000001";


  $scope.create_result = "";


  $scope.change_location = function(g) {
			
  		$scope.bill.group_id = g;

  		$scope.bill_init();
  };

  $scope.bill_init = function() {

	  $scope.playlists = {};
  
	  var url = encodeURI("/core/bill/get?group_id=" + $scope.bill.group_id);
	  console.log(url)

	  $http.get(url).success(function(data) {
		  console.log(data);
		  $scope.playlists = data;
	  })
	 .finally(function() {
		  $scope.$broadcast('scroll.refreshComplete');
	  })


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

	/*
	var url = encodeURI("/core/bill/add?group_id=" + $scope.bill.group_id+ "&bill_name=" + $scope.bill.bill_name + "&s_from=" + $scope.bill.s_from + "&s_to=" + $scope.bill.s_to + "&seat_number=" + $scope.bill.seat_number + "&start_time=" + new Date($scope.bill.start_time) + "&s_type=driver"
		+ "&phone_id=" + $rootScope.phone_id);
	console.log(url)



	$http.get(url).success(function(data) {
		console.log(data);

		$scope.closeBill();
  	  	$scope.bill_init();
	});
	*/

	if ($rootScope.phone_id == null) {
		$scope.bill.phone_id = "";
	} else {
		$scope.bill.phone_id = $rootScope.phone_id;
	}

	
	$scope.bill.start_time = moment($scope.bill.start_time).subtract(8, 'hour').format("YYYY-MM-DD HH:mm:ss");

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

});
