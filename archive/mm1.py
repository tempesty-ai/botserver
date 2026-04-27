from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# OpenAI API 키 및 Assistant ID 설정
openai.api_key = "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"  # OpenAI API 키
ASSISTANT_ID = "asst_ZzcEXIDjnhij7wTUCwrl7xpb"  # Assistant ID

# Mattermost Slash Command Token (보안을 위해 유효성 검증)
MATTERMOST_TOKEN = "9ztk3ptonpgmjqcez79bg8gtgy"

@app.route('/chat', methods=['GET', 'POST'])
def chat_command():
    # 1. Mattermost 요청 검증
    token = request.form.get('token')
    if token != MATTERMOST_TOKEN:
        return jsonify({"text": "Invalid token."}), 403

    # 2. 사용자가 보낸 메시지 추출
    user_input = request.form.get('text', '').strip()
    if not user_input:
        return jsonify({"text": "Please provide a message after the command."}), 400

    # 3. OpenAI ChatCompletion 호출
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # OpenAI 모델
            messages=[
                {"role": "system", "content": f"You are an assistant with ID: {ASSISTANT_ID}. Respond appropriately."},
                {"role": "user", "content": user_input}
            ]
        )
        ai_response = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return jsonify({"text": f"Error occurred: {str(e)}"}), 500

    # 4. Mattermost에 응답 반환
    return jsonify({
        "response_type": "in_channel",  # 공개 응답
        "text": ai_response
    })

@app.route('/', methods=['GET'])
def home():
    return "Flask server for Mattermost chatbot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
