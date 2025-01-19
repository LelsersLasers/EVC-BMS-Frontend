# EVC BMS Frontend

SvelteKit webapp for the BMS for Purdue's Electric Vehicle Club's high voltage battery.

## TODO:

- Change the ip address even if currently connected
- Loading back to T/F instead of a count?
	- Or 2 separate loading states? (one for data loop one for parameters)
- Section dividers (`// ------------...---------- //`s)
- Appearance:
	- More readable bars
		- Make the unit (V, A, C, etc) and label (1, FET, avg, etc) smaller/italtics/ligher font/something
	- Improve look of "waiting for ip" and loading displays
	- Improve the look of buttons
		- More button-y, drop shadow
	- In general, better CSS
- Component for the collections of bars (instead of repeating the same code)
- Finish side bar
- File upload
- Fix graphing
- WEBSOCKETS?????
- MOBILE CSS