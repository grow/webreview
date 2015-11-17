angular.module('jetwayFilters', []).filter('prettyRole', function() {
  return function(role) {
    var rolesToTitles = {
      'ADMIN': 'Administrator',
      'READ_ONLY': 'Read',
      'WRITE_FULL': 'Write'
    };
    return rolesToTitles[role] || 'Unknown';
  };
});
