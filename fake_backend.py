# from flask import Flask, jsonify
import flask
import flask_cors
import random
import time

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.route('/name', methods=['GET'])
def name():
	return "apSSID"

@app.route('/state/idle', methods=['GET'])
def idle():
	time.sleep(3)
	return "idle"

@app.route('/state/monitor', methods=['GET'])
def monitor():
	return "monitor"

@app.route('/state/balancing', methods=['GET'])
def balancing():
	return "balancing"

@app.route('/fullShutdown', methods=['GET'])
def fullShutdown():
	return "ok"

@app.route('/parameters/<param>/<value>', methods=['GET'])
def parameter(param, value):
	time.sleep(1)
	return "ok -> " + value

@app.route('/forceDischarge/enable', methods=['GET'])
def forceDischargeEnable():
	return "enable"

@app.route('/forceDischarge/disable', methods=['GET'])
def forceDischargeDisable():
	return "disable"

@app.route('/log/download', methods=['GET'])
def logDownload():
	return "log"

@app.route('/log/delete', methods=['GET'])
def logDelete():
	return "ok"

@app.route('/upload', methods=['POST'])
def upload():
	return "ok"

@app.route('/acknowledge/<fault>', methods=['GET'])
def acknowledge(fault):
	time.sleep(1)
	return "ok"

@app.route('/data', methods=['GET'])
def data():
	time.sleep(0.2)

	def random_voltage():
		# return random.random() * (4.2 - 3.0) + 3.0
		return random.random() * (4.0 - 3.9) + 3.9
	def random_temperature():
		# return random.random() * (50 - 10) + 10
		return random.random() * (30 - 28) + 28

	doc = {}

	doc["cells"] = []
	doc["discharge"] = []
	for i in range(2):
		discharge = 1 << 8
		doc["discharge"].append(discharge)
		
		doc["cells"].append([])		
		for _j in range(12):
			doc["cells"][i].append(random_voltage())

	doc["min"] = min([min(doc["cells"][i]) for i in range(2)])
	doc["max"] = max([max(doc["cells"][i]) for i in range(2)])
	doc["avg"] = random_voltage()
	doc["sum"] = random_voltage() * 12 * 2

	doc["pack"] = {}
	doc["pack"]["1"] = random_voltage() * 12
	doc["pack"]["2"] = random_voltage() * 12

	doc["current"] = random.random() * 30

	doc["therm"] = {}
	doc["therm"]["1"] = random_temperature()
	doc["therm"]["2"] = random_temperature()
	doc["therm"]["3"] = random_temperature()
	doc["therm"]["FET"] = random_temperature() * 0.8

	doc["anyBypassed"] = True # random.choice([True, False])
	doc["tDiffTriggered"] = True
	doc["tempFetTrigged"] = True

	doc["state"] = "monitor" # random.choice(["idle", "monitor", "balancing"] )

	doc["SSS"] = True # random.choice([True, False])
	doc["HCS"] = True # random.choice([True, False])

	doc["parameters"] = {}

	doc["parameters"]["bypass"] = False 
	doc["parameters"]["vBypass"] = 5.0 
	
	doc["parameters"]["vMin"] = 3.0
	doc["parameters"]["vMax"] = 4.2
	doc["parameters"]["vMinAvg"] = 3.0
	doc["parameters"]["vMaxAvg"] = 4.2
	doc["parameters"]["vDiff"] = 0.2
	
	doc["parameters"]["tMin"] = 10.0
	doc["parameters"]["tMax"] = 50.0
	doc["parameters"]["tDiff"] = 30.0

	doc["parameters"]["tMaxBal"] = 50.0
	doc["parameters"]["tResetBal"] = 40.0

	doc["parameters"]["logSpeed"] = 1000
	doc["parameters"]["deleteLog"] = False

	doc["faults"] = {}

	doc["faults"]["batteryMinVoltage"]     = False
	doc["faults"]["batteryMaxVoltage"]     = False
	doc["faults"]["batteryAverageVoltage"] = False
	doc["faults"]["batteryVoltageDiff"]    = True
	doc["faults"]["batteryTherm1Temp"]     = False
	doc["faults"]["batteryTherm2Temp"]     = False
	doc["faults"]["batteryTherm3Temp"]     = True
	doc["faults"]["batteryCurrent"]        = True

	doc["faults"]["overPower"]             = True

	doc["pFaults"] = {}

	doc["pFaults"]["batteryMinVoltage"]     = False
	doc["pFaults"]["batteryMaxVoltage"]     = False
	doc["pFaults"]["batteryAverageVoltage"] = False
	doc["pFaults"]["batteryVoltageDiff"]    = True
	doc["pFaults"]["batteryTherm1Temp"]     = False
	doc["pFaults"]["batteryTherm2Temp"]     = False
	doc["pFaults"]["batteryTherm3Temp"]     = True
	doc["pFaults"]["batteryCurrent"]        = True

	doc["pfaults"]["overPower"]             = True

	doc["name"] = "apSSID"

	return flask.jsonify(doc)

if __name__ == '__main__':
	app.run(debug=True)