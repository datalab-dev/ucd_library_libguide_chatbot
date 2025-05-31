###############################################################################
### LOAD PACKAGES:
library("servr")
library("httpuv")
library("stringr")
library("ollamar")
library(jsonlite)
library(libbotR)

###############################################################################
### LOAD DATA:
#**REMEMBER TO CHANGE THE FILE PATH FOR THE DATA**

# Vector Space of Corpus Text
vector_file_path = "~/my_projects/my_R_stuff/output_sets/emb_full_libguide_df.rds"
embedding_full_libguide <- readRDS(vector_file_path)

# Text Wrapper + Corpus Text
text_file_path <- "~/my_projects/my_R_stuff/output_sets/text_full_libguide.rds"
text_full_libguide <- readRDS(text_file_path)

###############################################################################

# Main HTTP request handler function for the chatbot service
chatbot_handler <- function(env) {
  tryCatch({
    
    # Parse the query string from the HTTP GET request
    query <- str_split(env[["QUERY_STRING"]], "=")[[1]]
    msg <- if (length(query) > 1) URLdecode(query[2]) else ""
    
    # If no message is provided in the request, return an error response
    if (msg == "") {
      return(list(
        status = 400L,
        headers = list("Content-Type" = "text/plain", "Access-Control-Allow-Origin" = "*"),
        body = "⚠️ No message provided in query."
      ))
    }
    
    # Log the received user message to the console
    cat("User message received: ", msg, "\n")
    
    # Create a librarian-style summary prompt to send to the LLM
    summary_prompt <- paste0(
      "Act as the user's librarian. Please summarize the user's query in one concise and informative paragraph. Briefly explain the topic the user is asking about, and then suggest reliable strategies or places to find more information, such as library databases, archives, or catalogs. Do not make up specific book titles or sources — only refer to general or commonly known resources, or give search strategies.\n\n",
      msg
    )
    # Use the LLM (Ollama via `generate()`) to generate a summary paragraph based on the user's message
    llm_response <- generate("llama3:8b", summary_prompt, output = "text")
    
    # Use RAG function to find top matching library resources
    rag_response <- capture.output(return_top_matches(
      prompt = msg,
      top_n = 3,
      embedding_matrix_df = embedding_full_libguide,
      corpus_text_df = text_full_libguide
    ))
    
    # Combine the LLM summary and library resource results into a formatted HTML response
    combined_response <- paste0(
      llm_response,
      "<br><br><strong>Reliable resources from the UC Davis Library:</strong><br>", 
      paste(rag_response, collapse = "<br>")
    )
    
    # Return combined response
    list(
      status = 200L,
      headers = list("Content-Type" = "text/html", "Access-Control-Allow-Origin" = "*"),
      body = combined_response
    )
    
  }, error = function(e) {
    # If something goes wrong, return a server error with the error message
    list(
      status = 500L,
      headers = list("Content-Type" = "text/html"),
      body = paste(" Server error:\n", conditionMessage(e))
    )
  })
}

# Stop any previous servers that might be running on this port
stopAllServers()

# Start the local server on port 8000 using `chatbot_handler` as the request processor
startServer("127.0.0.1", 8000, list(call = chatbot_handler))


