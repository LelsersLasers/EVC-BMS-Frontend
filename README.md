# EVC BMS Frontend

SvelteKit webapp for the BMS for Purdue's Electric Vehicle Club's high voltage battery.

## TODO:

- [ ] Build system to automatically push to BMS SPIFFS if connected?
- Display all faults (high voltage, big diff, etc)
	- And make it persistent
- Parameters/GUI inputs for all hardcoded values:
	- [ ] Name change (apSSID)
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
			- [x] Doesn't apply to temp fet
		- [x] Max temp delta [`tDiff`]
			- Doesn't apply to FET
			- Not critical (no cutoff) but should throw fault code
			- [x] Add bar
		- TODO: 4 temps now
		- 2 new balance temps
		- [ ] Max FET temp [`tMaxFET`]
			- 50-80C
		- [ ] Max balance temp [`tMaxBal`]
			- TODO: implement into the UI
			- 40C restart
			- 50C stop
	- Current
		- [ ] Max instantaneous current [`iMax`]
		- [ ] Max continuous current [`iMaxCont`]
		- We will need to change some logic for this
		- NOTE: negative current is fine (charging vs discharging)
	- [ ] If BMS sees current being drawn and it shouldn't -> complain
	- [x] Logging speed [`logSpeed`]
	- Bypass
		- [x] Bypass enabled [`bypass`]
		- [x] Bypass voltage [`vBypass`]
			- Not critical
	- [ ] Battery/fault check rate
	- Notes:
		- Defines for starting parameters in battery.h
		- Actually use the Parameters struct/dict when doing the checks
			- On the frontend and the Arduino
- [ ] Automatically create a graph from `log.csv`
- Save all past valid IPs
- Actually fix CORS
- Fix: 5 sec fetch timer?
	- The fetch seems to not go off at exactly 5 seconds??
	- [ ] Also it would be interesting to have an input for the fetch timer
- Svelte components (or snippets) for:
	- [ ] The collections of bars and bars (instead of repeating the same code)?
	- [x] And all the inputs
		- Did this with a component, might make more sense to use a snippet
- Appearance:
	- [ ] Better button colors
	- [ ] Use a table for stacked inputs so they all line up
	- In general, better CSS
	- Ex: better color diversity (and maybe some less aggressive colors)
	- [x] Update mobile CSS

## Reference

- https://github.com/espressif/arduino-esp32/blob/master/libraries/HTTPUpdateServer/src/HTTPUpdateServer.h
- https://arduinojson.org/
