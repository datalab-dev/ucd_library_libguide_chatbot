library("servr")
library("httpuv")
library("stringr")
library("ollamar")
library(jsonlite)

# Modified from 'ollamar.R' file
ollamar_chatbot2 <- function(model, user_input) {
  pull(model)
  
  response <- generate(model, user_input, output = "text")
  
  return(response)
}

# 
chatbot_handler <- function(env) {
  query <- str_split(env[["QUERY_STRING"]], "=")[[1]]
  msg <- if (length(query) > 1) URLdecode(query[2]) else ""
  
  rag_response <- " hehe"
  response <- paste(ollamar_chatbot2("llama3.2", msg), "\n\n", rag_response, sep = "")
  
  list(
    status = 200L,
    headers = list(
      "Content-Type" = "text/plain",
      "Access-Control-Allow-Origin" = "*"  # ← critical for fetch() in browser!!
    ),
    body = response
  )
}


startServer("127.0.0.1", 8000, list(call = chatbot_handler))


