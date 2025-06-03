#' This R script defines the core functions and datasets used in the 'Libbot Chatbot'
#' search-and-response system.
#'
#' Each function and dataset is documented with comments explaining its purpose and usage.
#'
#' An example query (search prompt) and its corresponding response can be found at the bottom
#' of the script.

###############################################################################
### LOAD PACKAGES:
library(ollamar)
library(jsonlite)

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
  
  # Create a data frame with index, similarity, and corresponding text
  result_df <- data.frame(
    index = seq_along(similarities),
    similarity = similarities,
    text = text_full_libguide$text  # This assumes the corpus text lives here
  )
  
  #' Remove duplicate texts (keep first occurrence); there are some cases where specific
  #' guides refer to the same text and external link on multiple pages, so this removes duplicates
  result_df_unique <- result_df[!duplicated(result_df$text), ]
  
  # Order by similarity and select top_n
  top_results <- result_df_unique[order(result_df_unique$similarity, decreasing = TRUE), ]
  top_results <- head(top_results, top_n)
  
  #' Returning all of the components of top_results is helpful for when debugging or looking
  #' into the individual cosine similarities of results
  return(top_results)
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
  
  # Create text wrapper out
  result_list <- sapply(1:nrow(matched_entries), function(i) {
    row <- matched_entries[i, ]
    entry_text <- paste0(
      "[", i, "]\n",
      "Main Libguide: ", row$libguide_title, "\n",
      "Link: ", row$libguide_url, "\n\n",
      
      "Section: ", row$chunk_title, "\n",
      ifelse(is.na(row$chunk_url) || row$chunk_url == "", "", paste0("Section Link: ", row$chunk_url, "\n")),
      "External Resource: ", row$external_url, "\n\n",
      
      row$text, "\n\n\n"
    )
  })
  
  cat(paste(result_list, collapse = ""))
}



# TESTS:
# prompt1 <- "Where can I find information regarding climate change and bugs?"
# result <- return_top_matches(prompt1, 3)







