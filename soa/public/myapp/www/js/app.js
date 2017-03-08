// Ionic Starter App

// angular.module is a global place for creating, registering and retrieving Angular modules
// 'starter' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
// 'starter.controllers' is found in controllers.js
angular.module('starter', ['ionic', 'starter.controllers', 'starter.services'])

.run(function($ionicPlatform) {
  $ionicPlatform.ready(function() {
    // Hide the accessory bar by default (remove this to show the accessory bar above the keyboard
    // for form inputs)
    if (window.cordova && window.cordova.plugins.Keyboard) {
      cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);
      cordova.plugins.Keyboard.disableScroll(true);

    }
    if (window.StatusBar) {
      // org.apache.cordova.statusbar required
      StatusBar.styleDefault();
    }
  });
})


.config(function($stateProvider, $urlRouterProvider,$ionicConfigProvider) {

  //Modify the tabs of android display position! start
  $ionicConfigProvider.platform.ios.tabs.position('top');
/*
  $ionicConfigProvider.platform.ios.tabs.style('standard');

  $ionicConfigProvider.platform.android.tabs.style('standard');
  $ionicConfigProvider.platform.android.tabs.position('top');

  $ionicConfigProvider.platform.ios.navBar.alignTitle('center');
  $ionicConfigProvider.platform.android.navBar.alignTitle('left');

  $ionicConfigProvider.platform.ios.backButton.previousTitleText('').icon('ion-ios-arrow-thin-left');
  $ionicConfigProvider.platform.android.backButton.previousTitleText('').icon('ion-android-arrow-back');

  $ionicConfigProvider.platform.ios.views.transition('ios');
  $ionicConfigProvider.platform.android.views.transition('android');
*/
})



.config(function($stateProvider, $urlRouterProvider) {
  $stateProvider

   .state('app', {
    url: '/app',
    abstract: true,
    templateUrl: 'templates/menu.html',
    controller: 'AppCtrl'
  })


  .state('app.order', {
	  url: '/order/:location/:pId',
      views: {
        'menuContent': {
          templateUrl: 'templates/order.html',
          controller: 'order'
        }
      }
    })

  .state('app.tabs', {
	  url: '/tabs/:pId',
      views: {
      'menuContent': {
        templateUrl: 'templates/tabs.html',
        controller: 'tabs'
      }
    }
  })

  .state('app.search', {
    url: '/search/:pId',
    views: {
      'menuContent': {
        templateUrl: 'templates/search.html',
        controller: 'search'
      }
    }
  })


  .state('app.blog_list', {
    url: '/blog_list/:location/:pId',
    views: {
      'menuContent': {
        templateUrl: 'templates/blog_list.html',
        controller: 'blog_list'
      }
    }
  })

 .state('app.blog_show', {
    url: '/blog_show/:pId',
    views: {
      'menuContent': {
        templateUrl: 'templates/blog_show.html',
        controller: 'blog_show'
      }
    }
  })

  .state('app.mybill', {
      url: '/mybill',
      views: {
        'menuContent': {
          templateUrl: 'templates/mybill.html',
          controller: 'mybill'
        }
      }
    })
  .state('app.playlists', {
	  url: '/playlists/:location/:pId',
      views: {
        'menuContent': {
          templateUrl: 'templates/bill.html',
          controller: 'PlaylistsCtrl'
        }
      }
    })

  .state('app.sport', {
	  url: '/sport/:location/:pId',
      views: {
        'menuContent': {
          templateUrl: 'templates/sport.html',
          controller: 'PlaylistsCtrl'
        }
      }
    })

  .state('app.single', {
    url: '/playlist/:playlistId',
    views: {
      'menuContent': {
        templateUrl: 'templates/bill_show.html',
        controller: 'PlaylistCtrl'
      }
    }
  });
  // if none of the above states are matched, use this as the fallback
  $urlRouterProvider.otherwise('/app/tabs/1');
});
