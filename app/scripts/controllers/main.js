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

    $scope.step = 1;
    $scope.loaded = false;

    var baseUrl = 'http://127.0.0.1:3044';
    $scope.question = {};

    function qInit() {
        $http({method: 'POST', url: baseUrl + '/api/initial_question'}).
            success(function(data, status, headers, config) {
                console.log("success! status: ",status,", data: ",data);
                $scope.question = data;
                $scope.loaded = true;
                // callback(data);
            }).
            error(function(data, status, headers, config) {
                console.log("error! status: ",status,", data: ",data);
                // callback(data);
            });
    }

    function questionResult(query) {
        console.log("query: ",query);
        $http({method: 'POST', url: baseUrl + '/api/question_results', data: query}).
            success(function(data, status, headers, config) {
                console.log("success! status: ",status,", data: ",data);
                $scope.result = data;
                // callback(data);
            }).
            error(function(data, status, headers, config) {
                console.log("error! status: ",status,", data: ",data);
                // callback(data);
            });
    }

    function newTag(query, tags, callback) {
        $http({method: 'POST', url: baseUrl + '/api/new_tag', data: {"query": query, "tags": tags}}).
            success(function(data, status, headers, config) {
                console.log("success! status: ",status,", data: ",data);
                callback(data);
            }).
            error(function(data, status, headers, config) {
                console.log("error! status: ",status,", data: ",data);
                // callback(data);
            });
    }

    qInit();

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

    // $scope.question = {'tag': 'genre', 'query': 'action', 'question': 'this is question 1'};

    $scope.result = [];
    $scope.oldQuery = {};

    $scope.yes = function(questions) {
        console.log("yes");
        newTag(questions.query, questions.tags, function(res) {
            questionResult(res.query);
            $scope.oldQuery = res.query;
            $scope.question = res;
            $scope.step++;
        });
        // questionResult(questions.query);
        // questionResult(questions.query);
        // addFilter(query, tag, function(data) {
        //     console.log("data: ",data);
        //     querySender(query);
        // });
        
        // $scope.question = {'query': 'drama', 'question': 'this is question 2'};
        // $scope.result = [
        //     {'title': "bla3", 'thumbnailUrl': "/images/no-image3.jpg"},
        //     {'title': "bla4", 'thumbnailUrl': "/images/no-image3.jpg"},
        //     {'title': "bla5", 'thumbnailUrl': "/images/no-image3.jpg"}
        // ];
    };
    $scope.no = function(query, tag) {
        console.log("no: ",tag);
        if ($scope.step === 1) {
            qInit();
        } else {
            console.log("old: ",$scope.oldQuery)
            questionResult($scope.oldQuery, function(res) {
                questionResult(res.query);
                $scope.question = res;
            });
        }
        // $scope.question = {'query': 'drama', 'question': 'this is question 3'};
        // $scope.result = [
        //     {'title': "bla3", 'thumbnailUrl': "/images/no-image3.jpg"},
        //     {'title': "bla4", 'thumbnailUrl': "/images/no-image3.jpg"},
        //     {'title': "bla5", 'thumbnailUrl': "/images/no-image3.jpg"}
        // ];
    };
  });
