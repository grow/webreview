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
      if (!$scope.watchers) {
        $scope.watchers = [];
      }
      $scope.watchers.push(resp['watcher']);
      $scope.watching = true;
      $scope.$apply();
    });
  };

  $scope.rpcs.watchers = grow.rpc('projects.list_watchers', {
    'project': project
  }).execute(function(resp) {
    $scope.watchers = resp['watchers'];
    $scope.watching = resp['watching'];
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


var SettingsOrgsController = function($scope, grow) {

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
  $scope.createNamedFileset = function(project, namedFileset) {
    grow.rpc('projects.list_named_filesets', {'project': project}).execute(function(resp) {
      $scope.namedFilesets = resp['named_filesets'];
      $scope.$apply();
    });
  };
  $scope.listNamedFilesets = function(project) {
    grow.rpc('projects.list_named_filesets', {'project': project}).execute(function(resp) {
      $scope.namedFilesets = resp['named_filesets'];
      $scope.$apply();
    });
  };
  $scope.deleteProject = function(project) {
    grow.rpc('projects.delete', {'project': project}).execute(function(resp) {
      $state.go('owner.projects', {'owner': project['owner']['nickname']});
      $scope.$apply();
    });
  };
};
