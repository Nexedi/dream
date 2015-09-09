/*global require */
module.exports = function (grunt) {
  "use strict";


  var global_config = {
      src: "dream/platform/src/",
      lib: "dream/platform/vendor/",
      tmp: "tmp",
      dest: "dream/platform/static/"
    };

  grunt.loadNpmTasks("grunt-jslint");
  grunt.loadNpmTasks("grunt-contrib-uglify");
  grunt.loadNpmTasks('grunt-contrib-watch');
//   grunt.loadNpmTasks('grunt-contrib-qunit');
  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-curl');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-manifest');
  grunt.loadNpmTasks('grunt-zip');

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    global_config: global_config,

    jslint: {
      config: {
        src: ['package.json', 'Gruntfile.js'],
        directives: {
          maxlen: Infinity,
          indent: 2,
          maxerr: 3,
          predef: [
            'module'
          ]
        }
      },
      gadget: {
        src: ["<%= global_config.src %>/**/*.js"],
        directives: {
          maxlen: Infinity,
          indent: 2,
          maxerr: 5,
          todo: true,
          white: true,
          nomen: true,
          predef: [
            'window',
            'document',
            'Event'
          ]
        }
      }
    },

    less: {
      production: {
        options: {
          paths: ["<%= global_config.src %>/"],
          cleancss: true,
          syncImports: true,
          strictMath: true,
          strictUnits: true,
          syncImport: true
        },
        files: {
          "<%= global_config.dest %>/dream/index.css":
            "<%= global_config.src %>/dream/index.less",
          "<%= global_config.dest %>/jsplumb/jsplumb.css":
            "<%= global_config.src %>/jsplumb/jsplumb.css",
          "<%= global_config.dest %>/toolbox/toolbox.css":
            "<%= global_config.src %>/toolbox/toolbox.css"
        }
      }
    },

    uglify: {
      gadget: {
        // XXX Dev options
        options: {
          report: false,
          mangle: false,
          compress: false,
          beautify: true,
          preserveComments: "all"
        },
        files: [{
          expand: true,
          cwd: "<%= global_config.src %>/",
          src: '**/*.js',
          dest: "<%= global_config.dest %>/"
        }]
      }
    },

    copy: {
      images: {
        expand: true,
        cwd: "<%= global_config.src %>/",
        src: "**/images/*.*",
        dest: "<%= global_config.dest %>/"
      },
      favicon: {
        expand: true,
        cwd: "<%= global_config.src %>/",
        src: "**/*.ico",
        dest: "<%= global_config.dest %>/"
      },
      rsvp: {
//         src: "node_modules/rsvp/dist/rsvp-2.0.4.min.js",
        src: "<%= global_config.lib %>/rsvp.js",
        relative_dest: "lib/rsvp.min.js",
        dest: "<%= global_config.dest %>/<%= copy.rsvp.relative_dest %>"
      },
      uritemplate: {
        src: "node_modules/uritemplate/bin/uritemplate-min.js",
        relative_dest: "lib/uritemplate.min.js",
        dest: "<%= global_config.dest %>/<%= copy.uritemplate.relative_dest %>"
      },
      renderjs: {
//         src: "node_modules/renderjs/dist/renderjs-latest.js",
        src: "<%= global_config.lib %>/renderjs.js",
        relative_dest: "lib/renderjs.min.js",
        dest: "<%= global_config.dest %>/<%= copy.renderjs.relative_dest %>"
      },
      uri: {
        src: "<%= global_config.lib %>/URI.js",
        relative_dest: "lib/URI.js",
        dest: "<%= global_config.dest %>/<%= copy.uri.relative_dest %>"
      },
      handlebars: {
        src: 'node_modules/handlebars/dist/handlebars.min.js',
        relative_dest: 'lib/handlebars.min.js',
        dest: "<%= global_config.dest %>/<%= copy.handlebars.relative_dest %>"
      },
      qunitjs: {
        src: 'node_modules/qunitjs/qunit/qunit.js',
        relative_dest: 'lib/qunit.js',
        dest: "<%= global_config.dest %>/<%= copy.qunitjs.relative_dest %>"
      },
      dhtmlxganttjs: {
        src: "<%= global_config.lib %>/dhtmlxgantt.js",
//         src: "<%= unzip.dhtmlxgantt.dest %>/codebase/dhtmlxgantt.js",
        relative_dest: 'lib/dhtmlxgantt.js',
        dest: "<%= global_config.dest %>/<%= copy.dhtmlxganttjs.relative_dest %>"
      },
      dhtmlxganttcss: {
        src: "<%= global_config.lib %>/dhtmlxgantt.css",
//         src: "<%= unzip.dhtmlxgantt.dest %>/codebase/dhtmlxgantt.css",
        relative_dest: 'lib/dhtmlxgantt.css',
        dest: "<%= global_config.dest %>/<%= copy.dhtmlxganttcss.relative_dest %>"
      },
      dhtmlxschedulercss: {
        src: "<%= global_config.lib %>/dhtmlxscheduler.css",
        relative_dest: 'lib/dhtmlxscheduler.css',
        dest: "<%= global_config.dest %>/<%= copy.dhtmlxschedulercss.relative_dest %>"
      },
      dhtmlxschedulerjs: {
        src: "<%= global_config.lib %>/dhtmlxscheduler.js",
        relative_dest: 'lib/dhtmlxscheduler.js',
        dest: "<%= global_config.dest %>/<%= copy.dhtmlxschedulerjs.relative_dest %>"
      },
      qunitcss: {
        src: 'node_modules/qunitjs/qunit/qunit.css',
        relative_dest: 'lib/qunit.css',
        dest: "<%= global_config.dest %>/<%= copy.qunitcss.relative_dest %>"
      },
      gadget: {
        expand: true,
        cwd: "<%= global_config.src %>/",
        src: "**/*.html",
        dest: "<%= global_config.dest %>/",
        nonull: true,
        options: {
          process: function (content) {
            return grunt.template.process(content);
          }
        }
      }
    },

    watch: {
      src: {
        files: [
          '<%= global_config.src %>/**',
          '<%= jslint.config.src %>'
        ],
        tasks: ['default']
      }
    },

    curl: {
      jquery: {
        src: 'http://code.jquery.com/jquery-2.0.3.js',
        relative_dest: 'lib/jquery.js',
        dest: '<%= global_config.dest %>/<%= curl.jquery.relative_dest %>'
      },
      jquerymobilejs: {
        url_base: 'http://code.jquery.com/mobile/1.4.0-alpha.2/',
        src_base: '<%= curl.jquerymobilejs.url_base %>jquery.mobile-1.4.0-alpha.2',
        src: '<%= curl.jquerymobilejs.src_base %>.js',
        relative_dest: 'lib/jquerymobile.js',
        dest: '<%= global_config.dest %>/<%= curl.jquerymobilejs.relative_dest %>'
      },
      jquerymobileloader: {
        src: '<%= curl.jquerymobilejs.url_base %>images/ajax-loader.gif',
        relative_dest: 'lib/images/ajax-loader.gif',
        dest: '<%= global_config.dest %>/<%= curl.jquerymobileloader.relative_dest %>'
      },
      jquerymobilecss: {
        src: '<%= curl.jquerymobilejs.src_base %>.css',
        relative_dest: 'lib/jquerymobile.css',
        dest: '<%= global_config.dest %>/<%= curl.jquerymobilecss.relative_dest %>'
      },
      jqueryflot: {
        url_base: 'https://raw.githubusercontent.com/flot/flot/' +
          '453b017cc5acfd75e252b93e8635f57f4196d45d/',
        src: '<%= curl.jqueryflot.url_base%>jquery.flot.js',
        relative_dest: 'lib/jquery.flot.js',
        dest: '<%= global_config.dest %>/<%= curl.jqueryflot.relative_dest %>'
      },
      jqueryflotstack: {
        src: '<%= curl.jqueryflot.url_base%>jquery.flot.stack.js',
        relative_dest: 'lib/jquery.flot.stack.js',
        dest: '<%= global_config.dest %>/<%= curl.jqueryflotstack.relative_dest %>'
      },
      jqueryflottime: {
        src: '<%= curl.jqueryflot.url_base%>jquery.flot.stack.js',
        relative_dest: 'lib/jquery.flot.time.js',
        dest: '<%= global_config.dest %>/<%= curl.jqueryflottime.relative_dest %>'
      },
      jqueryflotorderbars: {
        src: '<%= curl.jqueryflot.url_base%>jquery.flot.orderBars.js',
        relative_dest: 'lib/jquery.flot.orderBars.js',
        dest: '<%= global_config.dest %>/<%= curl.jqueryflotorderbars.relative_dest %>'
      },
      dhtmlxgantt: {
        src: 'http://dhtmlx.com/x/download/regular/dhtmlxGantt.zip',
        dest: '<%= global_config.tmp %>/dhtmlxGantt.zip'
      },
      jquerysimulatejs: {
        src: "https://raw.githubusercontent.com/eduardolundgren/jquery-simulate/" +
          "b9e110ddbdff2fc0853c9ebf00c493c8e368e6c9/jquery.simulate.js",
        relative_dest: 'lib/jquery.simulate.js',
        dest: '<%= global_config.dest %>/<%= curl.jquerysimulatejs.relative_dest %>'
      },
      momentjs: {
        src: 'https://raw.githubusercontent.com/moment/moment/2.5.1/min/' +
          'moment-with-langs.min.js',
        relative_dest: 'lib/moment.js',
        dest: '<%= global_config.dest %>/<%= curl.momentjs.relative_dest %>'
      },
      daff: {
        src: "<%= global_config.lib %>/daff.js",
        relative_dest: 'lib/daff.js',
        dest: '<%= global_config.dest %>/<%= curl.daff.relative_dest %>'
      },
      handsontablejs: {
        src: 'https://raw.githubusercontent.com/warpech/' +
          'jquery-handsontable/v0.10.5/dist/jquery.handsontable.full.js',
        relative_dest: 'lib/handsontable.js',
        dest: '<%= global_config.dest %>/<%= curl.handsontablejs.relative_dest %>'
      },
      handsontablecss: {
        src: 'https://raw.githubusercontent.com/warpech/' +
          'jquery-handsontable/v0.10.5/dist/jquery.handsontable.full.css',
        relative_dest: 'lib/handsontable.css',
        dest: '<%= global_config.dest %>/<%= curl.handsontablecss.relative_dest %>'
      },
      jqueryuijs: {
        src: 'https://code.jquery.com/ui/1.10.4/jquery-ui.js',
        relative_dest: 'lib/jquery-ui.js',
        dest: '<%= global_config.dest %>/<%= curl.jqueryuijs.relative_dest %>'
      },
      jqueryuicss: {
        src: 'https://code.jquery.com/ui/1.11.0-beta.1/themes/base/jquery-ui.css',
        relative_dest: 'lib/jquery-ui.css',
        dest: '<%= global_config.dest %>/<%= curl.jqueryuicss.relative_dest %>'
      },
      jsplumbjs: {
        src: "https://raw.githubusercontent.com/sporritt/jsPlumb/" +
          "1.6.2/dist/js/jquery.jsPlumb-1.6.2.js",
        relative_dest: 'lib/jquery.jsplumb.js',
        dest: '<%= global_config.dest %>/<%= curl.jsplumbjs.relative_dest %>'
      }
//       },
//       beautifyhtml: {
//         src: 'https://raw.githubusercontent.com/einars/js-beautify/master/js/lib/beautify-html.js',
//         relative_dest: 'lib/beautify-html.js',
//         dest: '<%= global_config.dest %>/<%= curl.beautifyhtml.relative_dest %>'
//       }
      //     qunit: {
//       all: ['test/index.html']
    },

    unzip: {
      dhtmlxgantt: {
        src: '<%= curl.dhtmlxgantt.dest %>',
        dest: '<%= global_config.tmp %>/dhtmlxGantt/'
      }
    },
    manifest: {
      generate: {
        options: {
          basePath: "<%= global_config.dest %>",
          verbose: true,
          timestamp: true,
          hash: true
        },
        src: [
          '**/*.html',
          '**/*.gif',
          '**/*.png',
          '**/*.jpg',
          '**/*.js',
          '**/*.css',
          '**/*.json'
        ],
        dest: '<%= global_config.dest %>/manifest.appcache'
      }
    }

  });

  grunt.registerTask('default', ['all']);
  grunt.registerTask('all', ['lint', 'build']);
  grunt.registerTask('lint', ['jslint']);
  grunt.registerTask('dep', ['curl', 'unzip']);
//   grunt.registerTask('test', ['qunit']);
  grunt.registerTask('build', ['copy', 'uglify', 'less', 'manifest']);

};
