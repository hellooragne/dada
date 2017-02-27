angular.module('starter.services', [])

.factory('myweixin', function() {

	var weixin = {

		init : function() {

			var _this = this;

			_this.title = "";
			_this.desc  = "";
			_this.link  = "";
			_this.imgurl = "";


			wx.config({
				debug: true, 
				appId: 'wx7f638d2d85dc480f', 
				signature: '25e7cd39957ae919a74f04eb6b800879519be89a',
				timestamp: 1488188721, 
				nonceStr: '4kGw2IQWrgme4tm', 
				jsApiList: ['onMenuShareTimeline', 'onMenuShareAppMessage'] 
			});

			wx.error(function(res){
				alert(location.href.split('#')[0])
				console.log(res);
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
						alert('success');
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
		}

	};

	weixin.init();

	return weixin;

});
