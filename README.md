# EVC BMS Frontend

SvelteKit webapp for the BMS for Purdue's Electric Vehicle Club's high voltage battery.

## TODO:

- Defines for starting parameters
- Actually use the Parameters struct
	- Frontend
	- And Arduino
- Parameters/GUI inputs for all hardcoded values
	- Temp high cutoff
	- [x] Bypass voltage
	- Max - min voltage
		- Add bar?
	- Max - avg voltage (balancing cutoff)
		- Add bar? (maybe combine with above)
	- [x] Voltage low cutoff
	- Voltage high cutoff
	- Max charging current
	- Bypass minium voltage
- Hover over State header -> tooltip that says that state changes are immediate
- Will CORS be a problem?
	- Why can I not use things from: https://github.com/espressif/arduino-esp32/blob/master/libraries/WebServer/examples/Middleware/Middleware.ino ??????
- Better usage of error vs result messages
- Svelte component for the collections of bars and bars (instead of repeating the same code)?
	- Or snippets?
- Automatically create a graph from `log.csv`
- Handle multiple people connecting?
	- Problem: need to keep the parameter states``
- Fix: 5 sec fetch timer??
	- The fetch seems to not go off at exactly 5 seconds??
- `/` redirects to the frontend web app
- Appearance:
	- In general, better CSS
	- Ex: better color diversity (and maybe some less aggressive colors)
	- Update mobile CSS

## Reference

- https://github.com/espressif/arduino-esp32/blob/master/libraries/HTTPUpdateServer/src/HTTPUpdateServer.h
- https://arduinojson.org/
