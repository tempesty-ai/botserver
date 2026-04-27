from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

# OpenAI API 키 설정
OPENAI_API_KEY = "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"
ASSISTANT_API_KEY = "asst_ZzcEXIDjnhij7wTUCwrl7xpb"  # Assistant API 키
ASSISTANT_API_URL = "https://platform.openai.com/playground/assistants?assistant=asst_ZzcEXIDjnhij7wTUCwrl7xpb&thread=thread_1NDvjQNxL429j96LDKYHUPoz"

THREAD_ID = "thread_1NDvjQNxL429j96LDKYHUPoz"  # 지정된 스레드 ID

# OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY

@app.route('/chat', methods=['POST'])
def slash_command():
    # Mattermost에서 받은 요청 데이터
    user_input = request.form.get('text')  # 사용자가 입력한 텍스트

    if not user_input:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Please provide a query after the /chat command."
        })

    # Assistant API 호출
    try:
        headers = {
            "Authorization": f"Bearer {ASSISTANT_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "input": {
                "type": "text",
                "content": user_input.strip()
            },
            "thread": THREAD_ID  # 스레드 ID 지정
        }

        response = requests.post(ASSISTANT_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            assistant_response = response.json().get("output", {}).get("content", "No response received.")
            return jsonify({
                "response_type": "in_channel",
                "text": assistant_response
            })
        else:
            return jsonify({
                "response_type": "ephemeral",
                "text": f"Assistant API Error: {response.status_code} - {response.text}"
            })

    except Exception as e:
        return jsonify({
            "response_type": "ephemeral",
            "text": f"An error occurred while calling Assistant API: {str(e)}"
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
