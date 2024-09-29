from flask import Flask, request, jsonify  # type: ignore
import tensorflow as tf  # type: ignore
import numpy as np  # type: ignore
import ast  # For safely parsing the query parameter string into a Python list
app = Flask(__name__)

model = tf.keras.models.load_model('model.keras')

def pre_process(sequence: list):
    pad = (0, 0, 0, 0)
    iopen = sequence[0][0] if sequence[0][0] != 0 else 2**(-20)
    iclose = sequence[0][1] if sequence[0][1] != 0 else 2**(-20)
    ihigh = sequence[0][2] if sequence[0][2] != 0 else 2**(-20)
    ilow = sequence[0][3] if sequence[0][3] != 0 else 2**(-20)
    initial = sequence[0]
    for i in range(len(sequence)):
        sequence[i] = (((sequence[i][0] - iopen) / iopen) * 10000,
                       ((sequence[i][1] - iclose) / iclose) * 10000,
                       ((sequence[i][2] - ihigh) / ihigh) * 10000,
                       ((sequence[i][3] - ilow) / ilow) * 10000)
    for _ in range(19 - len(sequence)):
        sequence.insert(0, pad)
    return sequence, initial

@app.route('/predict', methods=['GET'])
def pred():
    sequence_str = request.args.get('sequence')

    try:
        sequence = ast.literal_eval(sequence_str)
    except (ValueError, SyntaxError):
        return jsonify({'error': 'Invalid sequence format', 'content': 'Nil'}), 400

    if not isinstance(sequence, list) or not all(isinstance(i, list) and len(i) == 4 for i in sequence):
        return jsonify({'error': 'Invalid sequence format. Expected list of lists with length 4.', 'content':'Nil'}), 400

    altered, initial = pre_process(sequence)
    np_altered = np.array(altered)[np.newaxis, ...]
    prediction = model.predict(np_altered)
    iclose = initial[1]
    scaled = iclose+((prediction*iclose)/10000)
    return jsonify({'error': 'Nil', 'content': scaled.tolist()}),200
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8008)