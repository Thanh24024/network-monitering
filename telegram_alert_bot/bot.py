from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = '7494031859:AAGGWdgrEE3BVl_WTH4BbPQ-dZmGm09CwRY'
CHAT_ID = '5898979798'

@app.route('/alert', methods=['POST'])
def alert():
    data = request.json
    for alert in data.get('alerts', []):
        msg = f"""🚨 *{alert['labels'].get('alertname')}*
Instance: `{alert['labels'].get('instance')}`
Severity: `{alert['labels'].get('severity')}`
Summary: {alert['annotations'].get('summary')}
Description: {alert['annotations'].get('description')}
Status: *{alert['status']}*
"""
        send_telegram(msg)
    return '', 200

def send_telegram(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
