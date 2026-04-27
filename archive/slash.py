from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# OpenAI API 키
openai.api_key = 'asst_I9XN5L0KLEtT4rQuFrzRXCDf'

# Mattermost Slash Command Token
MM_SLASH_TOKEN = 'xnhmpu55uf8k5yhttpg45is7ye'

# 기본 경로 (GET 요청 허용)
@app.route('/mattermost', methods=['GET'])
def home():
    return "Flask server is running. Use /chat for Mattermost commands."

# /chat 엔드포인트 (Mattermost Slash Command 처리)
@app.route('/chat', methods=['POST'])
def mattermost_slash():
    # Mattermost 요청 검증
    token = request.form.get('token')
    if token != MM_SLASH_TOKEN:
        return jsonify({"text": "Invalid token."}), 403

    # 사용자가 보낸 메시지
    user_input = request.form.get('text', '')
    print("User Input:", user_input)

    # OpenAI API 호출
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant for Mattermost."},
                {"role": "user", "content": user_input},
            ]
        )
        ai_response = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        ai_response = f"Error: {str(e)}"
        print("Error:", ai_response)

    # Mattermost에 반환
    return jsonify({
        "response_type": "in_channel",  # 채널에 메시지 표시
        "text": ai_response
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
