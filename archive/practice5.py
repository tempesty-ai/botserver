from flask import Flask, request, jsonify
import openai
import requests
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# OpenAI API 키 설정
OPENAI_API_KEY = "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"
ASSISTANT_API_KEY = "asst_ZzcEXIDjnhij7wTUCwrl7xpb"  # Assistant API 키
ASSISTANT_API_URL = "https://platform.openai.com/playground/assistants?assistant=asst_ZzcEXIDjnhij7wTUCwrl7xpb"

# OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY

@app.route('/get_thread_id', methods=['GET'])
def get_thread_id():
    """
    새로운 스레드를 생성하고 스레드 ID를 반환합니다.
    ---
    responses:
      200:
        description: 스레드 ID를 반환합니다.
        schema:
          type: object
          properties:
            thread_id:
              type: string
      500:
        description: 오류가 발생했습니다.
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        # 새로운 스레드를 생성
        thread = openai.beta.threads.create()
        new_thread_id = thread.id
        return jsonify({"thread_id": new_thread_id})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/chat', methods=['POST'])
def slash_command():
    """
    사용자 입력을 받아 Assistant API를 호출합니다.
    ---
    parameters:
      - name: text
        in: formData
        type: string
        required: true
        description: 사용자가 입력한 텍스트
      - name: thread_id
        in: formData
        type: string
        required: true
        description: 사용자가 제공한 thread_id
    responses:
      200:
        description: Assistant API의 응답을 반환합니다.
        schema:
          type: object
          properties:
            response_type:
              type: string
            text:
              type: string
      400:
        description: 잘못된 요청입니다.
        schema:
          type: object
          properties:
            response_type:
              type: string
            text:
              type: string
    """
    # Mattermost에서 받은 요청 데이터
    user_input = request.form.get('text')  # 사용자가 입력한 텍스트
    thread_id = request.form.get('thread_id')  # 사용자가 제공한 thread_id

    if not user_input:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Please provide a query after the /chat command."
        })

    if not thread_id:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Please provide a thread_id."
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
            "thread": thread_id  # 사용자가 제공한 스레드 ID 지정
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
