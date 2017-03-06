angular.module('starter.services', [])

.factory('myweixin', function($http) {

	var weixin = {

		init : function() {

			var _this = this;

			_this.title = "";
			_this.desc  = "";
			_this.link  = "";
			_this.imgurl = "";
			

			$http.post("/api/weixin_config", '{"weixin_url":"' + location.href.split('#')[0] + '"}').success(function(data) {

				wx.config(data);

				wx.error(function(res){
					//alert(location.href.split('#')[0])
					console.log(res);
				});

			});

		},

		set : function() {
			var _this = this;

			wx.ready(function(){
				wx.onMenuShareAppMessage({
					title: _this.title, // 分享标题
					desc: _this.desc, // 分享描述
					link: location.href, // 分享链接
					imgUrl: _this.imgurl, // 分享图标
					type: 'link', // 分享类型,music、video或link，不填默认为link
					dataUrl: '', // 如果type是music或video，则要提供数据链接，默认为空
					success: function () { 

					},
					cancel: function () { 

					}
				});
			});
		},

	    set_desc : function(desc) {
			var _this = this;
			_this.desc = desc;
			_this.set();
		},

		set_title : function(title) {
			var _this = this;

			_this.title = title;
			_this.set();
		},

		set_imgurl : function(imgurl) {
			var _this = this;

			_this.imgurl = imgurl;
			_this.set();
		},

		set_pic : function(cb) {
			var _this = this;	

			wx.chooseImage({
				    count: 9, // 默认9
				    sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有
				    sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
				    success: function (res) {
						    var localIds = res.localIds; // 返回选定照片的本地ID列表，localId可以作为img标签的src属性显示图片
							var serverids = [];


							for (var i = 0; i < localIds.length; i++) {

								wx.uploadImage({
									localId: localIds[i], // 需要上传的图片的本地ID，由chooseImage接口获得
									isShowProgressTips: 1, // 默认为1，显示进度提示
									success: function (res) {
										var serverId = res.serverId; // 返回图片的服务器端ID
										serverids.push(serverId);

										if (serverids.length == localIds.length) {
										
											cb(serverids);
										}
									}
								});
							}
					}
			});
		}

	};

	weixin.init();

	return weixin;

});
