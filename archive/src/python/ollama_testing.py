# Had to switch over to OLLAMA for the time being, as OpenLLM has stopped supporting the smaller models
# that I wanted to use in order to run locally.


# This script is a simple command-line chatbot that interacts with an Ollama model.
# It sends user input to the model and prints the model's response in real-time.
# It uses the requests library to handle HTTP requests and JSON for data formatting.

# So far I've tried it with the "tinyllama" and 'llama2' models, and it works well.
# In order to change the model, you can change the "model" parameter in the requests.post() call, but remember
# to first have the model downloaded and running in the background on the Ollama server. This can be done by
# running the following command in the terminal:
#   ollama run <model_name>



import requests
import json



def chat():
    print("Chatbot started. Type 'exit' to quit.")
    messages = [] # Store the conversation history

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit': # Exit condition
            break

        # Add user's message to the conversation history
        messages.append({"role": "user", "content": user_input})

        try:
            # Send a POST request to Ollama's chat API
            # Not sure if the syntax is the cleanest, but I hadn't worked with
            # requests recently, so I had to look all this up.

            response = requests.post(
                'http://localhost:11434/api/chat',
                json={
                    "model": "llama2",  # Or another model like 'tinyllama', etc.
                    "messages": messages,
                    "stream": True
                },
                stream=True,
                timeout=60  # Timeout if the response takes too long (saw this was helpful online)
            )
        except requests.exceptions.RequestException as e:
            print(f"[Request error: {e}]")
            continue

        full_response = "" # Variable to store the model's reply
        try:

            # Stream the response line by line
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    # Decode each line and parse it as JSON. This was another section I did not really
                    # know how to do in python in specific, but it was easy to look up and debug.
                    data = json.loads(line.decode('utf-8'))
                    content = data.get("message", {}).get("content", "")
                    if content:
                        print(content, end="", flush=True) # Displays the message as it's generated 
                        full_response += content # Save it to append later (whole idea is to keep a concept of "memory" of the conversation)
                except json.JSONDecodeError as e:
                    print(f"\n[Error decoding JSON: {e}]")
        except Exception as e:
            print(f"\n[Streaming error: {e}]")
            continue

        print()  # line break after the bot response finishes
        if full_response.strip():
            # Add the model's reply to the conversation history
            messages.append({"role": "assistant", "content": full_response})
        else:
            print("[No response received. Check if the model is running and healthy.]")


# Starting chat interface
if __name__ == "__main__":
    chat()
