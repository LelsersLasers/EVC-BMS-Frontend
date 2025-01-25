# EVC BMS Frontend

SvelteKit webapp for the BMS for Purdue's Electric Vehicle Club's high voltage battery.

## TODO:

- Logging errors (as codes)
- Display all faults (high voltage, big diff, etc)
	- And make it persistent
- Parameters/GUI inputs for all hardcoded values:
	- Voltage
		- [x] Per cell min [`vMin`]
		- [x] Per cell max [`vMax`]
		- [x] Average cell min [`vMinAvg`]
		- [x] Average cell max [`vMaxAvg`]
		- [x] Max cell delta [`vDiff`]
			- [x] Add bar
	- Temperature
		- [x] Per thermistor min [`tMin`]
		- [x] Per thermistor max [`tMax`]
			- Doesn't apply to temp fet
		- [x] Max temp delta [`tDiff`]
			- Doesn't apply to FET
			- Not critical (no cutoff) but should throw fault code
			- [x] Add bar
		- [ ] Max FET temp [`tMaxFET`]
		- [ ] Max balance temp [`tMaxBal`]
	- Current
		- [ ] Max instantaneous current [`iMax`]
		- [ ] Max continuous current [`iMaxCont`]
		- We will need to change some logic for this
	- [ ] If BMS sees current being drawn and it shouldn't -> complain
	- [x] Logging speed [`logSpeed`]
	- Bypass
		- [x] Bypass enabled [`bypass`]
		- [x] Bypass voltage [`vBypass`]
			- Not critical
	- Notes:
		- Defines for starting parameters in battery.h
		- Actually use the Parameters struct/dict when doing the checks
			- On the frontend and the Arduino
- Will CORS be a problem?
	- Why can I not use things from: https://github.com/espressif/arduino-esp32/blob/master/libraries/WebServer/examples/Middleware/Middleware.ino ??????
- Automatically create a graph from `log.csv`
- Fix: 5 sec fetch timer??
	- The fetch seems to not go off at exactly 5 seconds??
- Svelte components (or snippets) for:
	- [] The collections of bars and bars (instead of repeating the same code)?
	- [x] And all the inputs
		- Did this with a component, might make more sense to use a snippet
- Appearance:
	- [ ] Use a table for stacked inputs so they all line up
	- In general, better CSS
	- Ex: better color diversity (and maybe some less aggressive colors)
	- [x] Update mobile CSS

## Reference

- https://github.com/espressif/arduino-esp32/blob/master/libraries/HTTPUpdateServer/src/HTTPUpdateServer.h
- https://arduinojson.org/
