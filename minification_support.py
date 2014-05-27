import random
import os
import consts

def getScriptTags(development):
    scripts = []

    scripts.append('<script type="text/javascript" src="//www.google.com/jsapi"></script>')
    scripts.append('<script type="text/javascript" src="/init.js"></script>')

    if (development):
        random_num = random.randrange(1,100000000)
        scripts.append('<script type="text/javascript" src="/js/jquery-1.11.1.min.js?b=' + str(random_num)  + '"></script>')
        scripts.append('<script type="text/javascript" src="/js/vex.combined.min.js?b=' + str(random_num) + '"></script>')
	scripts.append('<script type="text/javascript" src="/js/main.js?b=' + str(random_num) + '"></script>')
	scripts.append('<script type="text/javascript" src="/js/json2.min.js?b=' + str(random_num) + '"></script>')
	scripts.append('<script type="text/javascript" src="/js/moment.min.js?b=' + str(random_num) + '"></script>')
	scripts.append('<script type="text/javascript" src="/js/moment-timezone.min.js?b=' + str(random_num)+ '"></script>')
	scripts.append('<script type="text/javascript" src="/js/moment-timezone-data.js?b=' + str(random_num) + '"></script>')
	scripts.append('<script type="text/javascript" src="/js/jquery.qtip.min.js?b=' + str(random_num) + '"></script>')
	scripts.append('<script type="text/javascript" src="/js/timeline.js?b=' + str(random_num) + '"></script>')
    else:
        scripts.append('<script type="text/javascript" src="/js/lib.min.js?b=' + str(consts.BUILD_NUMBER) + '"></script>')


    scripts.append('<script src="//node.fridge-cop.com/socket.io/socket.io.js"></script>')


    return os.linesep.join(scripts)
