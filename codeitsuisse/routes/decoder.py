import logging
import json
import itertools
from time import time
from random import choice

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)

@app.route('/decoder', methods=['POST'])
def evaluateDecoder():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    pv = data['possible_values']
    ns = data['num_slots']

    
    # avs = list(itertools.permutations(pv, ns))
    avs = list(itertools.product(pv, repeat=ns))
    r = choice(avs)
    # r = avs[int(time()) % len(avs)]
    outputs = {"answer": list(r)}
    logging.info("My result :{}".format(json.dumps(outputs)))
    return json.dumps(outputs)