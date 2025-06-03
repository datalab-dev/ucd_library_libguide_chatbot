

library(ollamar)

# setting up "chatbot" interface

repeat {
  user_input <- readline(prompt = "You: ")
  if (tolower(user_input) == "exit") {
    break
  }
  
  response <- generate("llama3.1", user_input, output="text")
  cat("Bot:", response, "\n")
}


# generalize function
ollamar_chatbot <- function(model){
  pull(model)
  
  # setting up "chatbot" interface
  repeat {
    user_input <- readline(prompt = "You: ")
    if (tolower(user_input) == "exit") {
      break
    }
    
  response <- generate(model, user_input, output = "text")
  cat("Bot: ", response, "\n")
    }
}


# chatbot remembers previous responses

ollamar_history <- function(model) {
  pull(model)
  
  # message system for user
  message("To exit chatbot, type 'exit'!")
  Sys.sleep(1)
  
  messages <- list()
  
  repeat {
    user_input <- readline(prompt = "You: ")
    if (tolower(user_input) == "exit") {
      break
    }
    
    messages <- append(messages, create_message(content=user_input))
    
    response <- chat(model, messages, output = "text")
    cat("Bot:", response, "\n")
    
    messages <- append(messages, create_message(content=response, role='assistant'))
  }
}


# Model: llama3.2
ollamar_chatbot("llama3.2")
ollamar_history('llama3.2')

# Model: llama3.3
ollamar_chatbot("llama3.3") # takes really long to run
