from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
import time

app = FastAPI()

# OpenAI API 설정
client = OpenAI(api_key="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")
ASSISTANT_ID = "asst_ZzcEXIDjnhij7wTUCwrl7xpb"

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message,
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    return run

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(ASSISTANT_ID, thread, user_input)
    return thread, run

@app.post("/chat")
async def chat_command(
    token: str = Form(...),
    text: str = Form(...),
    user_name: str = Form(...),
):
    # Mattermost 토큰 인증
    if token != "9ztk3ptonpgmjqcez79bg8gtgy":
        raise HTTPException(status_code=403, detail="Invalid token")
    
    # GPT Assistant 실행
    thread, run = create_thread_and_run(text)
    run = wait_on_run(run, thread)
    response = get_response(thread)
    
    # 응답 메시지 처리
    if response and response[-1].role == "assistant":
        gpt_reply = response[-1].content
        return JSONResponse(
            {
                "response_type": "in_channel",  # or "ephemeral" for private response
                "text": f"**{user_name}**, here's my response: {gpt_reply}"
            }
        )
    else:
        return JSONResponse(
            {"response_type": "ephemeral", "text": "Sorry, I couldn't process your request."}
        )

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
