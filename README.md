# GitHub Webhook Event Tracker

Real-time dashboard for GitHub events (PUSH, PULL_REQUEST, MERGE) using Flask + MongoDB.

## Quick Setup

### 1. Install Dependencies
```bash
cd webhook-repo
pip install -r requirements.txt
```

### 2. Setup .env
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true
FLASK_ENV=production
```

Get MongoDB connection from: https://mongodb.com/cloud/atlas (free tier)

### 3. Run (3 Terminals)

**Terminal 1 - ngrok:**
```bash
ngrok http 5000
```

**Terminal 2 - Flask:**
```bash
python app.py
```

**Terminal 3 - Push code:**
```bash
cd action-repo
git add . && git commit -m "test" && git push origin main
```

### 4. View Dashboard
```
http://127.0.0.1:5000/
```

## GitHub Webhook Setup

1. `action-repo` → Settings → Webhooks → Add webhook
2. Payload URL: `https://your-ngrok-url/webhook`
3. Events: Push events, Pull requests
4. Save

## How It Works

```
GitHub → Webhook → Flask → MongoDB → Dashboard (updates every 15s)
```

## Database Fields

```json
{
  "author": "username",
  "action": "PUSH | PULL_REQUEST | MERGE",
  "from_branch": "feature-branch",
  "to_branch": "main",
  "timestamp": "2024-01-30T10:30:00Z"
}
```

## API Endpoints

| Path | Purpose |
|------|---------|
| `/` | Dashboard |
| `/api/events` | Get all events |


## Troubleshooting

- **MongoDB fail?** → Check URI in .env
- **Webhook not working?** → Verify ngrok URL in GitHub settings
- **Events not showing?** → Hard refresh (Ctrl+Shift+R)

## Submission

Submit these links:
- https://github.com/yuvrajshete05/action-repo
- https://github.com/yuvrajshete05/webhook-repo

## Tech Stack

Flask | MongoDB Atlas | GitHub Webhooks | ngrok
