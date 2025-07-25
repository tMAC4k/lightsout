from flask import Flask, jsonify, request, send_file
import os
from datetime import datetime

app = Flask(__name__)

FIRMWARE_DIR = '/firmware'

@app.route('/firmware/latest', methods=['GET'])
def get_latest_firmware():
    try:
        # Get latest firmware file
        files = [f for f in os.listdir(FIRMWARE_DIR) if f.endswith('.bin')]
        if not files:
            return jsonify({'update_available': False}), 200
        
        latest = max(files, key=lambda f: os.path.getctime(os.path.join(FIRMWARE_DIR, f)))
        
        return jsonify({
            'update_available': True,
            'version': latest.split('.')[0],
            'filename': latest,
            'size': os.path.getsize(os.path.join(FIRMWARE_DIR, latest)),
            'date': datetime.fromtimestamp(
                os.path.getctime(os.path.join(FIRMWARE_DIR, latest))
            ).isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/firmware/download/<filename>', methods=['GET'])
def download_firmware(filename):
    try:
        return send_file(
            os.path.join(FIRMWARE_DIR, filename),
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/telemetry', methods=['POST'])
def receive_telemetry():
    data = request.get_json()
    # Process telemetry data (implement as needed)
    print(f"Received telemetry: {data}")
    return jsonify({'status': 'received'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
