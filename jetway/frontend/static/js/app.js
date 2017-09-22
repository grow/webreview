var _prefix = '/_app/' + __config.ver;

var app = angular.module('jetway', [
  'ui.router',
  'ui.bootstrap',
  'jetwayFilters',
  'xeditable'
])

.config(function($stateProvider, $urlRouterProvider, $locationProvider) {
  $locationProvider.html5Mode(true);
  $stateProvider
    .state('home', {
      url: '/',
      templateUrl: _prefix + '/static/html/home.html',
      controller: HomeController
    })
    .state('new', {
      url: '/new?owner',
      controller: NewController,
      templateUrl: _prefix + '/static/html/new.html'
    })
    .state('orgs', {
      url: '/orgs',
      template: '<ui-view/>',
      abstract: true
    })
      .state('orgs.new', {
        url: '/new',
        controller: OrgNewController,
        templateUrl: _prefix + '/static/html/orgs.new.html'
      })

    .state('settings', {
      abstract: true,
      url: '/settings',
      templateUrl: _prefix + '/static/html/settings.html',
      controller: SettingsController 
    })
      .state('settings.index', {
        url: '',
        templateUrl: _prefix + '/static/html/settings.index.html'
      })
      .state('settings.accounts', {
        url: '/accounts',
        templateUrl: _prefix + '/static/html/settings.accounts.html'
      })
      .state('settings.memberships', {
        url: '/memberships',
        templateUrl: _prefix + '/static/html/settings.memberships.html'
      })
      .state('settings.org', {
        url: '/org',
        abstract: true
      })
        .state('settings.org.index', {
          url: '/:org'
        })
/*
      .state('settings.referrals', {
        url: '/referrals',
        templateUrl: _prefix + '/static/html/settings.referrals.html'
        controller: ReferralsController
      })
*/

    .state('deployments', {
      abstract: true,
      url: '/deployments',
      template: '<ui-view/>'
    })
      .state('deployments.new', {
        url: '/new?owner',
        controller: DeploymentNewController,
        templateUrl: _prefix + '/static/html/deployments.new.html'
      })
      .state('deployments.deployment', {
        url: '/:deployment',
        controller: DeploymentController,
        templateUrl: _prefix + '/static/html/deployment.html'
      })

    .state('launches', {
      url: '/launches',
      abstract: true,
      template: '<ui-view/>'
    })
      .state('launches.new', {
        url: '/new?owner&project',
        controller: LaunchNewController,
        templateUrl: _prefix + '/static/html/launches.new.html'
      })
      .state('launches.launch', {
        url: '/:launch',
        controller: LaunchController,
        templateUrl: _prefix + '/static/html/launch.html'
      })

    .state('owner', {
      abstract: true,
      url: '/:owner',
      controller: OwnerController,
      templateUrl: _prefix + '/static/html/owner.html'
    })
      .state('owner.projects', {
        url: '',
        controller: ProjectsController,
        templateUrl: _prefix + '/static/html/projects.html'
      })
      .state('owner.launches', {
        url: '/launches',
        controller: LaunchesController,
        templateUrl: _prefix + '/static/html/launches.html'
      })
      .state('owner.deployments', {
        url: '/deployments',
        controller: DeploymentsController,
        templateUrl: _prefix + '/static/html/deployments.html'
      })
      /*
      .state('owner.team', {
        url: '/teams/:team',
        controller: TeamController,
        templateUrl: _prefix + '/static/html/team.html'
      })
      */
      .state('owner.teams', {
        url: '/teams',
        controller: TeamsController,
        templateUrl: _prefix + '/static/html/teams.html'
      })
      .state('owner.settings', {
        url: '/settings',
        controller: OwnerSettingsController,
        templateUrl: _prefix + '/static/html/owner.settings.html'
      })

    .state('teams', {
      url: '/teams',
      abstract: true,
      template: '<ui-view/>'
    })
      .state('teams.new', {
        url: '/new?owner',
        controller: TeamNewController,
        templateUrl: _prefix + '/static/html/teams.new.html'
      })
      .state('teams.team', {
        url: '/:letter/:team',
        controller: TeamController,
        templateUrl: _prefix + '/static/html/team.html'
      })

    .state('project', {
      url: '/:owner/:project',
      abstract: true,
      templateUrl: _prefix + '/static/html/project.html',
      controller: ProjectController
    })
      .state('project.index', {
        url: '',
        controller: ProjectIndexController,
        templateUrl: _prefix + '/static/html/project.builds.html'
      })
      .state('project.translations', {
        abstract: true,
        url: '/translations',
        templateUrl: _prefix + '/static/html/project.translations.html'
      })
        .state('project.translations.index', {
          url: ''
        })
        .state('project.translations.locale', {
          url: '/:locale'
        })
      .state('project.team', {
        url: '/team',
        templateUrl: _prefix + '/static/html/project.team.html'
      })
      .state('project.settings', {
        url: '/settings',
        templateUrl: _prefix + '/static/html/project.settings.html'
      })

    .state('file', {
      url: '/:owner/:project/:branch/file/{file:.*}',
      controller: FileController,
      templateUrl: _prefix + '/static/html/file.html'
    })
})

.run(function($rootScope, $state, $stateParams, grow, editableOptions) {
  editableOptions.theme = 'bs3';
  $rootScope.$state = $state;
  $rootScope.$stateParams = $stateParams;
  $rootScope.grow = grow;
})

.factory('grow', function($http){
  var grow = {};
  grow.urlencode = function(obj) {
    var parts = [];
    for (var p in obj) {
     parts.push(encodeURIComponent(p) + '=' + encodeURIComponent(obj[p]));
    }
    return parts.join('&');
  };
  grow.Permission = {
    READ: 'READ',
    WRITE: 'WRITE',
    ADMINISTER: 'ADMINISTER'
  };
  grow.Status = {
    WAITING: 'waiting',
    LOADING: 'loading',
    ERROR: 'error',
    SUCCESS: 'success'
  };
  grow.rpc = function(path, body) {
    var rpcMessage = null;
    var rpcStatus = grow.Status.WAITING;
    return {
      execute: function(callback, opt_$scope) {
        rpcStatus = grow.Status.LOADING;
        var http = new XMLHttpRequest();
        http.open('POST', '/_api/' + path, true);
        http.setRequestHeader('Content-Type', 'application/json');
        http.send(JSON.stringify(body));
        http.onreadystatechange = function() {
          if (http.readyState == 4) {
            var resp = JSON.parse(http.responseText);
            if (resp['error_message']) {
              rpcStatus = grow.Status.ERROR;
              rpcMessage = resp['error_message'];
            } else {
              rpcStatus = grow.Status.SUCCESS;
              callback(resp);
            }
          }
        };
        return {
          message: function() {
            return rpcMessage;
          },
          status: function() {
            return rpcStatus;
          }
        };
      }
    };
  };
  grow.uploadAvatar = function(owner, project, $event) {
    var imageEl = $event.target;
    var fileEl = document.createElement('input');
    fileEl.type = 'file';
    fileEl.onchange = function(e) {
      var file = fileEl.files[0];
      if (!file) {
        return;
      }
      var fileReader = new FileReader();
      fileReader.onload = function(e) {
        // var md5 = CryptoJS.algo.MD5.create();
        // md5.update(fileReader.result);
        // md5.update(CryptoJS.lib.WordArray.create(fileReader.result));
        // var md5Hash = md5.finalize().toString();
        grow.rpc('avatars.create_upload_url', {
          'project': project,
          'owner': owner
          // 'headers': {
          //  'content_type': file.type,
          //  'content_length': file.size.toString()
          //  'content_md5': md5Hash 
          // }
        }).execute(function(resp) {
          //var signedRequest = resp['signed_request'];
          //var xhr = new XMLHttpRequest();
          //xhr.open('POST', resp['upload_url'], true);
          //var url = signedRequest['url'] + '?' + grow.urlencode(signedRequest['params']);
          //xhr.open(signedRequest['verb'], url, true);
          //xhr.setRequestHeader('Content-Type', signedRequest['headers']['content_type']);
          //xhr.setRequestHeader('Content-MD5', signedRequest['headers']['content_md5']);
          //xhr.setRequestHeader('Content-Length', signedRequest['headers']['content_length']);
          // xhr.send(formData);
          var parentEl = $event.target.parentNode;
          var formData = new FormData();
          formData.append('file', file);
          parentEl.className += ' spinner-loading';
          $http.post(resp['upload_url'], formData, {
            headers: {'Content-Type': undefined},
            transformRequest: function(data) { return data; }
          }).success(function(resp) {
            var base = imageEl.src.split('?')[0];
            imageEl.src = base + '?' + new Date().getTime();
            parentEl.className = parentEl.className.replace(' spinner-loading', '');
            var ident = parentEl.getAttribute('data-avatar-ident');
            var avatarEls = document.querySelectorAll('[data-avatar-ident="' + ident + '"] img');
            [].forEach.call(
              avatarEls,
              function(el) {
              if (imageEl != el) {
                el.src = imageEl.src;
              }
            });
          });
        });
      };
      fileReader.readAsText(file);
    };
    fileEl.click();
  };
  grow.signOut = function(url) {
    window.location = url;
  };
  window['grow'] = grow;
  return grow;
})

.directive('editableIf', function() {
  return {
    link: function($scope, el, attrs) {
      var editableText = attrs.editableText;
      angular.element(el).attr('editable-text', null);
      console.log(el);
    }
  };
})

.controller('HeaderController', HeaderController)
