# Varje endpoint ska kunna ge korrekta HTTP-responskoder vid både framgång och fel, t.ex. 200 (OK), 422 (Unprocessable Entity), 404 (Not Found).

#Get POST PUT DELETE endpoints för CRUD operationer på resurse
#All responses should return either success or failure 200, 422, 404

from flask import jsonify, request, Blueprint
import jsonify

from json_handler import JsonHandler

route_blueprint = Blueprint('route_blueprint', __name__)

#Return 200, 422, 404
@route_blueprint.route('/GetExample', methods=['GET'])
def get_example():

    return jsonify({"message": "This is a GET endpoint example"}), 200

    #Failure 
    return jsonify({"error": "This is a GET endpoint failure example"}), 404


@route_blueprint.route('/PostExample', methods=['POST'])
def post_example():
    data = request.get_json()

    return jsonify({"message": "This is a POST endpoint example", "data_received": data}) 
    #Failure event
    return jsonify({"error": "This is a POST endpoint failure example"}), 422


@route_blueprint.route('/PutExample', methods=['PUT'])
def put_example(): 
    data = request.get_json()
    return jsonify({"message": "This is a PUT endpoint example", "data_received": data})
    #Failure event
    return jsonify({"error": "This is a PUT endpoint failure example"}), 422


@route_blueprint.route('/DeleteExample', methods=['DELETE'])
def delete_example():
    return jsonify({"message": "This is a DELETE endpoint example"})
    #Failure event
    return jsonify({"error": "This is a DELETE endpoint failure example"}), 404