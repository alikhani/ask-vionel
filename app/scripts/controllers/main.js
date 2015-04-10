'use strict';

/**
 * @ngdoc function
 * @name askVionelApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the askVionelApp
 */
angular.module('askVionelApp')
  .controller('MainCtrl', function ($scope, $http) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];

    console.log("bla");

    function querySender(query) {
        var q = 'tags=genre:' + query;
        var url = '/api/search?'+q+'&size=3&page=1';
        $http({method: 'GET', url: url}).
            success(function(data, status, headers, config) {
                console.log("success! status: ",status,", data: ",data);
                // callback(data);
            }).
            error(function(data, status, headers, config) {
                console.log("error! status: ",status,", data: ",data);
                // callback(data);
            });
    }

    $scope.question = {'query': 'action', 'question': 'this is question 1'};

    $scope.result = [
    {'title': "bla", 'thumbnailUrl': "/images/no-image3.jpg"},
    {'title': "bla1", 'thumbnailUrl': "/images/no-image3.jpg"},
    {'title': "bla2", 'thumbnailUrl': "/images/no-image3.jpg"}
    ];

    $scope.yes = function(query) {
        console.log("yes");
        querySender(query);
        $scope.question = {'query': 'drama', 'question': 'this is question 2'};
        $scope.result = [
            {'title': "bla3", 'thumbnailUrl': "/images/no-image3.jpg"},
            {'title': "bla4", 'thumbnailUrl': "/images/no-image3.jpg"},
            {'title': "bla5", 'thumbnailUrl': "/images/no-image3.jpg"}
        ];
    };
    $scope.no = function(query) {
        console.log("no");
        $scope.question = {'query': 'drama', 'question': 'this is question 3'};
        $scope.result = [
            {'title': "bla3", 'thumbnailUrl': "/images/no-image3.jpg"},
            {'title': "bla4", 'thumbnailUrl': "/images/no-image3.jpg"},
            {'title': "bla5", 'thumbnailUrl': "/images/no-image3.jpg"}
        ];
    };
  });
