from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Mattermost Slash Command 핸들러
@app.route('/chat', methods=['POST'])
def handle_slash_command():
    # Mattermost에서 전송한 데이터
    user_input = request.form.get('text')  # 슬래시 명령어 뒤에 입력된 텍스트
    response_url = request.form.get('response_url')  # Mattermost에서 응답을 전송할 URL (선택적)

    if not user_input:
        return jsonify({
            "response_type": "ephemeral",
            "text": "명령어와 함께 질문을 입력하세요. 예: `/chatgpt Hello!`"
        })

    try:
        # ChatGPT API에 요청
        api_url = "https://chatgpt.com/g/g-673db1688c8c8191b5548e5325b937f3-intermax-caesbos"  # ChatGPT API URL
        api_payload = {"message": user_input}
        headers = {"Content-Type": "application/json"}

        # ChatGPT API 호출
        chatgpt_response = requests.post(api_url, json=api_payload, headers=headers)
        chatgpt_response.raise_for_status()  # 오류 확인

        # ChatGPT의 응답 텍스트
        bot_reply = chatgpt_response.json().get("reply", "ChatGPT로부터 응답이 없습니다.")

        # Mattermost에 반환
        return jsonify({
            "response_type": "in_channel",  # 채널 전체에 표시
            "text": bot_reply
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "response_type": "ephemeral",
            "text": "ChatGPT와 통신 중 오류가 발생했습니다. 나중에 다시 시도해주세요."
        })

# Flask 앱 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




