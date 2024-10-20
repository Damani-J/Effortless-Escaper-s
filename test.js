gulp.task('scripts', function(){
    return gulp.src('./EEV2/vendor/jquery/jquery.min.js')  // Test with just one file
    .pipe(concat('combined.js'))
    .pipe(gulp.dest('./dist'));
});