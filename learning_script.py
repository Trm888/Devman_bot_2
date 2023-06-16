import argparse
import json
import os

from environs import Env


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """Create an intent of the given intent type."""
    from google.cloud import dialogflow

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    return intents_client.create_intent(
        request={"parent": parent, "intent": intent, "language_code": "ru"}
    )


if __name__ == '__main__':
    default_file_path = os.path.join(os.getcwd(), 'examples_JSON_files_with_text', 'questions.json')
    parser = argparse.ArgumentParser(description='Запуск скрипта')
    parser.add_argument(
        '-fp',
        '--file_path',
        help='Укажите путь к файлу',
        nargs='?', default=default_file_path, type=str
    )
    args = parser.parse_args()
    file_path = args.file_path

    env = Env()
    env.read_env()
    project_id = env.str('GOOGLE_CLOUD_PROJECT_ID')

    with open(file_path, 'r', encoding='utf-8') as file:
        for intent, training_phrases in json.load(file).items():
            questions = training_phrases["questions"]
            answer = [training_phrases['answer']]
            create_intent(project_id, intent, questions, answer)
