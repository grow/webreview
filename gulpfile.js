var autoprefixer = require('gulp-autoprefixer');
var concat = require('gulp-concat');
var es = require('event-stream');
var gulp = require('gulp');
var plumber = require('gulp-plumber');
var sass = require('gulp-sass');
var stylish = require('jshint-stylish');
var uglify = require('gulp-uglify');


var Path = {
  CSS_OUT_DIR: './dist/css/',
  CSS_SOURCES: './jetway/frontend/static/sass/*',
  JS_OUT_DIR: './dist/js/',
  JS_SOURCES: './jetway/frontend/static/js/*.js',
};


gulp.task('sass', function() {
  var appFiles = gulp.src('./jetway/frontend/static/sass/*.scss')
    .pipe(plumber())
    .pipe(sass({
        outputStyle: 'compressed'
    }))
  var vendorFiles = gulp.src([
    './bower_components/bootstrap/dist/css/bootstrap.min.css',
  ])
  return es.concat(vendorFiles, appFiles)
      .pipe(concat('main.min.css'))
      .pipe(autoprefixer())
      .pipe(gulp.dest(Path.CSS_OUT_DIR));
});


gulp.task('minify', function(){
  return gulp.src([
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
  gulp.watch([Path.JS_SOURCES], ['minify']);
  gulp.watch([Path.CSS_SOURCES], ['sass']);
});


gulp.task('build', ['sass', 'minify']);
gulp.task('default', ['sass', 'minify', 'watch']);
