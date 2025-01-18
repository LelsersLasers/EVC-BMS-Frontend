# from flask import Flask, jsonify
import flask
import flask_cors
import random

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.route('/name', methods=['GET'])
def get_plaintext():
	return "apSSID"

@app.route('/data', methods=['GET'])
def get_json():
	def random_voltage():
		return random.random() * (4.4 - 2.8) + 2.8
	def random_temperature():
		return random.random() * (40 - 20) + 20

	doc = {}

	doc["cells"] = []
	for i in range(2):
		doc["cells"].append([])
		for j in range(12):
			doc["cells"][i].append(random_voltage())

	doc["min"] = random_voltage()
	doc["max"] = random_voltage()
	doc["avg"] = random_voltage()
	doc["sum"] = random_voltage() * 12 * 2
	doc["current"] = random.random() * 100

	doc["therm"] = {}
	doc["therm"]["1"] = random_temperature()
	doc["therm"]["2"] = random_temperature()
	doc["therm"]["3"] = random_temperature()
	doc["therm"]["FET"] = random_temperature()

	doc["bypass"] = False # random.choice([True, False])
	doc["anyBypassed"] = False # random.choice([True, False])

	doc["state"] = "Monitor" # random.choice(["Idle", "Charging", "Monitor"])

	doc["SSS"] = False # random.choice([True, False])
	doc["HCS"] = False # random.choice([True, False])

	return flask.jsonify(doc)

if __name__ == '__main__':
	app.run(debug=True)