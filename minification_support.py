import random
import os
import generated_data
import const_data

def getScriptTags(development):
    scripts = []

    scripts.append('<script type="text/javascript" src="//www.google.com/jsapi"></script>')
    scripts.append('<script type="text/javascript" src="/init.js"></script>')

    if (development):
        random_num = random.randrange(1,100000000)
        for file_name in const_data.js_files:
            scripts.append('<script type="text/javascript" src="/js/{0}?b={1}"></script>'.format(file_name, str(random_num)))
        scripts.append('<script src="//localhost:8081/socket.io/socket.io.js"></script>')
    else:
        scripts.append('<script type="text/javascript" src="/js/lib.min.js?b=' + str(consts.BUILD_NUMBER) + '"></script>')
        scripts.append('<script src="//node.fridge-cop.com/socket.io/socket.io.js"></script>')

    return os.linesep.join(scripts)
