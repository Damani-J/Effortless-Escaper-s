import gulp from 'gulp';
import concat from 'gulp-concat';
import order from 'gulp-order';


gulp.task('scripts', function(){
    return gulp.src('./EEV2/vendor/**/*.js')  // Include all .js files in vendor and subfolders
    .pipe(order([
        'jquery.min.js',
        'jquery.validate.min.js',
        'bootstrap.min.js',
        'jquery.bootstrap.wizard.min.js',
        'daterangepicker.js',
        'moment.min.js',
        'select2.min.js'
    ]))
    .pipe(concat('combined.js'))
    .pipe(gulp.dest('./dist'));    // Save to 'dist' folder
});
