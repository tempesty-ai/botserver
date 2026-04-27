from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Mattermost Incoming Webhook URL
incoming_webhook_url = "https://chat.exem.io/hooks/fbnisbe5kjrxifrjk18nf1ip6r"

@app.route('/')
def home():
    return "Flask Webhook Server is Running!"

# Outgoing Webhook 처리
@app.route('/mattermost', methods=['GET', 'POST'])
def outgoing_webhook():
    print("Webhook endpoint hit!")
    if request.method == 'GET':
        # GET 요청에 대해 안내 메시지 반환
        return "This endpoint only supports POST requests for Mattermost Webhooks. Please use POST to send data.", 200

    # POST 요청 처리
    data = request.json  # JSON 데이터로 받음
    if not data:
        print("No data received from Mattermost")
        return "No data received", 400

    # Mattermost에서 보낸 데이터 출력
    print("Outgoing Webhook Data:", data)

    # 사용자가 보낸 메시지와 보안 토큰 확인
    user_message = data.get('text', '')  # 사용자가 보낸 메시지
    token = data.get('token', '')  # Mattermost Webhook Token

    # 토큰 검증
    if token != "9gzbm7dc7brt8robg535nze84a":
        print(f"Invalid token received: {token}")
        return "Invalid token", 403

    # 트리거 단어 확인
    if not user_message.startswith('$qwer'):
        print(f"Message does not start with trigger word: {user_message}")
        return "No trigger word matched", 200

    # 트리거 단어를 제거하고 메시지 처리
    user_message = user_message[len('$qwer'):].strip()

    # 사용자가 보낸 메시지에 따라 응답 결정
    if "hello" in user_message.lower():
        response_message = "Hi there! How can I help you?"
    elif "bye" in user_message.lower():
        response_message = "Goodbye! Have a nice day!"
    else:
        response_message = f"You said: {user_message}"

    # Mattermost Incoming Webhook으로 응답 보내기
    response_payload = {
        "response_type": "in_channel",  # 채널에 메시지를 보이게 설정
        "text": response_message
    }
    print(f"Sending response to Mattermost Incoming Webhook: {response_message}")

    # Mattermost로 응답 전송
    response = requests.post(incoming_webhook_url, json=response_payload)

    # 응답 성공 여부 확인
    if response.status_code == 200:
        print("Response successfully sent to Mattermost.")
    else:
        print(f"Failed to send response to Mattermost. Status Code: {response.status_code}, Response: {response.text}")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
