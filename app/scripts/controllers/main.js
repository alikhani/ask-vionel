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

    $scope.searchQuery = "";

    console.log("bla");

    function querySender(query) {
        var q = 'tags=genre:' + query;
        var url = 'http://127.0.0.1:3044/api/search?'+q+'&size=3&page=1';
        $http({method: 'get', url: url}).
            success(function(data, status, headers, config) {
                console.log("success! status: ",status,", data: ",data);
                // callback(data);
            }).
            error(function(data, status, headers, config) {
                console.log("error! status: ",status,", data: ",data);
                // callback(data);
            });
    }

    function addFilter(filter, tag, callback) {
      var newQuery;
      var regTag = /tags=(.*?)(?=&|$)/;
      var tags = regTag.exec($scope.searchQuery);
      var f = angular.lowercase(filter);

      if (tags && tags.length>0) {
        var tagBla = new RegExp(tag+'(.*?)(?=\\||$)');
        var genres = tagBla.exec(angular.lowercase(tags[1]));
        // console.log("tags:12 ",tags);
        if(genres) {
          if(genres[0].indexOf(angular.lowercase(f)) > 0) {
            return;
          }
          // console.log("tags: ",tags);
          newQuery = $scope.searchQuery.replace(tags[0], '$&,'+f);
        } else {
          newQuery = $scope.searchQuery.replace(tags[0], '$&'+'|'+tag+':'+f);
        }

      } else {
        newQuery = $scope.searchQuery+'tags='+tag+':'+f;
      }

      if(newQuery) {
        callback(newQuery);
      }
    }

    $scope.question = {'tag': 'genre', 'query': 'action', 'question': 'this is question 1'};

    $scope.result = [
    {'title': "bla", 'thumbnailUrl': "/images/no-image3.jpg"},
    {'title': "bla1", 'thumbnailUrl': "/images/no-image3.jpg"},
    {'title': "bla2", 'thumbnailUrl': "/images/no-image3.jpg"}
    ];

    $scope.yes = function(query, tag) {
        console.log("yes");
        addFilter(query, tag, function(data) {
            console.log("data: ",data);
            querySender(query);
        });
        
        $scope.question = {'query': 'drama', 'question': 'this is question 2'};
        $scope.result = [
            {'title': "bla3", 'thumbnailUrl': "/images/no-image3.jpg"},
            {'title': "bla4", 'thumbnailUrl': "/images/no-image3.jpg"},
            {'title': "bla5", 'thumbnailUrl': "/images/no-image3.jpg"}
        ];
    };
    $scope.no = function(query, tag) {
        console.log("no: ",tag);
        $scope.question = {'query': 'drama', 'question': 'this is question 3'};
        $scope.result = [
            {'title': "bla3", 'thumbnailUrl': "/images/no-image3.jpg"},
            {'title': "bla4", 'thumbnailUrl': "/images/no-image3.jpg"},
            {'title': "bla5", 'thumbnailUrl': "/images/no-image3.jpg"}
        ];
    };
  });
