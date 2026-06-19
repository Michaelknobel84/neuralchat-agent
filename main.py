services:
  - type: web
    name: neuralchat-agent
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn main:app --bind 0.0.0.0:$PORT
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
