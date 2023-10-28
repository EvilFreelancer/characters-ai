import json
import os
import shutil
import openai

from tqdm import tqdm
from jinja2 import Template

from chars.io import write_jsonl, read_jsonl
from chars.open_ai import OpenAIDecodingArguments, openai_batch_completion

openai.api_key = os.getenv('OPENAI_TOKEN')


def encode_prompt(char, template_path):
    with open(template_path) as f:
        template = Template(f.read())
    fields = ("name", "context", "greeting")
    char = {k: v for k, v in char.items() if k in fields}
    return template.render(char_json=json.dumps(char, ensure_ascii=False)).strip() + "\n"


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
        result = result.message["content"]
        # facts = result.split("\n")
        # cleaned_facts = []
        # for fact in facts:
        #     fact = fact.strip()
        #     if not fact:
        #         continue
        #     if not fact[0].isnumeric():
        #         continue
        #     fact = " ".join(fact.strip().split(" ")[1:])
        #     cleaned_facts.append(fact)
        # print(prompt[-1]["content"])
        print(result)
        print()
        print("=============")
        print()
        char["facts"] = result
        chars.append(char)
    return chars


def main(
        chars_path,
        output_path,
        template_path,
        model_name="gpt-3.5-turbo-16k",
        request_batch_size=1
):
    existing_keys = set()
    output_records = []
    if os.path.exists(output_path):
        with open(output_path) as f:
            output_records = [json.loads(line) for line in f]
            existing_keys = {get_char_key(r) for r in output_records}
    print(f"Existing keys: {len(existing_keys)}")

    chars = read_jsonl(chars_path)
    batch = []
    for char in tqdm(chars):
        key = get_char_key(char)
        if key in existing_keys:
            print(f"Skipping {key}")
            continue
        batch.append(char)
        if len(batch) != request_batch_size:
            continue
        updated_chars = process_batch(batch, model_name, template_path)
        output_records.extend(updated_chars)
        batch = []
        write_jsonl(output_records, output_path + "_tmp")
        shutil.move(output_path + "_tmp", output_path)

    if batch:
        updated_chars = process_batch(batch, model_name, template_path)
        output_records.extend(updated_chars)
        write_jsonl(output_records, output_path + "_tmp")
        shutil.move(output_path + "_tmp", output_path)


if __name__ == "__main__":
    main(
        'characters.jsonl',
        'characters_facts.jsonl',
        'instructs/ru_char_facts.txt'
    )
