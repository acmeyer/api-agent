from project_manager_agent import ProjectManagerAgent  

if __name__ == "__main__":
    project_manager_agent = ProjectManagerAgent()
    user_input = input('User: ').strip()
    project_manager_agent.run(user_input)
    project_manager_agent.pretty_print_conversation_history()
