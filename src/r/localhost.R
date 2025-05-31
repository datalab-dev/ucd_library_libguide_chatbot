
library("servr")
library("httpuv")
library("stringr")
library("ollamar")
library(jsonlite)
library(libbotR)

embedding_full_libguide <- readRDS("~/Documents/ucd/sts195/2025_startup_libguide_chatbot/data/emb_full_libguide_df.rds")
text_full_libguide <- readRDS("~/Documents/ucd/sts195/2025_startup_libguide_chatbot/data/text_full_libguide.rds")

# Modified from 'ollamar.R' file
#ollamar_chatbot2 <- function(model, user_input) {
#  pull(model)
  
#  response <- generate(model, user_input, output = "text")
  
#  return(response)
#}

# 

# Define handler
# chatbot_handler <- function(env) {
#   tryCatch({
#     query <- str_split(env[["QUERY_STRING"]], "=")[[1]]
#     msg <- if (length(query) > 1) URLdecode(query[2]) else ""
#     
#     cat("User message received: ", msg, "\n")
#     
#     llm_response <- generate("llama3.2", msg, output = "text")
#     rag_response <- capture.output(return_top_matches(
#       prompt = msg,
#       top_n = 3,
#       embedding_matrix_df = embedding_full_libguide,
#       corpus_text_df = text_full_libguide
#     ))
#     
#     combined_response <- paste(llm_response, "\n\n---\n\n", paste(rag_response, collapse = "\n"))
#     
#     list(
#       status = 200L,
#       headers = list("Content-Type" = "text/plain", "Access-Control-Allow-Origin" = "*"),
#       body = combined_response
#     )
#   }, error = function(e) {
#     list(
#       status = 500L,
#       headers = list("Content-Type" = "text/plain"),
#       body = paste("⚠️ Server error:\n", conditionMessage(e))
#     )
#   })
# }

chatbot_handler <- function(env) {
  tryCatch({
    # Parse incoming query
    query <- str_split(env[["QUERY_STRING"]], "=")[[1]]
    msg <- if (length(query) > 1) URLdecode(query[2]) else ""
    
    if (msg == "") {
      return(list(
        status = 400L,
        headers = list("Content-Type" = "text/plain", "Access-Control-Allow-Origin" = "*"),
        body = "⚠️ No message provided in query."
      ))
    }
    
    cat("User message received: ", msg, "\n")
    
    # Generate LLM response (Ollama)
    summary_prompt <- paste0(
      "Act as a librarian, please summarize the following query into one concise paragraph:\n\n",
      msg
    )
    llm_response <- generate("llama3.2", summary_prompt, output = "text")
    
    # Retrieve relevant LibGuide entries using your custom RAG function
    rag_response <- capture.output(return_top_matches(
      prompt = msg,
      top_n = 3,
      embedding_matrix_df = embedding_full_libguide,
      corpus_text_df = text_full_libguide
    ))
    
    # Combine LLM and LibGuide response
    combined_response <- paste0(
       llm_response,
      "<br><br><strong>Related UC Davis Library Resources:</strong><br>", 
      paste(rag_response, collapse = "<br>")
    )
    
    # Return combined response
    list(
      status = 200L,
      headers = list("Content-Type" = "text/html", "Access-Control-Allow-Origin" = "*"),
      body = combined_response
    )
    
  }, error = function(e) {
    list(
      status = 500L,
      headers = list("Content-Type" = "text/html"),
      body = paste(" Server error:\n", conditionMessage(e))
    )
  })
}


startServer("127.0.0.1", 8000, list(call = chatbot_handler))


