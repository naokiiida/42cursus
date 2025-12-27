# Quick Start Guide - GitHub Webhook Integration

Get your webhook server running in 5 minutes!

## Prerequisites

- Python 3.7+ or Docker
- Git configured with SSH access to this repository
- A server with a public IP or ngrok for testing

## Step 1: Generate a Secret

```bash
openssl rand -hex 32
```

Copy this value - you'll need it in the next steps.

## Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your webhook secret
nano .env
```

Set at minimum:
```
WEBHOOK_SECRET=<your_secret_from_step_1>
```

## Step 3: Start the Server

### Option A: Docker (Easiest)

```bash
docker-compose up -d
```

### Option B: Python

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the server
python3 webhook_server.py
```

## Step 4: Make Server Accessible

### For Production
Deploy on a server with a public IP and use that IP in your webhook URL.

### For Testing (Using ngrok)
```bash
# In a new terminal
ngrok http 5000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

## Step 5: Configure GitHub Webhooks

### Automated Setup (Recommended)

```bash
./setup_webhooks.sh
```

Enter your webhook URL and secret when prompted.

### Manual Setup

For each submodule repository:

1. Go to `https://github.com/USERNAME/REPO/settings/hooks`
2. Click "Add webhook"
3. Set:
   - **Payload URL**: `https://your-server.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: Your webhook secret
   - **Events**: Just the push event
4. Click "Add webhook"

## Step 6: Test It!

```bash
# Test the server
./test_webhook.sh

# Or manually
curl http://localhost:5000/health
```

Push a commit to any submodule repository and watch the magic happen!

## Monitoring

View logs:

```bash
# Docker
docker-compose logs -f

# Python
tail -f webhook.log
```

## Troubleshooting

### Server won't start
- Check if port 5000 is available: `lsof -i :5000`
- Verify Python dependencies are installed
- Check .env file exists and has correct values

### Webhooks not triggering
- Verify the webhook URL is publicly accessible
- Check GitHub webhook delivery status in repo settings
- Ensure webhook secret matches between .env and GitHub

### Submodules not updating
- Check server logs for errors
- Verify git credentials are configured
- Ensure the branch exists and you have push permissions

## Next Steps

- Set up a reverse proxy with SSL (nginx/Caddy)
- Configure monitoring and alerting
- Review the full [README.md](README.md) for advanced configuration

## Common Commands

```bash
# View server status
docker-compose ps

# Restart server
docker-compose restart

# Stop server
docker-compose down

# Manually update all submodules
./update_all_submodules.sh

# View recent commits
git log --oneline -10
```

## Need Help?

Check the detailed [README.md](README.md) for:
- Architecture details
- Security considerations
- Advanced configuration
- Detailed troubleshooting

---

Happy coding! 🚀
