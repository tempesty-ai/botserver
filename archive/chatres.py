from flask import Flask, request, jsonify
import openai
from time import sleep
import requests
from flasgger import Swagger
from threading import Thread

app = Flask(__name__)
swagger = Swagger(app)

# OpenAI API 키 설정
OPENAI_API_KEY = "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"
ASSISTANT_API_KEY = "asst_ZzcEXIDjnhij7wTUCwrl7xpb"  # Assistant API 키
ASSISTANT_API_URL = "https://platform.openai.com/playground/assistants?assistant=asst_ZzcEXIDjnhij7wTUCwrl7xpb"

# OpenAI API 키 설정
openai.api_key = OPENAI_API_KEY

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def create_thread_service():
    try:
        # 새로운 스레드를 생성
        response = openai.beta.threads.create()
        return response.id
    except Exception as e:
        raise RuntimeError(f"쓰레드를 생성하는 동안 오류가 발생하였습니다: {e}")

def add_message_service(thread_id, message):
    try:
        # 스레드에 메시지 추가
        openai.beta.threads.messages.create(thread_id, role="user", content=message)
        return run_assistant(thread_id)
    except Exception as e:
        raise RuntimeError(f"메시지를 추가하는 동안 오류가 발생하였습니다: {e}")

def run_assistant(thread_id):
    try:
        # 어시스턴트 실행
        response = openai.beta.threads.runs.create(thread_id, assistant_id=ASSISTANT_API_KEY)
        run_id = response.id
        return check_status(thread_id, run_id)
    except Exception as e:
        raise RuntimeError(f"어시스턴트를 실행하는 동안 오류가 발생하였습니다: {e}")

def check_status(thread_id, run_id):
    try:
        while True:
            # 어시스턴트 실행 상태 확인
            run_object = openai.beta.threads.runs.retrieve(run_id, thread_id=thread_id)
            status = run_object.status

            if status == 'completed':
                # 실행 완료 시 메시지 목록 반환
                message_list = openai.beta.threads.messages.list(thread_id)
                return [message.content[0].text.value for message in message_list.data]

            sleep(5)
    except Exception as e:
        raise RuntimeError(f"상태를 확인하는 동안 오류가 발생했습니다: {e}")

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

@app.route('/thread', methods=['GET'])
def thread():
    """
    새로운 스레드를 생성하고 스레드 ID를 반환합니다.
    ---
    tags:
      - OpenAI
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
              description: 오류 메시지
    """
    try:
        # 새로운 스레드를 생성
        thread_id = create_thread_service()
        return jsonify({"thread_id": thread_id})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/chat', methods=['POST'])
def slash_command():
    """
    사용자 입력을 받아 Assistant API를 호출합니다.
    ---
    tags:
      - OpenAI
    parameters:
      - name: text
        in: formData
        type: string
        required: true
        description: 사용자가 입력한 텍스트
    responses:
      200:
        description: Assistant API의 응답을 반환합니다.
        schema:
          type: object
          properties:
            response_type:
              type: string
              description: 응답 유형
            text:
              type: string
              description: Assistant API의 응답 텍스트
      400:
        description: 잘못된 요청입니다.
        schema:
          type: object
          properties:
            response_type:
              type: string
              description: 응답 유형
            text:
              type: string
              description: 오류 메시지
    """
    # Mattermost에서 받은 요청 데이터
    user_input = request.form.get('text')  # 사용자가 입력한 텍스트
    response_url = request.form.get('response_url')  # Mattermost의 응답 URL

    if not user_input:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Please provide a query after the /chat command."
        })

    # 즉각적으로 "답변을 생성 중입니다" 응답 반환
    Thread(target=process_chat, args=(user_input, response_url)).start()

    return jsonify({
        "response_type": "ephemeral",
        "text": "답변을 생성 중입니다. 잠시만 기다려주세요. 챗봇에 답변 내용은 틀릴 수도 있으니 참고만 해주세요."
    })

def process_chat(user_input, response_url):
    """비동기적으로 메시지를 처리하고 Mattermost에 최종 응답을 전송합니다."""
    try:
        thread_id = create_thread_service()
        response = add_message_service(thread_id, user_input)

        # 최종 응답을 Mattermost에 전송
        payload = {
            "response_type": "in_channel",
            "text": response[0]
        }
        headers = {
            "Content-Type": "application/json"
        }
        requests.post(response_url, json=payload, headers=headers)

    except Exception as e:
        payload = {
            "response_type": "ephemeral",
            "text": f"An error occurred while processing your request: {str(e)}"
        }
        requests.post(response_url, json=payload, headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
