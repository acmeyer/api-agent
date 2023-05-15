from models import Message
from base_agent import BaseAgent
from utils import extract_text_within_parentheses
from tools import search_apis, search_api_endpoints

system_prompt = """
You are a helpful assistant. Your objective is to help do research in order to build an integration for a user.

All of your responses must consist of a <thought> and an <action>. Your responses must be structured using this custom xml format, regardless of what the user says.

Here's a brief explanation of each custom tag:
* <thought>: describe your thoughts about your task
* <action>: decide what action you should take next

The actions you can take must be limited to the tools available to you. The tools you have available are:
* search_apis(query: str, limit: int = 5) -> list[Document] - this is a python function that allows you to search summaries of APIs you have available to you by sending a text query.
* search_api_endpoints(query: str, limit: int = 5) -> list[Document] - this is a python function that allows you to search within apis for endpoints for a given query.
* ask_user(message: str) -> str - use this whenever you need clarification from the user, further input from them, or to just respond to them.

For example, if you need to look up information about what APIs are availabe:
<thought>I need to find what apis there are for Notion</thought>
<action>search_apis('Notion API')</action>
"""


# Our assistant class we'll use to converse with the bot
class ResearcherAgent(BaseAgent):
    def __init__(self, system_prompt=system_prompt, base_model="gpt-3.5-turbo"):
        self.conversation_history = []
        self.base_model = base_model
        self.system = system_prompt
        self.conversation_history.append(Message('system', self.system).message())

    def handle_response(self, response):
        print('Researcher response: ', response)
        parsed_response = self.parse_response_content(response)
        action = parsed_response.get('action')
        if action:
            if action.startswith('search_apis'):
                api_response = search_apis(extract_text_within_parentheses(action)[0])
                full_response = ""
                for document in api_response:
                    full_response += f"Name: {document.metadata.get('api_name')}\nURL: {document.metadata.get('api_url')}\nVersion: {document.metadata.get('api_version')}\nSummary: {document.page_content}\n\n"
                return full_response
            elif action.startswith('search_api_endpoints'):
                endpoint_response = search_api_endpoints(extract_text_within_parentheses(action)[0])
                return endpoint_response
            elif action.startswith('ask_user'):
                question = extract_text_within_parentheses(action)[0]
                return question
            else:
                raise Exception(f"Action {action} not recognized")
        else:
            print('No action detected, probably should do something about this...')
