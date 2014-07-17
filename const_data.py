import re
js_files = ["jquery-1.11.1.min.js",
            "jquery-ui.min.js",
            "vex.combined.min.js",
            "state_client.js",
            "bootstrap.js",
            "main.js",
            "magnets.js",
            "generated_data.js",
            "json2.min.js",
            "moment.min.js",
            "moment-timezone.min.js",
            "moment-timezone-data.js",
            "timeline.js",
            "jquery.qtip.min.js",
            "socket.io.js"]

css_files = ["bootstrap.css",
             "bootstrap-theme.css",
            "jquery.qtip.min.css",
             "timeline.css",
             "sprites.css",
             "vex.css",
             "vex-theme-default.css",
             "main.css"
            ]

min_visible_name_length = 5
max_visible_name_length = 30
visible_name_validation_expression = "^[\S ]{{{0},{1}}}$".format(min_visible_name_length,
                                                           max_visible_name_length)

visible_name_pattern = re.compile(visible_name_validation_expression, re.UNICODE)

