install.packages("ollamar")

library(ollamar)

# first model: llama3.1

pull("llama3.1")

# setting up "chatbot" interface

repeat {
  user_input <- readline(prompt = "You: ")
  if (tolower(user_input) == "exit") {
    break
  }
  
  response <- generate("llama3.2", user_input, output="text")
  cat("Bot:", response, "\n")
}

# next step: 1) initialize chat history?
#            2) try out diff models