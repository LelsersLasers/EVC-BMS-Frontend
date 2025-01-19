# EVC BMS Frontend

SvelteKit webapp for the BMS for Purdue's Electric Vehicle Club's high voltage battery.

## TODO:

- Favicon
- Better usage of error vs result messages
- Svelte component for the collections of bars and bars (instead of repeating the same code)?
	- Or snippets?
- Parameters/GUI inputs for all hardcoded values
	- Temp
	- Voltage difference
	- Current
- Automatically create a graph from `log.csv`
- A "currently balancing" bar color?
	- How to determine if it's balancing?
- Appearance:
	- In general, better CSS
	- Ex: better color diversity (and maybe some less aggressive colors)
	- Update mobile CSS

## Reference

- https://github.com/espressif/arduino-esp32/blob/master/libraries/HTTPUpdateServer/src/HTTPUpdateServer.h
- https://arduinojson.org/