import time
from openai import OpenAI


# 이전에 설정한 Assistant ID 를 기입합니다.
ASSISTANT_ID = "asst_ZzcEXIDjnhij7wTUCwrl7xpb"

# OpenAI API를 사용하기 위한 클라이언트 객체를 생성합니다.
client = OpenAI(api_key="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")


def submit_message(assistant_id, thread, user_message):
    # 사용자 입력 메시지를 스레드에 추가합니다.
    client.beta.threads.messages.create(
        # Thread ID가 필요합니다.
        # 사용자 입력 메시지 이므로 role은 "user"로 설정합니다.
        # 사용자 입력 메시지를 content에 지정합니다.
        thread_id=thread.id,
        role="user",
        content=user_message,
    )
    # 스레드에 메시지가 입력이 완료되었다면,
    # Assistant ID와 Thread ID를 사용하여 실행을 준비합니다.
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    return run


def wait_on_run(run, thread):
    # 주어진 실행(run)이 완료될 때까지 대기합니다.
    # status 가 "queued" 또는 "in_progress" 인 경우에는 계속 polling 하며 대기합니다.
    while run.status == "queued" or run.status == "in_progress":
        # run.status 를 업데이트합니다.
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        # API 요청 사이에 잠깐의 대기 시간을 두어 서버 부하를 줄입니다.
        time.sleep(0.5)
    return run


def get_response(thread):
    # 스레드에서 메시지 목록을 가져옵니다.
    # 메시지를 오름차순으로 정렬할 수 있습니다. order="asc"로 지정합니다.
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


def create_thread_and_run(user_input):
    # 사용자 입력을 받아 새로운 스레드를 생성하고, Assistant 에게 메시지를 제출합니다.
    thread = client.beta.threads.create()
    run = submit_message(ASSISTANT_ID, thread, user_input)
    return thread, run


thread1, run1 = create_thread_and_run(
    "다음 방정식을 풀고 싶습니다. `3x + 11 = 14`. 좀 도와주실 수 있나요?"
)
thread2, run2 = create_thread_and_run("선형대수에 대해 간략히 설명해 주실 수 있나요?")
thread3, run3 = create_thread_and_run(
    "수학에 정말 소질이 없는 것 같아요. 어떻게 하면 수학을 잘할 수 있을까요?"
)

import time


# 메시지 출력용 함수
def print_message(response):
    for res in response:
        print(f"[{res.role.upper()}]\n{res.content[0].text.value}\n")
    print("---" * 20)


# 반복문에서 대기하는 함수


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


# 첫 번째 실행을 위해 대기
run1 = wait_on_run(run1, thread1)
print_message(get_response(thread1))

# 두 번째 실행을 위해 대기
run2 = wait_on_run(run2, thread2)
print_message(get_response(thread2))

# 세 번째 실행을 위해 대기
run3 = wait_on_run(run3, thread3)
# 세 번째 스레드를 마치면 감사 인사를 전하고 종료합니다 :)
run4 = submit_message(ASSISTANT_ID, thread3, "도와주셔서 감사합니다!")
run4 = wait_on_run(run4, thread3)



print_message(get_response(thread3))

