#!/usr/bin/env python3
"""
GitHub Webhook Server for 42cursus Megarepo
Automatically updates submodules when changes are pushed to submodule repositories
"""

import os
import sys
import hmac
import hashlib
import subprocess
import logging
from flask import Flask, request, jsonify
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
REPO_PATH = os.environ.get('REPO_PATH', '/home/user/42cursus')
GIT_BRANCH = os.environ.get('GIT_BRANCH', 'claude/github-webhook-submodules-SFaoA')
ENABLE_AUTO_PUSH = os.environ.get('ENABLE_AUTO_PUSH', 'true').lower() == 'true'

# Mapping of repository URLs to submodule paths
SUBMODULE_MAP = {
    'naokiiida/get_next_line': 'get_next_line',
    'naokiiida/born2beroot': 'born2beroot',
    'naokiiida/push_swap': 'push_swap',
    'naokiiida/ft_printf': 'ft_printf',
    'naokiiida/libft': 'libft',
    'naokiiida/minitalk': 'minitalk',
    'naokiiida/fractol': 'fractol',
    'naokiiida/pipex': 'pipex',
    'naokiiida/minishell': 'minishell',
    'naokiiida/philosophers': 'philosophers',
    'naokiiida/cub3d': 'cub3d',
    'Shunpei0902/ft_irc': 'ft_irc',
    'naokiiida/inception': 'inception',
    'naokiiida/cpp00': 'cpp00',
    'naokiiida/cpp01': 'cpp01',
    'naokiiida/cpp02': 'cpp02',
    'naokiiida/cpp03': 'cpp03',
    'naokiiida/cpp04': 'cpp04',
    'naokiiida/cpp05': 'cpp05',
    'naokiiida/cpp06': 'cpp06',
}


def verify_signature(payload_body, signature_header):
    """Verify GitHub webhook signature"""
    if not WEBHOOK_SECRET:
        logger.warning("No webhook secret configured - skipping signature verification")
        return True

    if not signature_header:
        logger.error("No signature header received")
        return False

    hash_algorithm, github_signature = signature_header.split('=')
    algorithm = hashlib.sha256 if hash_algorithm == 'sha256' else hashlib.sha1

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload_body,
        algorithm
    ).hexdigest()

    return hmac.compare_digest(expected_signature, github_signature)


def run_git_command(command, cwd=None):
    """Execute a git command and return the result"""
    if cwd is None:
        cwd = REPO_PATH

    try:
        logger.info(f"Executing: {' '.join(command)} in {cwd}")
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Command output: {result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return False, e.stderr


def update_submodule(submodule_path, repo_name):
    """Update a specific submodule and commit the change"""
    logger.info(f"Starting update for submodule: {submodule_path}")

    # Change to repo directory
    os.chdir(REPO_PATH)

    # Ensure we're on the correct branch
    success, output = run_git_command(['git', 'checkout', GIT_BRANCH])
    if not success:
        logger.error(f"Failed to checkout branch {GIT_BRANCH}")
        return False, "Failed to checkout branch"

    # Pull latest changes from remote
    success, output = run_git_command(['git', 'pull', 'origin', GIT_BRANCH])
    if not success:
        logger.warning(f"Failed to pull latest changes: {output}")

    # Update the submodule to latest commit
    success, output = run_git_command([
        'git', 'submodule', 'update', '--remote', '--merge', submodule_path
    ])
    if not success:
        return False, f"Failed to update submodule: {output}"

    # Check if there are changes to commit
    success, status_output = run_git_command(['git', 'status', '--porcelain'])
    if not status_output.strip():
        logger.info("No changes to commit")
        return True, "Submodule already up to date"

    # Stage the submodule change
    success, output = run_git_command(['git', 'add', submodule_path])
    if not success:
        return False, f"Failed to stage changes: {output}"

    # Create commit message
    commit_message = f"Update {submodule_path} submodule\n\nAutomatically updated via webhook from {repo_name}"

    # Commit the change
    success, output = run_git_command(['git', 'commit', '-m', commit_message])
    if not success:
        return False, f"Failed to commit changes: {output}"

    # Push to remote if auto-push is enabled
    if ENABLE_AUTO_PUSH:
        success, output = run_git_command(['git', 'push', '-u', 'origin', GIT_BRANCH])
        if not success:
            logger.error(f"Failed to push changes: {output}")
            return False, f"Changes committed but push failed: {output}"
        logger.info("Successfully pushed changes to remote")
    else:
        logger.info("Auto-push disabled - changes committed locally only")

    return True, "Submodule updated successfully"


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook POST requests"""
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256') or request.headers.get('X-Hub-Signature')
    if not verify_signature(request.data, signature):
        logger.error("Invalid webhook signature")
        return jsonify({'error': 'Invalid signature'}), 403

    # Get event type
    event_type = request.headers.get('X-GitHub-Event')
    logger.info(f"Received webhook event: {event_type}")

    # Only process push events
    if event_type != 'push':
        logger.info(f"Ignoring event type: {event_type}")
        return jsonify({'message': 'Event ignored'}), 200

    # Parse payload
    payload = request.json

    # Extract repository information
    repo_full_name = payload.get('repository', {}).get('full_name', '')
    ref = payload.get('ref', '')

    logger.info(f"Push event from {repo_full_name} to {ref}")

    # Check if this is a submodule we track
    if repo_full_name not in SUBMODULE_MAP:
        logger.info(f"Repository {repo_full_name} is not a tracked submodule")
        return jsonify({'message': 'Repository not tracked'}), 200

    submodule_path = SUBMODULE_MAP[repo_full_name]

    # Update the submodule
    success, message = update_submodule(submodule_path, repo_full_name)

    if success:
        logger.info(f"Successfully processed webhook for {repo_full_name}")
        return jsonify({
            'message': message,
            'submodule': submodule_path,
            'repository': repo_full_name
        }), 200
    else:
        logger.error(f"Failed to process webhook for {repo_full_name}: {message}")
        return jsonify({
            'error': message,
            'submodule': submodule_path,
            'repository': repo_full_name
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'repo_path': REPO_PATH,
        'branch': GIT_BRANCH,
        'auto_push_enabled': ENABLE_AUTO_PUSH,
        'tracked_submodules': len(SUBMODULE_MAP)
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Index page with basic information"""
    return jsonify({
        'service': 'GitHub Webhook Server for 42cursus',
        'endpoints': {
            '/webhook': 'POST - GitHub webhook receiver',
            '/health': 'GET - Health check',
            '/': 'GET - This page'
        },
        'tracked_submodules': list(SUBMODULE_MAP.keys())
    }), 200


if __name__ == '__main__':
    logger.info("Starting webhook server...")
    logger.info(f"Repository path: {REPO_PATH}")
    logger.info(f"Target branch: {GIT_BRANCH}")
    logger.info(f"Auto-push enabled: {ENABLE_AUTO_PUSH}")
    logger.info(f"Tracking {len(SUBMODULE_MAP)} submodules")

    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')

    app.run(host=host, port=port, debug=False)
