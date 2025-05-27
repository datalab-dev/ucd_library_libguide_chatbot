library("servr")
library("httpuv")
library("stringr")
library("ollamar")
library(jsonlite)

# Integrate final_demo_script into server

chatbot_handler <- function(env) {
  
###############################################################################
### LOAD DATA:
#**REMEMBER TO CHANGE THE FILE PATH FOR THE DATA**

# Vector Space of Corpus Text
vector_file_path = "~/my_projects/my_R_stuff/output_sets/emb_full_libguide_df.rds"
embedding_full_libguide <- readRDS(vector_file_path)

# Text Wrapper + Corpus Text
text_file_path <- "~/my_projects/my_R_stuff/data_sets/text_full_libguide.rds"
text_full_libguide <- readRDS(text_file_path)

###############################################################################
#### HELPER FUNCTIONS:

# Get text embedding/vector for text using Ollama's 'embeddings' function
get_text_embedding <- function(text, model = "mxbai-embed-large") {
  response <- ollamar::embeddings(model, text)
  return(response)
}

#' Compute the cosine similarity between vectors (semantic relationship/similarity
#' between text)
cosine_similarity <- function(vec1, vec2) {
  dot_product <- sum(vec1 * vec2)
  magnitude_vec1 <- sqrt(sum(vec1^2))
  magnitude_vec2 <- sqrt(sum(vec2^2))
  
  similarity <- dot_product / (magnitude_vec1 * magnitude_vec2)
  return(similarity)
}

#' Get indices and cosine similarity of top 'n' matches, in terms of similarity
#' between prompt and corpus vectors
get_top_matches <- function(prompt_vector, embedding_matrix_df, top_n = 3) {
  #' Convert to matrix for speed and safety
  embedding_matrix <- as.matrix(embedding_matrix_df)
  
  # Compute cosine similarities across corpus vector space
  similarities <- apply(embedding_matrix, 1, function(vec) cosine_similarity(prompt_vector, vec))
  
  # Get top matches
  top_indices <- order(similarities, decreasing = TRUE)[1:top_n]
  
  # Return indices and similarity scores
  return(data.frame(index = top_indices, similarity = similarities[top_indices]))
}

###############################################################################

#' Returns list of top 'n' matches between prompt and data, including additional information such as
#' titles and URLs, on top of the text response itself
return_top_matches <- function(prompt, top_n){
  # Get vector of given prompt
  prompt_vec <- get_text_embedding(prompt)
  
  # Data frame of the top matches (index and cosine similarity of match)
  top_matches <- get_top_matches(prompt_vec, embedding_full_libguide, top_n)
  
  # Get indices from the top returned matches
  top_indices <- top_matches$index
  
  # Get text wrapper and text information from text_full_libguide
  matched_entries <- text_full_libguide[top_indices, ]
  
  # Create text wrapper out of the different componets
  result_list <- lapply(seq_len(nrow(matched_entries)), function(i) {
    row <- matched_entries[i, ]
    list(
      # id = row$local_id,
      libguide_title = row$libguide_title,
      libguide_url = row$libguide_url,
      chunk_title = row$chunk_title,
      section_url = if (!is.na(row$chunk_url)) row$chunk_url else NULL,
      text = row$text,
      external_url = row$external_url
    )
  })
  
  # Return as JSON (for frontend to use to display information)
  jsonlite::toJSON(result_list, pretty = TRUE, auto_unbox = TRUE)
}


  query <- str_split(env[["QUERY_STRING"]], "=") [[1]]
  prompt <- if (length(query) > 1) {
    URLdecode(query[2])
  } else {
    ""
  }
  if (prompt == "") {
    response <- jsonlite::toJSON(list(error = "No query provided."), auto_unbox = TRUE)
  } else {
    response <- return_top_matches(prompt, top_n = 3)
  }
  
  list(
    status = 200L,
    headers = list("Content-Type" = "application/json"),
    body = response
  )
}

startServer("127.0.0.1", 8000, list(call = chatbot_handler))

