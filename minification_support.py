import random
import os
import generated_data
import const_data


def getScriptTags(development):
    script_tag_template = '<script type="text/javascript" src="/js/{0}?b={1}"></script>'
    
    scripts = []

    scripts.append('<script type="text/javascript" src="//www.google.com/jsapi"></script>')
    scripts.append('<script type="text/javascript" src="/init.js"></script>')

    if (development):
        random_num = random.randrange(1,100000000)
        for file_name in const_data.js_files:
            scripts.append(script_tag_template.format(file_name, str(random_num)))            
    else:
        scripts.append(script_tag_template.format("lib.min.js", str(generated_data.BUILD_NUMBER)))

    return os.linesep.join(scripts)

def getStyleTags(development):
    styles = []
    style_tag_template = '<link rel="stylesheet" type="text/css" href="/css/{0}?b={1}">'

    if (development):
        random_num = random.randrange(1,100000000)
        for file_name in const_data.css_files:
            styles.append(style_tag_template.format(file_name, str(random_num)))
    else:
        styles.append(style_tag_template.format("main.min.css", str(generated_data.BUILD_NUMBER)))
        
    return os.linesep.join(styles)
