# GitHub Webhook Event Tracker

A real-time dashboard to track GitHub repository events (PUSH, PULL_REQUEST, MERGE) using webhooks, Flask, and MongoDB.

## Project Structure

```
webhook-repo/
├── app.py                 # Main Flask application
├── database.py            # MongoDB connection and operations
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Environment variables (create from .env.example)
├── templates/
│   └── index.html        # Dashboard UI
└── README.md             # This file
```

## Prerequisites

- **Python 3.8+** installed
- **MongoDB** running locally or accessible via URI
- **GitHub Account** with repository access
- **ngrok** or similar tool to expose local server to internet (for webhooks)

## Installation & Setup

### 1. Clone or Download This Project

```bash
cd webhook-repo
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy the example file
copy .env.example .env

# Edit .env with your settings:
# - MONGODB_URI: Your MongoDB connection string
# - GITHUB_WEBHOOK_SECRET: A random secret for webhook verification
```

### 5. Install MongoDB

**Option A: Local MongoDB**
```bash
# Download from: https://www.mongodb.com/try/download/community
# Follow installation instructions for your OS
```

**Option B: MongoDB Atlas (Cloud)**
```
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account and cluster
3. Get connection string: mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
4. Add to .env: MONGODB_URI=your-connection-string
```

### 6. Run the Flask Application

```bash
python app.py
```

You should see:
```
✓ Connected to MongoDB successfully
✓ Database indexes created
 * Running on http://0.0.0.0:5000
```

## Exposing to Internet (For GitHub Webhooks)

GitHub needs to send webhooks to your server. Use ngrok to expose your local server:

### Install ngrok
```bash
# Download from: https://ngrok.com/download
```

### Run ngrok
```bash
ngrok http 5000
```

You'll get a URL like: `https://abc123.ngrok.io`

## Setting Up GitHub Webhook

### 1. Create `action-repo` (The Repository That Sends Events)

```
Go to GitHub → Create New Repository → Name it "action-repo"
```

### 2. Configure Webhook in action-repo

```
1. Go to: action-repo Settings → Webhooks → Add webhook
2. Payload URL: https://your-ngrok-url.ngrok.io/webhook
3. Content type: application/json
4. Secret: Enter the same secret from your .env file
5. Events: Select:
   - Push events
   - Pull requests
6. Click "Add webhook"
```

### 3. Test the Webhook

```bash
# In your action-repo, do one of these:
1. Make a commit and push (PUSH event)
2. Create a pull request (PULL_REQUEST event)
3. Merge a pull request (MERGE event)
```

## How It Works

1. **GitHub Event** → You perform an action in `action-repo` (push, PR, etc.)
2. **Webhook Sent** → GitHub sends a webhook to your Flask app
3. **Verification** → Flask verifies the webhook signature using GITHUB_WEBHOOK_SECRET
4. **Data Extraction** → Event details are extracted (author, branch, timestamp, etc.)
5. **MongoDB Storage** → Event is saved to MongoDB
6. **UI Display** → Dashboard polls MongoDB every 15 seconds and displays events

## API Endpoints

### Receive Webhook
```
POST /webhook
Headers:
  - X-Hub-Signature-256: GitHub signature
  - X-GitHub-Event: Event type (push, pull_request)
  - X-GitHub-Delivery: Unique delivery ID
Body: GitHub webhook payload
```

### Get Events
```
GET /api/events
Response:
{
  "success": true,
  "data": [
    {
      "request_id": "abc-123",
      "author": "username",
      "action": "PUSH",
      "from_branch": null,
      "to_branch": "main",
      "timestamp": "2024-01-29T10:30:00Z"
    },
    ...
  ]
}
```

### Health Check
```
GET /health
Response: { "status": "healthy" }
```

## MongoDB Schema

Each event stored in MongoDB has:

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | String | Unique GitHub delivery ID (indexed) |
| `author` | String | GitHub username who made the action |
| `action` | String | Action type: PUSH, PULL_REQUEST, or MERGE |
| `from_branch` | String | Source branch (null for PUSH) |
| `to_branch` | String | Target/destination branch |
| `timestamp` | String | ISO 8601 timestamp in UTC |
| `created_at` | DateTime | When the record was created in MongoDB |

## Troubleshooting

### MongoDB Connection Failed
```
Error: "Failed to connect to MongoDB"
Solution: 
1. Check MongoDB is running: mongod (Windows) or brew services start mongodb-community (Mac)
2. Verify MONGODB_URI in .env
3. Check firewall/network access
```

### Webhook Not Being Received
```
Solution:
1. Verify ngrok is running and showing correct URL
2. Check webhook URL in GitHub settings matches ngrok URL
3. Verify secret key matches GITHUB_WEBHOOK_SECRET
4. Check Flask app logs for errors
```

### Events Not Showing in Dashboard
```
Solution:
1. Check browser console for JavaScript errors (F12)
2. Verify /api/events returns data: curl http://localhost:5000/api/events
3. Check MongoDB has events: mongosh → use github_events_db → db.events.find()
4. Make sure browser is not caching (Ctrl+Shift+R to hard refresh)
```

## Development Tips

### View Events in MongoDB
```bash
mongosh
> use github_events_db
> db.events.find().pretty()
> db.events.countDocuments()  # Count total events
```

### Clear All Events (Testing)
```python
# In Python shell or modify app.py temporarily
from database import db
db.init_db()
db.clear_all_events()
```

### Test Webhook Locally
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-GitHub-Delivery: test-123" \
  -d '{"pusher": {"name": "test"}, "ref": "refs/heads/main"}'
```

## Submission Requirements

### Create Two Repositories:

1. **action-repo** - The repository that triggers events
   - Add at least one GitHub Actions workflow (optional)
   - Configure webhook to send events to webhook-repo

2. **webhook-repo** - This project
   - Include all code files
   - Include .env template
   - Include comprehensive README
   - Push working code

## Notes

- The webhook receiver uses HMAC-SHA256 signature verification
- Timestamps are stored in ISO 8601 format (UTC)
- Dashboard auto-refreshes every 15 seconds
- Events are stored with MongoDB indexes for fast queries
- Maximum 50 most recent events displayed (configurable)

## License

Educational - TechStaX Developer Assessment

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Flask logs in terminal
3. Check MongoDB connection
4. Verify GitHub webhook configuration
5. Check ngrok is running and URL is correct
