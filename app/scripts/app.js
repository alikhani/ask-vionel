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

  .factory('Cookie', ['$location', function($location) {
  return {
    get: function(name){
      var result = document.cookie.match(new RegExp(name + '=([^;]+)'));
      if (result) {
        return JSON.parse(result[1]);
      }
    },
    set: function(name, value){
      var d = new Date();
      d.setMonth(d.getMonth() + 1);

        var cookie = name + '=' + JSON.stringify(value) + '; path=/; domain=.'+$location.host()+'; expires=' + d.toUTCString() + ';';
        console.log("cookie: ",cookie);

      document.cookie = cookie;
    },
    delete: function(name){
      document.cookie = name+ '=; path=/; domain=.'+$location.host()+'; expires=Thu, 01-Jan-1970 00:00:01 GMT;';
    }
  };
}])

  .factory('principal', ['$q', '$http', '$timeout', 'Cookie', 
  function($q, $http, $timeout, Cookie) {
    var _identity;
    var _authenticated = false;

    return {
      isIdentityResolved: function() {
        return angular.isDefined(_identity);
      },
      isAuthenticated: function() {
        return _authenticated;
      },
      getSessiontoken: function() {
        var _sessionToken = Cookie.get("user");
        return _sessionToken;
      },
      isInRole: function(role) {
        if (!_authenticated || !_identity.roles){ return false; }

        return _identity.roles.indexOf(role) !== -1;
      },
      isInAnyRole: function(roles) {
        if (!_authenticated || !_identity.roles) { return false; }

        for (var i = 0; i < roles.length; i++) {
          if (this.isInRole(roles[i])) { return true; }
        }

        return false;
      },
      isCookiesAccepted: function() {
        return Cookie.get("cookieacceptance");
      },
      acceptCookies: function() {
        Cookie.set("cookieacceptance", true);
      },
      getUser: function() {
        return _identity;
      },
      authenticate: function(identity) {
        _identity = identity;
        _authenticated = identity !== null;

        if (identity) {
          console.log("set user: ",identity);
          Cookie.set("user",angular.toJson(identity));
          localStorage.setItem("user.identity", angular.toJson(identity)); 
        } else {
          console.log("delete");
          Cookie.delete("user");
          localStorage.removeItem("user.identity");
          _authenticated = false;
          // Cookie.delete("sessionToken");
          // localStorage.removeItem("user.identity");
        }
      },
      userImage: function(type, image) {
        if (type === 'SET') {
          localStorage.setItem("user.portrait", angular.toJson(image));
        } else {
          if (localStorage.getItem("user.portrait") !== 'undefined') {
            return angular.fromJson(localStorage.getItem("user.portrait"));
          }
          
        }
      },
      authenticateTempUser: function(callback) {
        // console.log("temp auth");


        $http({method: 'post', url: 'http://127.0.0.1:3044/api/temp_auth'}).
        success(function(data, status, headers, config) {
          // console.log("success! status: ",status,", data: ",data);
                var user = {
                    "userToken": data.response.userToken,
                    "sessionToken": data.response.sessionToken,
                    "isTemp": true
                };
          Cookie.set("user", angular.toJson(user));
          localStorage.setItem("user.identity", angular.toJson(user)); 
          console.log("u: ",user);
          callback(user);
        });
      },
      identity: function(force) {
        var deferred = $q.defer();

        if (force === true) {
          _identity = undefined;
        }

        // check and see if we have retrieved the identity data from the server. if we have, reuse it by immediately resolving
        if (angular.isDefined(_identity)) {
          deferred.resolve(_identity);

          return deferred.promise;
        }

        var self = this;

_identity = angular.fromJson(localStorage.getItem("user.identity"));
self.authenticate(_identity);
deferred.resolve(_identity);

return deferred.promise;
}
};
}
])

  .factory('authorization', ['$rootScope', 'principal',
  function($rootScope, principal) {
    return {
      authorize: function() {
        return principal.identity()
        .then(function() {
          // console.log("auth-state: ",$state);
          var isAuthenticated = principal.isAuthenticated();
          var user = principal.getUser();

          console.log("auth: ",isAuthenticated,", user: ",user);

          if(isAuthenticated || user) {
            console.log("there is a user");
          } else {
            console.log("not auth");
            principal.authenticateTempUser( function(resp) {
              console.log("callback: ",resp);
              principal.authenticate(resp);
              // $state.transitionTo($state.current, $stateParams, {
              //   reload: true,
              //   inherit: false,
              //   notify: true
              // });
            });
          }
          });
      }
    };
  }
  ])

  .factory('sessionInjector', ['$q','$injector', '$rootScope', 'Cookie', function($q, $injector) {
    var user;
    var sessionInjector = {
        request: function(config) {
          var canceler = $q.defer();
          var p = $injector.get('principal');
          console.log("bla");
          user = p.getUser();
          console.log("user: ",user);
          // console.log("getUser: ",user,", id: ",p.isIdentityResolved(),", root: ",$rootScope.user,", cookie: ",Cookie.get("user"));
          if (user) {
            // config.headers['X-Session-Token'] = user.sessionToken;
            console.log("head: ",config);
          } else {

            // if(config.url !== "/api/temp_auth") {
            //   config.timeout = canceler.promise;
            //   canceler.resolve();
            // }

          }
          return config || $q.when(config);
        }
    };
    return sessionInjector;
  }])

  .config(function ($routeProvider, $httpProvider) {

    $httpProvider.interceptors.push('sessionInjector');

    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl',
        resolve: {
          authorize: ['authorization',
          function(authorization) {
            return authorization.authorize();
          }
          ]
        }
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
      link: function(scope, element, attrs) {

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