from openai import OpenAI

openai_api_key = "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"

model = OpenAI(api_key=openai_api_key)
assistant = model.beta.assistants.create(
    name="Math Tutor Example",
    instructions="You are a personal math tutor",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o"
)