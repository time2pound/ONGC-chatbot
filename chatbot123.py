from langchain_ollama import ChatOllama

# Connect to the local Llama 3.2 model
llm = ChatOllama(model="llama3.2")

print("===================================")
print("      ONGC AI Chatbot")
print("Type 'exit' to quit")
print("===================================")

while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    response = llm.invoke(question)

    print("\nAI:", response.content)