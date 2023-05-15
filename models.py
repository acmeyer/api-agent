# A basic class to create a message as a dict for chat
class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content
        
    def message(self):
        return {"role": self.role,"content": self.content}