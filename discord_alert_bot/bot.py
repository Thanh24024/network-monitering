from flask import Flask, request
import requests

app = Flask(__name__)

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1329267219514916989/qCOWZooQUZUxQ5ccZX2mbD_UeO8avhZGSWsuM6iRcQ07xmrFRWFRcUr-q3skGFcSP0PX'

@app.route('/alert', methods=['POST'])
def alert():
    data = request.json
    for alert in data.get('alerts', []):
        msg = f"""🚨 **{alert['labels'].get('alertname')}**
**Instance**: `{alert['labels'].get('instance')}`
**Severity**: `{alert['labels'].get('severity')}`
**Summary**: {alert['annotations'].get('summary')}
**Description**: {alert['annotations'].get('description')}
**Status**: **{alert['status']}**
"""
        send_discord(msg)
    return '', 200

def send_discord(message):
    payload = {
        "content": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
