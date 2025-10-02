from core.ollama_rag import OllamaRAG
import os

model = 'mistral:latest'
path = 'uploads/'

print(os.getcwd())

print("Which PDF do you want to chat with:", end=' ')
pdf_name = input().strip()
print('\n\t===== Please wait a while =====\t\n')

rag = OllamaRAG(model)
rag.load_pdf(path, pdf_name)
rag.create_chain()

while True:
    user_input = input("PROMPT: ")
    if user_input.lower() == 'exit':
        break
    for chunk in rag.query(user_input):
        print(chunk, end="", flush=True)
    print("\n")

print('Thanks for using!')