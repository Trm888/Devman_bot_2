import json
import os

from environs import Env


def delete_intent(project_id, intent_id):
    """Delete intent with the given intent type and intent value."""
    from google.cloud import dialogflow

    intents_client = dialogflow.IntentsClient()

    intent_path = intents_client.intent_path(project_id, intent_id)

    intents_client.delete_intent(request={"name": intent_path})


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
        request={"parent": parent, "intent": intent}
    )



if __name__ == '__main__':
    env = Env()
    env.read_env()
    project_id = env.str('GOOGLE_CLOUD_PROJECT_ID')
    file_path = os.path.join(os.getcwd(), 'examples_JSON_files_with_text', 'questions.json')

    with open(file_path, 'r', encoding='utf-8') as file:
        job_intent = json.load(file)["Устройство на работу"]
        questions = job_intent["questions"]
        answer = [job_intent['answer']]

    create_intent(project_id, 'getting-job', questions, answer)

