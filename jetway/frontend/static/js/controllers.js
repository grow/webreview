var HeaderController = function($scope, $rootScope, grow) {
  grow.rpc('me.get').execute(function(resp) {
    $rootScope.me = resp['me'];
    $scope.$apply();
  });
  grow.rpc('me.search_orgs').execute(function(resp) {
    $rootScope.orgs = resp['orgs'];
    $rootScope.$apply();
  });
};


var HomeController = function($scope, $rootScope) {
  $rootScope.$watch('me', function() {
    if ($rootScope.me) {
      grow.rpc('me.search_projects').execute(function(resp) {
        $scope.projects = resp['projects'];
        $scope.$apply();
      });
    }
  });
};


var ExploreController = function($scope) {
  $scope.rpc = grow.rpc('projects.search').execute(function(resp) {
    $scope.projects = resp['projects'];
    $scope.$apply();
  });
};


var ProjectsController = function($scope, $stateParams, $rootScope, $http, grow) {
  var owner = {'nickname': $stateParams['owner']};

  $scope.rpcs.owner = grow.rpc('owners.get', {'owner': owner}).execute(function(resp) {
    $scope.owner = resp['owner'];
    $scope.$apply();
  });

  $scope.rpc = grow.rpc('projects.search', {
    'project': {'owner': owner}
  }).execute(function(resp) {
    $scope.projects = resp['projects'];
    $scope.$apply();
  });
};


var OwnerController = function($scope, $stateParams, $rootScope, $http, grow) {
  $scope.rpcs = {};
  $scope.ownerName = $stateParams['owner'];
  var owner = {'nickname': $scope.ownerName};

  $scope.rpcs.owner = grow.rpc('owners.get', {'owner': owner}).execute(function(resp) {
    $scope.owner = resp['owner'];
    $scope.$apply();
    if (resp['owner']['kind'] == 'ORG') {
      loadOrg(resp['owner']);
    } else {
      loadUser(resp['owner']);
    }
  });

  $scope.updateOwner = function(owner) {
    grow.rpc('owners.update', {'owner': owner}).execute(function(resp) {
      $scope.owner = resp['owner'];
    }, $scope);
  };

  var loadOrg = function(org) {
    grow.rpc('orgs.search_members', {'org': org}).execute(function(resp) {
      $scope.users = resp['users'];
      $scope.$apply();
    });
  };

  var loadUser = function(user) {
    grow.rpc('users.search_orgs', {'user': user}).execute(function(resp) {
      $scope.orgs = resp['orgs'];
      $scope.$apply();
    });
  };
};


var ProjectController = function($scope, $stateParams, $state, $rootScope, grow) {
  $scope.rpcs = {};
  var project = {
    'owner': {'nickname': $stateParams['owner']},
    'nickname': $stateParams['project']
  };

  var setWatchingStatus = function(watchers) {
    var me = $rootScope.me;
    $scope.watching = false;
    watchers.forEach(function(watcher) {
      if (watcher['user']['ident'] == me['ident']) {
        $scope.watching = true;
      }
    });
  };

  $scope.unwatch = function(project) {
    grow.rpc('projects.unwatch', {
      'project': project
    }).execute(function(resp) {
      $scope.watchers = resp['watchers'];
      $scope.watching = false;
      $scope.$apply();
    });
  };

  $scope.watch = function(project) {
    grow.rpc('projects.watch', {
      'project': project
    }).execute(function(resp) {
      $scope.watchers = resp['watchers'];
      $scope.watching = true;
      $scope.$apply();
    });
  };

  $scope.rpcs.watchers = grow.rpc('projects.list_watchers', {
    'project': project
  }).execute(function(resp) {
    $scope.watchers = resp['watchers'];
    setWatchingStatus($scope.watchers);
    $scope.$apply();
  });

  $scope.rpcs.project = grow.rpc('projects.get', {
    'project': project
  }).execute(function(resp) {
    $scope.project = resp['project'];
    $scope.$apply();
  });

  $scope.updateProject = function(project) {
    grow.rpc('projects.update', {'project': project}).execute(function(resp) {
      $scope.project = resp['project'];
      $scope.$apply();
    });
  };

  $scope.setVisibility = function(visibility) {
    var p = project;
    p['visibility'] = visibility;
    $scope.updateProject(project);
  };

  grow.rpc('filesets.search', {
    'fileset': {
      'project': project
    }
  }).execute(function(resp) {
    $scope.filesets = resp['filesets'];
    $scope.$apply();
  });

  // Project team.

  $scope.membership = {
    'role': 'READ_ONLY'
  };
  var team = null;

  $scope.$watch('project', function() {
    var project = $scope.project;
    if (project && project['ident']) {
      team = {'kind': 'PROJECT_OWNERS', 'ident': project['ident']};
      grow.rpc('teams.get', {
        'team': team 
      }).execute(function(resp) {
        $scope.team = resp['team'];
        $scope.$apply();
      });
    }
  });

  $scope.updateMembership = function(membership) {
    grow.rpc('teams.update_membership', {
      'team': team,
      'membership': membership 
    }).execute(function(resp) {
      $scope.$apply();
    });
  };

  $scope.createMembership = function(membership) {
    grow.rpc('teams.create_membership', {
      'team': team,
      'membership': membership 
    }).execute(function(resp) {
      $scope.team = resp['team'];
      $scope.$apply();
    });
  };

  $scope.deleteMembership = function(membership) {
    grow.rpc('teams.delete_membership', {
      'team': team,
      'membership': membership 
    }).execute(function(resp) {
      $scope.team = resp['team'];
      $scope.$apply();
    });
  };

  // Delete.
  $scope.deleteProject = function(project) {
    grow.rpc('projects.delete', {'project': project}).execute(function(resp) {
      $state.go('owner.projects', {'owner': project['owner']['nickname']});
      $scope.$apply();
    });
  };
};


var WorkspacesController = function($scope, $stateParams, $state, grow) {
  var project = {
    'owner': {'nickname': $stateParams['owner']},
    'nickname': $stateParams['project']
  };
  $scope.project = project;
  $scope.rpc = grow.rpc('filesets.search', {
    'fileset': {
      'project': project
    }
  }).execute(function(resp) {
    $scope.filesets = resp['filesets'];
    $scope.$apply();
  });
};


var ProjectIndexController = function($scope, $stateParams, $state, grow) {
  var project = {
    'owner': {'nickname': $stateParams['owner']},
    'nickname': $stateParams['project']
  };
  grow.rpc('users.search', {
    'project': project
  }).execute(function(resp) {
    $scope.users = resp['users'];
    $scope.$apply();
  });
};


var NewController = function($scope, $state, $rootScope, grow) {
  $scope.owners = [];
  $rootScope.$watch('me', function() {
    if ($rootScope.me) {
      grow.rpc('users.search_orgs', {
        'user': $rootScope.me
      }).execute(function(resp) {
        if (resp['orgs']) {
          resp['orgs'].forEach(function(org) {
            $scope.owners.push(org['nickname']);
          });
        }
        $scope.owners.unshift($rootScope.me.nickname);
        $scope.project = {'owner': {'nickname': $rootScope.me.nickname}};
        $scope.$apply();
      });
    }
  });

  $scope.createProject = function(project) {
    grow.rpc('projects.create', {'project': project}).execute(
        function(resp) {
      $state.go('project.index', {
        'owner': project.owner.nickname,
        'project': resp['project']['nickname']
      });
      $scope.$apply();
    });
  };
};


var OrgNewController = function($scope, $state, grow) {
  $scope.createOrg = function(org) {
    grow.rpc('orgs.create', {'org': org}).execute(function(resp) {
      $state.go('owner.projects', {'owner': org['nickname']});
      $scope.$apply();
    });
  };
};


var SettingsController = function($scope, grow) {
  $scope.regenerateGitPassword = function() {
    grow.rpc('me.regenerate_git_password').execute(function(resp) {
      $scope.git_password = resp['git_password'];
      $scope.$apply();
    });
  };
  $scope.updateMe = function(me) {
    grow.rpc('me.update', {'me': me}).execute(function(resp) {
      $scope.me = resp['me'];
      $scope.$apply();
    });
  };
};


var TeamsController = function($scope, $stateParams, $state, grow) {
  var team = {
    'owner': {'nickname': $stateParams['owner']}
  };
  if ($stateParams['project']) {
    team['projects'] = [{'nickname': $stateParams['project']}];
  }
  $scope.rpc = grow.rpc('teams.search', {
    'team': team 
  }).execute(function(resp) {
    $scope.teams = resp['teams'];
    $scope.$apply();
  });
};


var TeamController = function($scope, $stateParams, $state, grow) {
  $scope.rpcs = {};

  var kind = 'DEFAULT';
  switch ($stateParams['letter']) {
    case 'o':
      kind = 'ORG_OWNERS';
      break;
    case 'p':
      kind = 'PROJECT_OWNERS';
      break;
  }
  var team = {'ident': $stateParams['team'], 'kind': kind};

  $scope.rpcs.teams = grow.rpc('teams.get', {
    'team': team 
  }).execute(function(resp) {
    $scope.team = resp['team'];
    $scope.$apply();
  });

  $scope.createMembership = function(membership) {
    grow.rpc('teams.create_membership', {
      'team': team,
      'membership': membership 
    }).execute(function(resp) {
      $scope.team = resp['team'];
      $scope.$apply();
    });
  };

  $scope.deleteMembership = function(membership) {
    grow.rpc('teams.delete_membership', {
      'team': team,
      'membership': membership 
    }).execute(function(resp) {
      $scope.team = resp['team'];
      $scope.$apply();
    });
  };

  $scope.addProject = function(project) {
    grow.rpc('teams.add_project', {
      'team': team,
      'project': project
    }).execute(function(resp) {
      $scope.team = resp['team'];
      $scope.$apply();
    });
  };

  $scope.removeProject = function(project) {
    project['owner'] = owner;
    grow.rpc('teams.remove_project', {
      'team': team,
      'project': project
    }).execute(function(resp) {
      $scope.team = resp['team'];
      $scope.$apply();
    });
  };

  $scope.updateTeam = function(team) {
    grow.rpc('teams.update', {
      'team': team
    }).execute(function(resp) {
      $scope.team = resp['team'];
    });
  };

  $scope.deleteTeam = function(team) {
    grow.rpc('teams.delete', {
      'team': team
    }).execute(function(resp) {
      $state.go('owner.teams', {'owner': team['owner']['nickname']});
      $scope.$apply();
    });
  };
};


var FileController = function($scope, $stateParams, grow) {
  grow.rpc('filesets.get_pagespeed_result', {
    'fileset': {
      'name': $stateParams['branch'],
      'project': {
        'owner': {'nickname': $stateParams['owner']},
        'nickname': $stateParams['project']
      }
    },
    'file': {'path': '/' + $stateParams['file']}
  }).execute(function(resp) {
    $scope.pagespeed_result = resp['pagespeed_result'];
    $scope.$apply();
  });
};


var TeamNewController = function($scope, $stateParams, $state, grow) {
  $scope.team = {
    'owner': {'nickname': $stateParams['owner']}
  };
  $scope.createTeam = function(team) {
    grow.rpc('teams.create', {'team': team}).execute(function(resp) {
      $state.go('teams.team', {
        'letter': resp['team']['letter'],
        'team': resp['team']['ident']
      });
      $scope.$apply();
    });
  };
};


var LaunchesController = function($scope, $stateParams, grow) {
  var owner = {'nickname': $stateParams['owner']};
  $scope.rpc = grow.rpc('launches.search', {
    'launch': {
      'project': {
        'owner': owner,
        'nickname': $stateParams['project']
      }
    }
  }).execute(function(resp) {
    $scope.launches = resp['launches'];
    $scope.$apply();
  });
};


var LaunchController = function($scope, $stateParams, grow) {
  $scope.comments = [];

  grow.rpc('comments.search', {
    'comment': {
      'parent': {'ident': $stateParams['launch']},
      'kind': 'LAUNCH'
    }
  }).execute(function(resp) {
    $scope.comments = resp['comments'];
    $scope.$apply();
  });

  grow.rpc('launches.get', {
    'launch': {
      'ident': $stateParams['launch']
    }
  }).execute(function(resp) {
    $scope.launch = resp['launch'];

    grow.rpc('filesets.search', {
      'fileset': {
        'project': resp['launch']['project']
      }
    }).execute(function(resp) {
      if ($scope.launch['fileset']) {
        resp['filesets'].forEach(function(fileset) {
          if ($scope.launch['fileset']['ident'] == fileset['ident']) {
            $scope.launch['fileset'] = fileset;
          }
        });
      }
      $scope.filesets = resp['filesets'];
      $scope.$apply();
    });

    grow.rpc('deployments.search', {
      'deployment': {
        'owner': resp['launch']['project']['owner']
      }
    }).execute(function(resp) {
      if ($scope.launch['deployment']) {
        resp['deployments'].forEach(function(deployment) {
          if ($scope.launch['deployment']['ident'] == deployment['ident']) {
            $scope.launch['deployment'] = deployment;
          }
        });
      }
      $scope.deployments = resp['deployments'];
      $scope.$apply();
    });

    $scope.$apply();
  });

  $scope.deleteApproval = function(launch) {
    grow.rpc('launches.delete_approval', {
      'launch': launch
    }).execute(function(resp) {
      $scope.launch = resp['launch'];
      $scope.$apply();
    });
  };

  $scope.createApproval = function(launch) {
    grow.rpc('launches.create_approval', {
      'launch': launch
    }).execute(function(resp) {
      $scope.launch = resp['launch'];
      $scope.$apply();
    });
  };

  $scope.updateLaunch = function(launch) {
    grow.rpc('launches.update', {
      'launch': launch
    }).execute(function(resp) {
      $scope.$apply();
    });
  };

  $scope.deleteComment = function(comment) {
    grow.rpc('comments.delete', {'comment': comment}).execute(
        function(resp) {
      $scope.comments = $scope.comments.filter(function(c) {
        return c['ident'] != comment['ident']; 
      });
      $scope.$apply();
    });
  };

  $scope.createComment = function(comment) {
    comment['parent'] = {'ident': $stateParams['launch']};
    comment['kind'] = 'LAUNCH';
    grow.rpc('comments.create', {'comment': comment}).execute(
        function(resp) {
      $scope.comments.push(resp['comment']);
      $scope.$apply();
    });
  };
};


var LaunchNewController = function($scope, $state, $stateParams, grow) {
  $scope.launch = {
    'project': {
      'owner': {'nickname': $stateParams['owner']},
      'nickname': $stateParams['project']
    }
  };
  $scope.createLaunch = function(launch) {
    grow.rpc('launches.create', {
      'launch': launch
    }).execute(function(resp) {
      $state.go('launches.launch', {'launch': resp['launch']['ident']});
      $scope.$apply();
    });
  };
};


var DeploymentsController = function($scope, $state, $stateParams, grow) {
  var owner = {'nickname': $stateParams['owner']};
  $scope.rpc = grow.rpc('deployments.search', {
    'deployment': {
      'owner': owner
    }
  }).execute(function(resp) {
    $scope.deployments = resp['deployments'];
    $scope.$apply();
  });
};


var DeploymentController = function($scope, $state, $stateParams, grow) {
  $scope.rpc = grow.rpc('deployments.get', {
    'deployment': {'ident': $stateParams['deployment']}
  }).execute(
      function(resp) {
    $scope.deployment = resp['deployment'];
    $scope.$apply();
  });

  $scope.updateDeployment = function(deployment) {
    console.log(deployment);
    grow.rpc('deployments.update', {
      'deployment': deployment
    }).execute(function(resp) {
      $scope.deployment = resp['deployment'];
      $scope.$apply();
    });
  };
};


var DeploymentNewController = function($scope, $state, $stateParams, grow) {
  $scope.deployment = {'owner': {'nickname': $stateParams['owner']}};
  $scope.destinations = [
    {'nickname': 'GOOGLE_STORAGE', 'title': 'Google Cloud Storage', 'image_url': 'http://preview.growsdk.org/static/images/banner/banner_gcs.svg'},
    {'nickname': 'GITHUB_PAGES', 'title': 'GitHub Pages', 'image_url': 'http://preview.growsdk.org/static/images/banner/banner_github.svg'}
  ];
  $scope.selectDestination = function(destination) {
    console.log(destination);
    var isSelected = $scope.deployment.destination == destination;
    if (isSelected) {
      $scope.deployment.destination = null;
    } else {
      $scope.deployment.destination = destination;
    }
  };

  $scope.createDeployment = function(deployment) {
    grow.rpc('deployments.create', {'deployment': deployment}).execute(
        function(resp) {
      $state.go('deployments.deployment', {
        'deployment': resp['deployment']['ident']
      });
      $scope.$apply();
    });
  };
};


var OwnerSettingsController = function($scope, $state, $rootScope, $stateParams, grow) {
  var org = {'nickname': $stateParams['owner']};
  $scope.deleteOrg = function() {
    grow.rpc('orgs.delete', {'org': org}).execute(function(resp) {
      $state.go('owner.projects', {'owner': $rootScope.me['nickname']});
      $scope.$apply();
    });
  };
};


var CollaboratorsController = function($scope, $state, $stateParams, grow) {
  $scope.membership = {
    'role': 'READ_ONLY'
  };
  var team = null;

  $scope.$watch('project', function() {
    var project = $scope.project;
    if (project && project['ident']) {
      team = {'kind': 'PROJECT_OWNERS', 'ident': project['ident']};
      grow.rpc('teams.get', {
        'team': team 
      }).execute(function(resp) {
        $scope.team = resp['team'];
        $scope.$apply();
      });
    }
  });

  $scope.updateMembership = function(membership) {
    grow.rpc('teams.update_membership', {
      'team': team,
      'membership': membership 
    }).execute(function(resp) {
      $scope.$apply();
    });
  };

  $scope.createMembership = function(membership) {
    grow.rpc('teams.create_membership', {
      'team': team,
      'membership': membership 
    }).execute(function(resp) {
      $scope.team = resp['team'];
      $scope.$apply();
    });
  };

  $scope.deleteMembership = function(membership) {
    grow.rpc('teams.delete_membership', {
      'team': team,
      'membership': membership 
    }).execute(function(resp) {
      $scope.team = resp['team'];
      $scope.$apply();
    });
  };

  var query = {
    'kind': 'DEFAULT',
    'owner': {'nickname': $stateParams['owner']},
    'projects': [{'nickname': $stateParams['project']}]
  };
  $scope.rpc = grow.rpc('teams.search', {
    'team': query 
  }).execute(function(resp) {
    $scope.teams = resp['teams'];
    $scope.$apply();
  });
};


var ProjectSettingsController = function($scope, $state, $rootScope, $stateParams, grow) {
  $scope.deleteProject = function(project) {
    grow.rpc('projects.delete', {'project': project}).execute(function(resp) {
      $state.go('owner.projects', {'owner': project['owner']['nickname']});
      $scope.$apply();
    });
  };
};
