# EVC BMS Frontend

SvelteKit webapp for the BMS for Purdue's Electric Vehicle Club's high voltage battery.

## TODO:

- File upload
- Auto graph from `log.csv`
- Appearance:
	- More readable bars
		- Make the unit (V, A, C, etc) and label (1, FET, avg, etc) smaller/italtics/ligher font/something
	- Improve look of "waiting for ip" and loading displays
	- Improve the look of buttons
		- More button-y, drop shadow
	- In general, better CSS
		- Ex: better color diversity
		- Maybe make the whole thing dark mode
- Svelte component for the collections of bars (instead of repeating the same code)?
- CSS for mobile

## Reference

- https://github.com/espressif/arduino-esp32/blob/master/libraries/HTTPUpdateServer/src/HTTPUpdateServer.h
- https://arduinojson.org/