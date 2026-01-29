from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import hmac
import hashlib
import os
from datetime import datetime
from database import db, save_event, get_events
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

GITHUB_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', 'your-secret-key')


def verify_github_signature(request):
    """Verify that the request came from GitHub"""
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return False
    
    payload = request.get_data()
    expected_signature = 'sha256=' + hmac.new(
        GITHUB_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')


@app.route('/webhook', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events"""
    
    # Verify GitHub signature
    if not verify_github_signature(request):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Extract event type
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        
        # Initialize event object
        event = None
        
        # Handle PUSH event
        if event_type == 'push':
            event = {
                'request_id': request.headers.get('X-GitHub-Delivery'),
                'author': data['pusher'].get('name', data['pusher'].get('email', 'unknown')),
                'action': 'PUSH',
                'from_branch': None,
                'to_branch': data['ref'].replace('refs/heads/', ''),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        
        # Handle PULL_REQUEST event
        elif event_type == 'pull_request':
            action = data['action'].upper()
            if action in ['OPENED', 'CLOSED', 'REOPENED']:
                event = {
                    'request_id': request.headers.get('X-GitHub-Delivery'),
                    'author': data['pull_request']['user'].get('login', 'unknown'),
                    'action': 'PULL_REQUEST',
                    'from_branch': data['pull_request']['head'].get('ref', 'unknown'),
                    'to_branch': data['pull_request']['base'].get('ref', 'unknown'),
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
        
        # Handle other events as MERGE (when PR is merged)
        elif event_type == 'pull_request' and data.get('action') == 'closed' and data['pull_request'].get('merged'):
            event = {
                'request_id': request.headers.get('X-GitHub-Delivery'),
                'author': data['pull_request']['merged_by'].get('login', 'unknown'),
                'action': 'MERGE',
                'from_branch': data['pull_request']['head'].get('ref', 'unknown'),
                'to_branch': data['pull_request']['base'].get('ref', 'unknown'),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        
        # Save event if it was created
        if event:
            save_event(event)
            return jsonify({'success': True, 'message': f'{event["action"]} event recorded'}), 200
        
        return jsonify({'success': False, 'message': 'Event type not tracked'}), 202
    
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/events', methods=['GET'])
def get_all_events():
    """API endpoint to fetch all events from MongoDB"""
    try:
        print("\n📊 API Call: /api/events")
        
        # Ensure database is initialized
        if db.collection is None:
            print("⚠️ Collection not initialized, initializing...")
            db.init_db()
        
        events = get_events()
        print(f"✅ Retrieved {len(events)} events")
        print(f"Events data: {events}")
        
        response = {'success': True, 'data': events}
        print(f"Sending response: {response}")
        
        return jsonify(response), 200
    except Exception as e:
        print(f"❌ Error fetching events: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    # Initialize database connection first
    print("Initializing MongoDB connection...")
    db.init_db()
    print("✅ MongoDB connection ready!")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
