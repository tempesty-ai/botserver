from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# OpenAI API 키
openai.api_key = "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"  # 실제 API 키로 교체하세요


# Mattermost Slash Command Token (보안을 위해 실제 값 사용)
MM_SLASH_TOKEN = '9ztk3ptonpgmjqcez79bg8gtgy'

@app.route('/chat', methods=['POST'])
def mattermost_slash():
    # Mattermost 요청 검증 (토큰 확인)
    token = request.form.get('token')
    if token != MM_SLASH_TOKEN:
        return jsonify({"text": "Invalid token."}), 403

    # 사용자가 보낸 메시지 (Slash Command 뒤의 텍스트)
    user_input = request.form.get('text', '')
    print("User Input:", user_input)

    # 사용자가 텍스트를 입력하지 않은 경우 처리
    if not user_input:
        return jsonify({"text": "Please provide input after the command."}), 400

    # OpenAI API 호출
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 사용할 모델 (gpt-3.5-turbo 또는 다른 모델 선택)
            messages=[
                {"role": "system", "content": "You are an assistant for Mattermost."},
                {"role": "user", "content": user_input}  # 사용자가 입력한 메시지
            ]
        )
        # OpenAI 응답에서 텍스트 추출
        ai_response = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        ai_response = f"Error: {str(e)}"
        print("Error:", ai_response)

    # Mattermost에 반환할 데이터
    return jsonify({
        "response_type": "in_channel",  # 메시지를 채널에 공개
        "text": ai_response  # OpenAI의 응답을 사용자에게 전달
    })

@app.route('/mattermost', methods=['GET'])
def home():
    return "Flask server is running. Use /chat for Mattermost commands."

if __name__ == '__main__':
    app.run(debug=True, port=5000)
