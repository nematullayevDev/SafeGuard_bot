module.exports = {
  apps: [
    {
      name: 'safeguard-bot',
      script: 'main.py',
      interpreter: 'python3',
      restart_delay: 5000,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONUNBUFFERED: '1',
      }
    }
  ]
};
