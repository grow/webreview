var concat = require('gulp-concat');
var gulp = require('gulp');
var stylish = require('jshint-stylish');
var uglify = require('gulp-uglify');


var Path = {
  CSS_OUT_DIR: './dist/css/',
  CSS_SOURCES: './jetway/frontend/static/css/*.css',
  JS_OUT_DIR: './dist/js/',
  JS_SOURCES: './jetway/frontend/static/js/*.js',
};


gulp.task('minify', function(){
  gulp.src([
    './bower_components/bootstrap/dist/css/bootstrap.min.css',
    Path.CSS_SOURCES,
  ])
      .pipe(concat('main.min.css'))
      .pipe(gulp.dest(Path.CSS_OUT_DIR));

  gulp.src([
    './bower_components/angular/angular.min.js',
    './bower_components/angular-bootstrap/ui-bootstrap.min.js',
    './bower_components/angular-ui-router/release/angular-ui-router.min.js',
    './bower_components/angular-xeditable/dist/js/xeditable.js',
    './jetway/frontend/static/js/controllers.js',
    Path.JS_SOURCES,
  ])
      .pipe(concat('main.min.js'))
      .pipe(gulp.dest(Path.JS_OUT_DIR));
});


gulp.task('watch', function() {
  var paths = [
    Path.JS_SOURCES,
    Path.CSS_SOURCES,
  ];
  gulp.watch(paths, ['minify']);
});


gulp.task('build', ['minify']);
gulp.task('default', ['minify', 'watch']);
