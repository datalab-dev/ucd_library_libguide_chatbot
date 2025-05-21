library(ollamar)
library(dplyr)
library(tidyr)

# LOADING CORPUS SENTENCE GROUPS
sentence_groups_df <- readRDS("~/my_projects/my_R_stuff/output_sets/sentence_groups_df.rds")


# -----------------------------------------------------------------------------------------------------
###' Old functions used to get vector spaces and cosine similarity

# function for getting vector space of given text
get_text_embedding <- function(text, model = "mxbai-embed-large") {
  response <- ollamar::embeddings(model, text)
  return(response)
}

# compute the cosine similarity between vectors or vector spaces
cosine_similarity <- function(vec1, vec2) {
  dot_product <- sum(vec1 * vec2)
  magnitude_vec1 <- sqrt(sum(vec1^2))
  magnitude_vec2 <- sqrt(sum(vec2^2))
  
  similarity <- dot_product / (magnitude_vec1 * magnitude_vec2)
  return(similarity)
}

# -----------------------------------------------------------------------------------------------------

# getting embeddings/vector space of each chunk/sentence group (NESTED)
text_embeddings <- lapply(sentence_groups_df$pasted_text, get_text_embedding) 
sentence_groups_df$text_embeddings <- text_embeddings # adding the respective vectors to the df

# SAVING VECTOR SPACE TO SAME DF (NESTED)
# saveRDS(sentence_groups_df, "~/my_projects/my_R_stuff/output_sets/sentence_groups_df.rds")

# -----------------------------------------------------------------------------------------------------

#**UNNESTED VECTOR STORE**
unnested_sentence_groups_df <- sentence_groups_df %>%
  select(text_embeddings) %>%
  unnest_wider(text_embeddings, names_sep = "_")

# SAVING UNNESTED VECTOR
# saveRDS(unnested_sentence_groups_df, "~/my_projects/my_R_stuff/output_sets/unnested_sentence_groups_df.rds")

# -----------------------------------------------------------------------------------------------------

# NEW VERSION OF GET_TOP_MATCHES
get_top_matches <- function(prompt_vector, embedding_matrix_df, top_n = 3) {
  #' Convert to matrix for speed and safety (in case we ever have to do any other linear-algebra-type
  #' operations)
  embedding_matrix <- as.matrix(embedding_matrix_df)
  
  # Compute cosine similarities
  similarities <- apply(embedding_matrix, 1, function(vec) cosine_similarity(prompt_vector, vec))
  
  # Get top matches
  top_indices <- order(similarities, decreasing = TRUE)[1:top_n]
  
  # Return indices and similarity scores
  return(data.frame(index = top_indices, similarity = similarities[top_indices]))
}


# -----------------------------------------------------------------------------------------------------

# TESTING THE ALGORITHM
prompt_vec <- get_text_embedding("Where can I get information about climate change?")
top_matches <- get_top_matches(prompt_vec, unnested_sentence_groups_df, top_n = 5)
top_matches

# TOP 1
sentence_groups_df$text[[1337]]
# TOP 2
sentence_groups_df$text[[2424]]
# ...