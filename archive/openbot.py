from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# OpenAI API Key 설정
OPENAI_API_KEY = "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"

# Mattermost Incoming Webhook URL
INCOMING_WEBHOOK_URL = "https://chat.exem.io/hooks/fbnisbe5kjrxifrjk18nf1ip6r"

@app.route('/mattermost', methods=['POST'])
def mattermost_webhook():
    # Mattermost로부터 요청 데이터 받기
    data = request.json

    # 트리거 단어와 함께 메시지 내용 확인
    if 'text' not in data or not data['text'].startswith('$qwer'):
        return jsonify({'status': 'ignored'}), 200

    user_message = data['text'].replace('$qwer', '').strip()

    # OpenAI API 호출
    openai_response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'gpt-4',
            'messages': [{'role': 'user', 'content': user_message}],
            'temperature': 0.7
        }
    )

    if openai_response.status_code != 200:
        # 에러 발생 시 Mattermost에 에러 메시지 전송
        error_message = f"OpenAI API 호출 에러: {openai_response.status_code}"
        requests.post(INCOMING_WEBHOOK_URL, json={"text": error_message})
        return jsonify({'error': 'OpenAI API Error'}), 500

    # GPT-4 응답 추출
    bot_reply = openai_response.json()['choices'][0]['message']['content']

    # Mattermost로 응답 전송
    requests.post(INCOMING_WEBHOOK_URL, json={"text": bot_reply})

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    # 서버 실행
    app.run(host='0.0.0.0', port=5000)
