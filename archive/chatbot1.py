from quart import Quart, request, jsonify
import asyncio
import openai

app = Quart(__name__)

OPENAI_API_KEY = "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"
ASSISTANT_API_KEY = "asst_ZzcEXIDjnhij7wTUCwrl7xpb"

openai.api_key = OPENAI_API_KEY


async def create_thread_service():
    try:
        response = await asyncio.to_thread(openai.beta.threads.create)
        return response.id
    except Exception as e:
        raise RuntimeError(f"쓰레드를 생성하는 동안 오류가 발생하였습니다: {e}")


async def add_message_service(thread_id, message):
    try:
        await asyncio.to_thread(openai.beta.threads.messages.create, thread_id, role="user", content=message)
        return await run_assistant(thread_id)
    except Exception as e:
        raise RuntimeError(f"메시지를 추가하는 동안 오류가 발생하였습니다: {e}")


async def run_assistant(thread_id):
    try:
        response = await asyncio.to_thread(openai.beta.threads.runs.create, thread_id, assistant_id=ASSISTANT_API_KEY)
        run_id = response.id
        return await check_status(thread_id, run_id)
    except Exception as e:
        raise RuntimeError(f"어시스턴트를 실행하는 동안 오류가 발생하였습니다: {e}")


async def check_status(thread_id, run_id):
    try:
        while True:
            run_object = await asyncio.to_thread(openai.beta.threads.runs.retrieve, run_id, thread_id=thread_id)
            if run_object.status == 'completed':
                message_list = await asyncio.to_thread(openai.beta.threads.messages.list, thread_id)
                return [message.content[0].text.value for message in message_list.data]
            await asyncio.sleep(1)
    except Exception as e:
        raise RuntimeError(f"상태를 확인하는 동안 오류가 발생하였습니다: {e}")


@app.route('/chat', methods=['POST'])
async def slash_command():
    user_input = (await request.form).get('text')
    if not user_input:
        return jsonify({"response_type": "ephemeral", "text": "Please provide a query."})

    try:
        thread_id = await create_thread_service()
        response = await add_message_service(thread_id, user_input)
        return jsonify({"response_type": "in_channel", "text": response[0]})
    except Exception as e:
        return jsonify({"response_type": "ephemeral", "text": f"Error: {e}"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
