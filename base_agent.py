from termcolor import colored
from openai_service import get_chat_completion
from models import Message
from utils import parse_response_for_xml

system_prompt = """You are a helpful assistant."""

class BaseAgent:
    def __init__(self, system_prompt=system_prompt, base_model="gpt-3.5-turbo"):
        self.conversation_history = []
        self.base_model = base_model
        self.system = system_prompt
        self.conversation_history.append(Message('system', self.system).message())

    def _get_assistant_response(self, prompt) -> dict[str, str]:
        try:
            completion = get_chat_completion(
                messages=prompt,
                model=self.base_model,
            )
            response_message = Message("assistant", completion)
            return response_message.message()
        except Exception as e:
            raise Exception(f'Request failed with exception {e}')

    def ask(self, next_user_prompt):
        [self.conversation_history.append(x) for x in next_user_prompt]
        assistant_response = self._get_assistant_response(self.conversation_history)
        self.conversation_history.append(assistant_response)
        return assistant_response
            
        
    def pretty_print_conversation_history(self, colorize_assistant_replies=True):
        for entry in self.conversation_history:
            if entry['role'] == 'system':
                pass
            else:
                prefix = entry['role']
                content = entry['content']
                output = colored(prefix +':\n' + content, 'green') if colorize_assistant_replies and entry['role'] == 'assistant' else prefix +':\n' + content
                print(output)

    def parse_response_content(self, response):
        return parse_response_for_xml(response, ['thought', 'action'])
    
    def handle_response(self, response):
        print('Not implemented')


if __name__ == '__main__':
    agent = BaseAgent()

    messages = []
    user_message = Message('user', 'I\'d like to build an integration')
    messages.append(user_message.message())
    response_message = agent.ask(messages)
    print(response_message.get('content'))
    agent.pretty_print_conversation_history()