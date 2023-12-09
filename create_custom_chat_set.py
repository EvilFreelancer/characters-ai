import json
import sys
import random

random.seed(42)


def calc_max_length(records):
    return max([sum([len(m["content"]) for m in r["messages"]]) for r in records])


def build_char_system_messages(char):
    name = char["name"]
    greeting = char["greeting"]
    example_dialogue = char["example_dialogue"]

    context = ""
    if random.random() < 0.5:
        context += f"Ты - {name}. "
    context += f"{char['context']}"
    chat = []
    if random.random() < 0.2:
        context += f"\nПриветствие: {greeting}"
        chat.append({
            "role": "bot",
            "content": greeting
        })
    if random.random() < 0.2:
        mapping = {
            "user": "Пользователь",
            "bot": "Персонаж"
        }
        print(example_dialogue)
        example_messages = [f'{mapping[m["role"]]}: {m["content"]}' for m in example_dialogue]
        context += "\nПример диалога:\n" + "\n".join(example_messages)
    chat.insert(0, {
        "role": "system",
        "content": context
    })
    return chat


def main(train_path, val_path):
    records = []

    chars_rp_records = []
    with open('characters.jsonl', 'r', encoding='utf-8') as f:
        for character in f:
            data = json.loads(character)
            for dialogue in data["dialogues"]:
                chat = dialogue["chat"]
                for message in chat:
                    if message["role"] == "char":
                        message["role"] = "bot"
                    if message["role"] == "operator":
                        message["role"] = "user"
                system_messages = build_char_system_messages(data)
                chat = system_messages + chat
                chars_rp_records.append({
                    "messages": chat,
                    "source": "characters_roleplay"
                })
    print("Characters roleplay count:", len(chars_rp_records))
    print("Characters roleplay max length:", calc_max_length(chars_rp_records))
    records += chars_rp_records

    print("All count:", len(records))
    print("All max length:", calc_max_length(records))

    random.shuffle(records)
    border = int(0.9 * len(records))
    train_records = records[:border]
    val_records = records[border:]
    with open(train_path, "w") as w:
        for record in train_records:
            w.write(json.dumps(record, ensure_ascii=False).strip() + "\n")
    with open(val_path, "w") as w:
        for record in val_records:
            w.write(json.dumps(record, ensure_ascii=False).strip() + "\n")


train_path = sys.argv[1]
val_path = sys.argv[2]
main(train_path, val_path)
