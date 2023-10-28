import os

import openai
import yaml
from pathlib import Path

openai.api_key = os.getenv('OPENAI_TOKEN')


def load_character_info(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        info = f"""
        Ты - искусственный интеллект имитирующий человека по имени {data['name']}.
        Твоя задача отвечать на запросы пользователя от имени этого персонажа придерживаясь стиля речи этого персонажа,
        старайся отвечать коротко и по делу, вот краткая информация о тебе:
        {data['description']}
        """
        return info


def ask_character(system_prompt, chat_history):
    conversation = [{"role": "system", "content": system_prompt}] + chat_history
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=conversation
    )
    answer = response['choices'][0]['message']['content']
    return answer.strip()


CURRENT_DIR = Path('.')

# Load character info
character_info = load_character_info(CURRENT_DIR / 'characters/yakovlev.yml')

# Small history if messages
chat_history = []

while True:
    # Read question from user
    user_input = input("User: ")
    if user_input.lower() in ['выход', 'exit', 'quit']:
        print("Bot: До встречи!")
        break

    # Add user question to history
    chat_history.append({"role": "user", "content": user_input})

    # Make a request
    response = ask_character(character_info, chat_history)
    print("Bot:", response)

    # Add an answer to history log
    chat_history.append({"role": "assistant", "content": response})

    # Let's keep just a couple last questions and responses
    if len(chat_history) > 4:
        chat_history = chat_history[-4:]
