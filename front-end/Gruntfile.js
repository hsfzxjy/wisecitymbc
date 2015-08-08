module.exports = function(grunt) {

    function generateFileList (pathPrefix, files) {

        //if (! pathPrefix.startswith('/')) pathPrefix += '/';

        return files.map(function (fileName) {
            return pathPrefix + fileName + '.js';
        });
    }

    var targetDir = '../static/';

    function baseFilter (filename) {
        return ! /^src\/dependencies/.test(filename);
    }

    function concatTargetFile (filename) {
        return targetDir + filename;
    }

    function getCommonConfig (dir) {
        return {
            src: generateFileList('src/common/', [
                'utils', 
                'api', 
                'load-list', 
                'multiselect-table'
            ]),
            dest: concatTargetFile(dir+'/common/main.js')
        };
    }

    function getAllConfig (dir) {
        return {
            expand: true,
            cwd: 'src',
            src: '**/*.js',
            filter: baseFilter,
            dest: concatTargetFile(dir)
        };
    }

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        copy: {
            src: getAllConfig('src')
        },

        concat: {
            common: getCommonConfig('src')
        },

        uglify: {
            common: getCommonConfig('build'),
            build: getAllConfig('build'),
            dependencies: {
                expand: true,
                cwd: 'src/dependencies',
                src: '*.js',
                dest: concatTargetFile('')
            }
        },

        less: {
            styles: {
                expand: true,
                cwd: 'styles',
                src: '*.less',
                dest: concatTargetFile('css'),
                ext: '.css'
            }
        },

        watch: {
            js: {
                files: ['src/**/*.js'],
                tasks: ['copy', 'concat', 'uglify']
            },
            less: {
                files: ['styles/**/*.less', 'styles/*.less'],
                tasks: ['less']
            },
            options: {
                nospawn: true,
                livereload: true
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.registerTask('default', ['uglify', 'copy', 'concat', 'less']);
};
