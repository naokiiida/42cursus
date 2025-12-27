# 42cursus Megarepo

This repository contains all 42 school projects as git submodules, with automatic webhook integration to keep submodules up to date.

## Submodules

This megarepo tracks the following projects:

- libft
- get_next_line
- ft_printf
- born2beroot
- push_swap
- minitalk
- fractol
- pipex
- minishell
- philosophers
- cub3d
- ft_irc
- inception
- cpp00-cpp06

## GitHub Webhook Integration

This repository includes an automated webhook server that keeps all submodules up to date when changes are pushed to individual project repositories.

### How It Works

1. When you push changes to any submodule repository, GitHub sends a webhook event
2. The webhook server receives the event and identifies which submodule was updated
3. The server automatically updates the submodule to the latest commit
4. Changes are committed and pushed to this megarepo

### Setup Instructions

#### 1. Generate a Webhook Secret

```bash
openssl rand -hex 32
```

Save this secret - you'll need it for both the server configuration and GitHub webhook settings.

#### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```bash
WEBHOOK_SECRET=your_generated_secret_here
REPO_PATH=/home/user/42cursus
GIT_BRANCH=claude/github-webhook-submodules-SFaoA
ENABLE_AUTO_PUSH=true
```

#### 3. Deploy the Webhook Server

You have three deployment options:

##### Option A: Docker (Recommended)

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

##### Option B: Systemd Service

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Copy service file
sudo cp webhook.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Start the service
sudo systemctl start webhook

# Enable on boot
sudo systemctl enable webhook

# Check status
sudo systemctl status webhook

# View logs
sudo journalctl -u webhook -f
```

##### Option C: Direct Python

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the server
python3 webhook_server.py
```

#### 4. Configure GitHub Webhooks

For **each** submodule repository, you need to set up a webhook:

1. Go to the repository on GitHub (e.g., `https://github.com/naokiiida/libft`)
2. Click **Settings** → **Webhooks** → **Add webhook**
3. Configure the webhook:
   - **Payload URL**: `http://your-server-ip:5000/webhook`
   - **Content type**: `application/json`
   - **Secret**: Enter the webhook secret you generated
   - **Which events**: Select "Just the push event"
   - **Active**: Check this box
4. Click **Add webhook**

Repeat this process for all 20 submodule repositories:

- `naokiiida/libft`
- `naokiiida/get_next_line`
- `naokiiida/ft_printf`
- `naokiiida/born2beroot`
- `naokiiida/push_swap`
- `naokiiida/minitalk`
- `naokiiida/fractol`
- `naokiiida/pipex`
- `naokiiida/minishell`
- `naokiiida/philosophers`
- `naokiiida/cub3d`
- `Shunpei0902/ft_irc`
- `naokiiida/inception`
- `naokiiida/cpp00`
- `naokiiida/cpp01`
- `naokiiida/cpp02`
- `naokiiida/cpp03`
- `naokiiida/cpp04`
- `naokiiida/cpp05`
- `naokiiida/cpp06`

#### 5. Make Your Server Publicly Accessible

GitHub needs to reach your webhook server. You have several options:

##### Option A: Public Server

Deploy on a cloud server (AWS, DigitalOcean, etc.) with a public IP.

##### Option B: ngrok (for testing)

```bash
# Install ngrok
# Visit https://ngrok.com/ and follow installation instructions

# Start ngrok tunnel
ngrok http 5000

# Use the HTTPS URL provided by ngrok as your webhook URL
# Example: https://abc123.ngrok.io/webhook
```

##### Option C: Cloudflare Tunnel

```bash
# Install cloudflared
# Visit https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# Create tunnel
cloudflared tunnel --url http://localhost:5000
```

### Testing the Webhook

#### Test the Server

Check if the server is running:

```bash
curl http://localhost:5000/health
```

You should see a JSON response with server status.

#### Test a Webhook

1. Push a commit to one of your submodule repositories
2. Check the webhook delivery in GitHub:
   - Go to repository → Settings → Webhooks
   - Click on your webhook
   - View "Recent Deliveries"
3. Check the webhook server logs to see the update process

### Monitoring

#### View Logs

Docker:
```bash
docker-compose logs -f webhook-server
```

Systemd:
```bash
sudo journalctl -u webhook -f
```

Direct:
```bash
tail -f webhook.log
```

#### Health Check

```bash
curl http://localhost:5000/health
```

### Security Considerations

1. **Webhook Secret**: Always use a strong, random webhook secret
2. **Firewall**: Only allow incoming connections to port 5000 from GitHub's webhook IPs
3. **HTTPS**: Use a reverse proxy (nginx, Caddy) with SSL/TLS for production
4. **Git Credentials**: Ensure the server has proper SSH keys or credentials to push to the megarepo

### Troubleshooting

#### Webhook Not Triggering

1. Check GitHub webhook delivery status
2. Verify the webhook URL is correct and accessible
3. Check server logs for errors
4. Verify webhook secret matches

#### Submodule Not Updating

1. Check if the repository is in the SUBMODULE_MAP in `webhook_server.py`
2. Verify git credentials are configured correctly
3. Check branch permissions
4. Review server logs for git command errors

#### Push Failing

1. Verify the server has permission to push to the megarepo
2. Check SSH keys or credentials
3. Verify the branch exists and is not protected
4. Check git logs: `git log --oneline -10`

### Manual Submodule Management

Update all submodules manually:

```bash
git submodule update --remote --merge
git add .
git commit -m "Update all submodules"
git push
```

Update a specific submodule:

```bash
git submodule update --remote --merge <submodule-path>
git add <submodule-path>
git commit -m "Update <submodule-name>"
git push
```

### Architecture

```
┌─────────────────┐
│  Submodule Repo │
│   (e.g. libft)  │
└────────┬────────┘
         │ push event
         ▼
┌─────────────────┐
│ GitHub Webhook  │
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────┐
│ Webhook Server  │
│  (Flask App)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Git Commands   │
│ - Update sub    │
│ - Commit        │
│ - Push          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Megarepo      │
│   (42cursus)    │
└─────────────────┘
```

### API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /webhook` - GitHub webhook receiver

### Contributing

When adding new submodules:

1. Add the submodule to the repository:
   ```bash
   git submodule add <url> <path>
   ```

2. Update `SUBMODULE_MAP` in `webhook_server.py`:
   ```python
   'username/repo-name': 'local-path',
   ```

3. Configure the webhook on the new repository

4. Restart the webhook server

## License

Educational project for 42 school.
