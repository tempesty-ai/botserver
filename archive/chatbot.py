from flask import Flask, request, jsonify
import openai
from time import sleep
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
    thread_id = create_thread_service()

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

        response = add_message_service(thread_id, user_input);

        return jsonify({
            "response_type": "in_channel",
            "text": response[0]
        })

    except Exception as e:
        return jsonify({
            "response_type": "ephemeral",
            "text": f"An error occurred while calling Assistant API: {str(e)}"
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)