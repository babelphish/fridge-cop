import ConfigParser
import subprocess
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from const_data import *
from subprocess import check_output
from copy import copy

cmd_folder = os.path.realpath(os.path.abspath(".."))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import const_data

def main():
    config = ConfigParser.SafeConfigParser()

    config.read("build.ini")
    build_number = int(config.get("version","build"))
    config.set("version","build", str(build_number + 1))

    with open('build.ini', 'w') as configfile:
        config.write(configfile)

    f = open('..\generated_data.py', 'w')
    f.write("BUILD_NUMBER = " + str(build_number))
    f.close()
    
    f = open('..\js\generated_data.js', 'w')
    f.write("var visibleUserNamePattern = /" + visible_name_validation_expression + "/;")
    f.write("var maxVisibleUserNameLength = " + str(max_visible_name_length) + ";")

    f.close()
    
    minify_css()
    js_process = minify_js()
    js_process.wait()
    
def minify_css():
    #css_build_args = ["java", "-jar", r"..\bin\yuicompressor-2.4.8.jar"]

    result = ""
    for file_name in const_data.css_files:
        with open('..\\css\\' + file_name, 'r') as f:
            read_data = f.read()
            result += read_data
        f.closed
        #process_css_file_args = copy(css_build_args)
        #process_css_file_args.append("..\\css\\" + file_name)
        #result += check_output(process_css_file_args).decode("utf-8") + os.linesep

    print (result)
    f = open('..\css\main.min.css', 'w')
    f.write(result)
    f.close()

def minify_js():
    #generate arguments to pass to minifier
    js_build_args = ["java", "-jar", r"..\bin\compiler.jar"]

    for file_name in const_data.js_files:
        js_build_args.append("--js")
        js_build_args.append(file_name)

    js_build_args.extend(["--create_source_map", "map.js",
        "--compilation_level=SIMPLE",
        "--js_output_file", "lib.min.js"])

    return subprocess.Popen(js_build_args, cwd=r"..\js")

if __name__ == "__main__":
    main()
