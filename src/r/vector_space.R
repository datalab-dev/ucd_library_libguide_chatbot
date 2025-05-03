library(ollamar)
library(httr)

# the function to calculate vector space
vector_space <- function(input, model) {
  response <- POST(
    url = "http://localhost:11434/api/embeddings",
    body = list(
      model = model,
      prompt = input
    ),
    encode = "json"
  )
  
  content <- content(response, as = "parsed")

  if (is.null(content$embedding) || length(content$embedding) == 0) {
    return(NULL)
  }  
  
  return(content$embedding)
}


ollamar_history <- function(model) {
  pull(model)
  
  # message system for user
  message("To exit chatbot, type 'exit'!")
  Sys.sleep(1)
  
  messages <- list()
  
  record <- list()
  
  repeat {
    user_input <- readline(prompt = "You: ")
    if (tolower(user_input) == "exit") {
      break
    }
    
    messages <- append(messages, create_message(content=user_input))
    
    response <- chat(model, messages, output = "text")
    cat("Bot:", response, "\n")
    
    messages <- append(messages, create_message(content=response, role='system'))
    
    # new part for vector space
    vector <- vector_space(user_input, model)
    if (!is.null(vector)) {
      record[[length(record) + 1]] <- data.frame(
        prompt = user_input,
        response = response,
        as.data.frame(t(vector))
      )
    }
  }
  
  if (length(record) > 0) {
    df <- do.call(rbind, record)
    names(df) [-(1:2)] <- paste0("dim_", 1:(ncol(df)-2))
    return(df) 
  } else {
    cat("No chat history to save.\n")
    return(NULL)
  }
}

prompt_vector_space <- ollamar_history("llama3.2")


# I combined the 'vector_space' function that I created with the 'ollamar_history' 
# to see if it actually calculates the vector space for prompt and it does return 
# something but I'm not sure if this is the "vector space" they're asking for.
