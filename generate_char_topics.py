import json
import os
import openai
from ruamel.yaml import YAML
from jinja2 import Template
from chars.open_ai import OpenAIDecodingArguments, openai_batch_completion

yaml = YAML(typ="rt")
openai.api_key = os.getenv('OPENAI_TOKEN')


def encode_prompt(char, template_path):
    with open(template_path) as f:
        template = Template(f.read())
    fields = ("name", "context", "greeting", "example_dialogue", "topics")
    char = {k: v for k, v in char.items() if k in fields}
    return template.render(
        char_json=json.dumps(char, ensure_ascii=False)
    ).strip() + "\n"


def get_char_key(char):
    return char["name"].strip(), char["context"].strip()


def process_batch(batch, model_name, template_path):
    prompts = [[
        {"role": "user", "content": encode_prompt(r, template_path)}
    ] for r in batch]

    results = openai_batch_completion(
        batch=prompts,
        model_name=model_name,
        decoding_args=OpenAIDecodingArguments(max_tokens=5033)
    )

    chars = []
    for char, prompt, result in zip(batch, prompts, results):
        print(f"Character: {char['name']}")
        result = result.message["content"]
        topics = result.split("\n")
        cleaned_topics = []
        for topic in topics:
            topic = topic.strip()
            if not topic:
                continue
            if not topic[0].isnumeric():
                continue
            topic = " ".join(topic.strip().split(" ")[1:])
            cleaned_topics.append(topic)
        # print(prompt[-1]["content"])
        print(cleaned_topics)
        print("=============")
        if "topics" in char:
            char["topics"] += cleaned_topics
        else:
            char["topics"] = cleaned_topics
        chars.append(char)
    return chars


def generate_char_topics(
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

        # Skip all non-topics files
        name_without_extension, extension = os.path.splitext(full_path)
        if extension in ['.yml', '.yaml']:
            # Read details about character
            with open(full_path, 'r', encoding='utf-8') as yaml_file:
                yaml_content = yaml.load(yaml_file)
            # Generate topics based on context
            updated_char = process_batch([yaml_content], model_name, template_path)[0]
            # Save topics to original file
            with open(full_path, 'w', encoding='utf-8') as yaml_file:
                yaml.dump(updated_char, yaml_file)
                # print(f"File {filename} successfully updated.")


if __name__ == "__main__":
    generate_char_topics(
        'characters',
        'instructs/ru_char_topics.txt'
    )
