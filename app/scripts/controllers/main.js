'use strict';

/**
 * @ngdoc function
 * @name askVionelApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the askVionelApp
 */
angular.module('askVionelApp')
  .controller('MainCtrl', function ($scope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];

    $scope.result = [
    {'title': "bla", 'thumbnailUrl': "/images/no-image3.jpg"},
    {'title': "bla1", 'thumbnailUrl': "/images/no-image3.jpg"},
    {'title': "bla2", 'thumbnailUrl': "/images/no-image3.jpg"}
    ];

    $scope.yes = function() {
        console.log("yes");
    };
    $scope.no = function() {
        console.log("no");
    };
  });
