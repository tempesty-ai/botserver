from flask import Flask, request, jsonify
import openai
import requests

app = Flask(__name__)

# OpenAI API 키 설정
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# Mattermost Incoming Webhook URL
MATTERMOST_WEBHOOK_URL = "https://chat.exem.io/hooks/sgtn33nchjrn8r54cmxgsmf5kr"

# Assistant API 설정
ASSISTANT_ID = "asst_EBL9oFbUZXs62VKe6mClfxgo"
ASSISTANT_API_URL = "https://api.openai.com/v1/assistants/interact"

@app.route('/mattermost', methods=['POST'])
def handle_mattermost_message():
    data = request.json
    
    # Mattermost에서 받은 메시지
    text = data.get("text")
    
    if not text:
        return jsonify({"error": "No text found in request"}), 400

    # Assistant API로 메시지 전달 및 응답 받기
    assistant_reply = get_assistant_response(text)

    # Mattermost로 응답 전송
    send_mattermost_response(assistant_reply)
    
    return jsonify({"status": "success"})

def get_assistant_response(user_input):
    # Assistant API 호출
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "assistant_id": ASSISTANT_ID,
        "input": user_input,
    }
    response = requests.post(ASSISTANT_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json().get("response", "No response received from Assistant API.")
    else:
        print(f"Error from Assistant API: {response.status_code} - {response.text}")
        return "Error in getting response from Assistant API."

def send_mattermost_response(message):
    payload = {"text": message}
    headers = {"Content-Type": "application/json"}
    requests.post(MATTERMOST_WEBHOOK_URL, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(port=5000)
