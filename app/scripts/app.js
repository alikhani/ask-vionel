'use strict';

/**
 * @ngdoc overview
 * @name askVionelApp
 * @description
 * # askVionelApp
 *
 * Main module of the application.
 */
angular
  .module('askVionelApp', [
    'ngAnimate',
    'ngAria',
    'ngCookies',
    'ngMessages',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  })

  .factory('preload', ['$q', function($q) {
    return function(url) {
      var deffered = $q.defer(),
      image = new Image();

      image.src = url;

      if (image.complete) {

        deffered.resolve();

      } else {

        image.addEventListener('load', function() {
          deffered.resolve();
        });

        image.addEventListener('error', function() {
          deffered.reject();
        });
      }

      return deffered.promise;
    };
  }])

  .directive('background', ['preload', function(preload) {
    return {
      restrict: 'E',
      link: function(scope, element, attrs, tabsCtrl) {

        // element.hide();
        element.addClass('vl-hide');
        // console.log(attrs.url);
        preload(attrs.url).then(function(){
          // console.log('yello');
          element.css({
            "background-image": "url('" + attrs.url + "')"
          });
          element.removeClass('vl-hide');
          element.addClass('vl-show');
          // element.fadeIn();
        });
      }
    };
  }])
;