from google.cloud import dialogflow


def detect_intent_texts(project_id, session_id, texts, language_code='ru-RU'):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session))

    for text in texts:
        print(text)
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        # print(text_input)
        query_input = dialogflow.QueryInput(text=text_input)
        # print(query_input)
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        # print(response)
        return response.query_result.fulfillment_text
