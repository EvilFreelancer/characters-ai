import json
import os
from ruamel.yaml import YAML
from jinja2 import Template
import openai
from chars.open_ai import openai_batch_completion, OpenAIDecodingArguments

yaml = YAML(typ="rt")
openai.api_key = os.getenv('OPENAI_TOKEN')


def encode_prompt(char, topic, template_path):
    with open(template_path) as f:
        template = Template(f.read())
    fields = ("name", "context", "greeting", "example_dialogue")
    char = {k: v for k, v in char.items() if k in fields}
    return template.render(
        char_json=json.dumps(char, ensure_ascii=False),
        topic=topic
    ).strip() + "\n"


def parse_chat(result):
    try:
        chat = json.loads(result)
    except Exception:
        print("Incorrect JSON:", result)
        return None

    if isinstance(chat, dict):
        keys = list(chat.keys())
        if len(keys) > 1:
            print("Too many keys:", result)
            return None
        key = keys[0]
        chat = chat[key]
    if not isinstance(chat, list):
        print("Not a list:", chat)
        return None

    prev_role = None
    for message in chat:
        if "role" not in message:
            print("No role in message:", message)
            return None
        if "content" not in message:
            print("No content in message:", message)
            return None
        if message["role"] not in ("user", "char"):
            print("Incorrect role:", message)
            return None
        if message["role"] == prev_role:
            print("Two messages from the same role:", chat)
            return None
        prev_role = message["role"]
    return chat


def process_batch(batch, model_name, template_path):
    prompts = [[
        {"role": "user", "content": encode_prompt(char, topic, template_path)}
    ] for char, topic in batch]

    results = openai_batch_completion(
        batch=prompts,
        model_name=model_name,
        decoding_args=OpenAIDecodingArguments(max_tokens=4096)
    )

    dialogues = []
    for (char, topic), prompt, result in zip(batch, prompts, results):
        result = result.message["content"]
        print(result)
        print("=============")
        chat = parse_chat(result)
        if chat is None:
            continue
        chat = {
            "topic": topic,
            "chat": chat,
            "model_name": model_name
        }
        dialogues.append(chat)

    return dialogues


def generate_char_chats(
        input_directory,
        template_path,
        model_name="gpt-3.5-turbo-16k"
):
    if not os.path.isdir(input_directory):
        print(f"The directory {input_directory} does not exist.")
        return

    for filename in os.listdir(input_directory):
        full_path = os.path.join(input_directory, filename)
        if not os.path.isfile(full_path):
            print(f"{filename} is not a file, skip...")
            continue

        # Skip all non-YAML files
        name_without_extension, extension = os.path.splitext(full_path)
        if extension not in ['.yml', '.yaml']:
            print(f"{filename} is not a YAML-file, skip...")
            continue

        # Read details about character
        with open(full_path, 'r', encoding='utf-8') as yaml_file:
            char_data = yaml.load(yaml_file)

        # Generate chats with character
        dialogues = process_batch(
            [(char_data, topic) for topic in char_data["topics"]],
            model_name,
            template_path
        )

        # Update dialogues fields
        if "dialogues" in char_data:
            char_data["dialogues"].extend(dialogues)
        else:
            char_data["dialogues"] = dialogues

        # Save chats to original file
        with open(full_path, 'w', encoding='utf-8') as yaml_file:
            yaml.dump(char_data, yaml_file)


if __name__ == "__main__":
    generate_char_chats(
        'characters',
        'instructs/ru_char_chat.txt'
    )
