java -jar ..\bin\compiler.jar --js jquery-1.11.1.js --js vex.combined.min.js ^
 --js main.js --js json2.min.js --js moment.min.js --js moment-timezone.min.js ^
 --js moment-timezone-data.js --js timeline-min.js ^
 --js jquery.qtip.js --create_source_map map.js ^
 --compilation_level=SIMPLE ^
 --js_output_file lib.min.js
	  