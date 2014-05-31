import configparser
import subprocess
import os, sys, inspect

cmd_folder = os.path.realpath(os.path.abspath(".."))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import const_data

config = configparser.ConfigParser()

config.read("build.ini")
build_number = int(config["version"]["build"])
config["version"]["build"] = str(build_number + 1)


#generate arguments to pass to minifier
js_build_args = ["java", "-jar", r"..\bin\compiler.jar"]

for file_name in const_data.js_files:
    js_build_args.append("--js")
    js_build_args.append(file_name)

js_build_args.extend(["--create_source_map", "map.js",
    "--compilation_level=SIMPLE",
    "--js_output_file", "lib.min.js"])

with open('build.ini', 'w') as configfile:
    config.write(configfile)

f = open('..\generated_data.py', 'w')
f.write("BUILD_NUMBER = " + str(build_number))
f.close()





process = subprocess.Popen(js_build_args, cwd=r"..\js")
process.wait()
