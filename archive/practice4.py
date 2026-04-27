from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def slash_command():
    # Mattermost에서 전송된 데이터를 로그로 확인
    data = request.form
    print("Received data:", data)
    
    # 응답 데이터 구성
    response = {
        "response_type": "in_channel",  # 'in_channel'은 공개 응답, 'ephemeral'은 개인 응답
        "text": "\n#### Test results for July 27th, 2017\n@channel here are the requested test results.\n\n"
                "| Component  | Tests Run   | Tests Failed                                   |\n"
                "| ---------- | ----------- | ---------------------------------------------- |\n"
                "| Server     | 948         | ✅ 0                           |\n"
                "| Web Client | 123         | ⚠️ 2 [(see details)](http://linktologs) |\n"
                "| iOS Client | 78          | ⚠️ 3 [(see details)](http://linktologs) |\n",
        "username": "test-automation",
        "icon_url": "https://www.mattermost.org/wp-content/uploads/2016/04/icon.png",
        "props": {
            "test_data": {
                "ios": 78,
                "server": 948,
                "web": 123
            }
        },
        "extra_responses": [
            {
                "text": "message 2",
                "username": "test-automation"
            },
            {
                "text": "message 3",
                "username": "test-automation"
            }
        ]
    }

    # JSON 응답 반환
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
