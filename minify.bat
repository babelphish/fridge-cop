java -jar .\bin\compiler.jar --js .\js\jquery-1.11.1.js --js .\js\vex.combined.min.js ^
 --js .\js\main.js --js .\js\json2.min.js --js .\js\moment.min.js --js .\js\moment-timezone.min.js ^
 --js .\js\moment-timezone-data.js  ^
 --js .\js\jquery.qtip.js --js .\js\vis.js --externs .\js\externs.js --create_source_map map.js^
 --compilation_level=ADVANCED ^
 --js_output_file .\js\lib.min.js
	  