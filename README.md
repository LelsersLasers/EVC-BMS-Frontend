# EVC BMS Frontend

SvelteKit webapp for the BMS for Purdue's Electric Vehicle Club's high voltage battery.

## TODO:

- Better usage of error vs result messages
- Svelte component for the collections of bars and bars (instead of repeating the same code)?
	- Or snippets?
- Parameters/GUI inputs for all hardcoded values
	- Temp high cutoff
	- Max - min voltage
	- Max - avg voltage (balancing cutoff)
	- Voltage low cutoff
	- Voltage high cutoff
	- Max charging current
- Automatically create a graph from `log.csv`
- Fix: 5 sec fetch timer??
	- The fetch seems to not go off at exactly 5 seconds??
- Appearance:
	- In general, better CSS
	- Ex: better color diversity (and maybe some less aggressive colors)
	- Update mobile CSS

## Reference

- https://github.com/espressif/arduino-esp32/blob/master/libraries/HTTPUpdateServer/src/HTTPUpdateServer.h
- https://arduinojson.org/