from models import Message
from base_agent import BaseAgent
from utils import extract_text_within_parentheses
from coder_agent import CoderAgent
from researcher_agent import ResearcherAgent

system_prompt = """
You are a helpful assistant. Your objective is to help manage a project for building an integration for a user.

All of your responses must consist of a <thought> and an <action>. Your responses must be structured using this custom xml format, regardless of what the user says.

Here's a brief explanation of each custom tag:
* <thought>: describe your thoughts about your task
* <action>: decide what action you should take next

The actions you take must be limited to the tools available to you. The tools you have available are:
* ask_researcher(message: str) -> str - use this whenever you need to find out more information about an API, how something works, or just general information.
* ask_coder(message: str) -> str - use this whenever you need some code written or generated for the project. You should be as specific as possible with your request.
* ask_user(message: str) -> str - use this whenever you need clarification from the user, further input from them, or to respond to them with the final result.

For example, if you need to know more about the user's request, you could respond with:
<thought>I need more information about the user's request</thought>
<action>ask_user('Can you please tell me more about your request?')</action>
"""


# Our assistant class we'll use to converse with the bot
class ProjectManagerAgent(BaseAgent):
    def __init__(self, system_prompt=system_prompt, base_model="gpt-4"):
        self.conversation_history = []
        self.base_model = base_model
        self.system = system_prompt
        self.conversation_history.append(Message('system', self.system).message())
        self.coder_agent = CoderAgent()
        self.researcher_agent = ResearcherAgent()

    def _ask_coder(self, message):
        coder_conversation = []
        coder_conversation.append(Message('user', message).message())
        resp = self.coder_agent.ask(coder_conversation)
        resp_content = resp.get('content')
        coder_response = self.coder_agent.handle_response(resp_content)
        coder_message = Message('assistant', coder_response).message()
        response_message = self.ask([coder_message])
        response_content = response_message.get('content')
        self.handle_response(response_content)

    def _ask_researcher(self, question):
        researcher_conversation = []
        researcher_conversation.append(Message('user', question).message())
        resp = self.researcher_agent.ask(researcher_conversation)
        resp_content = resp.get('content')
        researcher_response = self.researcher_agent.handle_response(resp_content)
        researcher_message = Message('assistant', researcher_response).message()
        response_message = self.ask([researcher_message])
        response_content = response_message.get('content')
        self.handle_response(response_content)

    def _ask_user(self, question):
        print(f"GPT: {question}")
        user_input = input('User: ').strip()
        user_message = Message('user', user_input).message()
        response_message = self.ask([user_message])
        response_content = response_message.get('content')
        self.handle_response(response_content)

    def handle_response(self, response):
        print('PM Response: ', response)
        parsed_response = self.parse_response_content(response)
        action = parsed_response.get('action')
        if action:
            if action.startswith('ask_coder'):
                coder_question = extract_text_within_parentheses(action)[0]
                self._ask_coder(coder_question)
            elif action.startswith('ask_researcher'):
                researcher_question = extract_text_within_parentheses(action)[0]
                self._ask_researcher(researcher_question)
            elif action.startswith('ask_user'):
                user_question = extract_text_within_parentheses(action)[0]
                self._ask_user(user_question)
            else:
                raise Exception(f"Action {action} not recognized")
        else:
            print('No action detected, probably should do something about this...')

    def run(self, query: str):
        user_message = Message('user', query).message()
        response_message = self.ask([user_message])
        response_content = response_message.get('content')
        self.handle_response(response_content)
