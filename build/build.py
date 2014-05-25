import configparser
import subprocess

config = configparser.ConfigParser()

config.read("build.ini")
build_number = int(config["version"]["build"])
build_number += 1

with open('build.ini', 'w') as configfile:
    config.write(configfile)

f = open('..\consts.py', 'w')
f.write("BUILD_NUMBER = " + str(build_number))
f.close()

subprocess.Popen(["java", "-jar", r"..\bin\compiler.jar", "--js", "jquery-1.11.1.min.js",
                "--js", "vex.combined.min.js",
                "--js", "main.js",
                "--js", "json2.min.js",
                "--js", "moment.min.js",
                "--js", "moment-timezone.min.js",
                "--js", "moment-timezone-data.js",
                "--js", "timeline.js",
                "--js", "jquery.qtip.min.js",
                "--create_source_map", "map.js",
                "--compilation_level=SIMPLE",
                "--js_output_file", "lib.min.js"], cwd=r"..\js"
                 )
