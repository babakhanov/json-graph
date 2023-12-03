from db import db
from flask import Flask, jsonify, request

graph = db.init_graph('./example.json')

app = Flask('json-graph')

@app.route('/', methods=['POST'])
def find():
    limit = request.args.get('limit', default=30, type=int)
    offset = request.args.get('offset', default=0, type=int)
    return jsonify(db.find(graph, request.json, offset, limit))

@app.route("/props")
def types():
    types = db.get_props(graph)
    return jsonify(types)


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': str(e)}), hasattr(e, 'status_code') and e.status_code or 500

app.run(debug=True)
