class ChatMemory:
    """
    In-memory storage for session-based chat history.
    """
    def __init__(self):
        self.sessions = {}  # session_id -> list of dict (role, content)

    def get_history(self, session_id: str):
        """
        Get chat history for a session.
        """
        return self.sessions.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to the chat history for a session.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": role, "content": content})
        # Limit history size to prevent prompt context bloat
        if len(self.sessions[session_id]) > 10:
            self.sessions[session_id] = self.sessions[session_id][-10:]

    def clear(self, session_id: str):
        """
        Clear session history.
        """
        if session_id in self.sessions:
            self.sessions[session_id] = []

_memory = ChatMemory()

def get_chat_memory():
    return _memory
