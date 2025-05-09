library(ollamar)

# main dataset
corpus_sections <- readRDS("~/my_projects/my_R_stuff/data_sets/corpus_sections.rds")
# head of data, for testing
test_data <- readRDS("~/my_projects/my_R_stuff/data_sets/ollama_testing_data.rds")
corpus_whole <- readRDS("~/my_projects/my_R_stuff/data_sets/corpus_whole.rds")



#' In this R file:
#' - get_text_embedding function = generates the vector space of given text using Ollamar (used both for prompts and for training text chunk data)
#' - cosine_similarity function = gets cosine similarity of input vectors (used both for finding similarity between prompt and corpus, and also for finding similarity between individual corpus chunks)
#' - get_top_matches function = specifically made to take and go through a data.frame of vectors, and getting the cosine similarity between the individual entries/vectors and an input prompt; it then compares the generated values to find the top 3 most similar vectors
#' - Below the functions is the application of the functions to the **CORPUS SECTIONS**, as well as the generated df. This hasn't yet been done with the **CORPUS WHOLE** because we still need to go through and confirm that the **CORPUS SECTIONS** one worked correctly and gave us what we wanted.
#' - At the very bottom are some examples of how the individual functions work, and some test runs I did with the smaller test_data








# Takes a text string and uses ollama embed() to retrieve word-level embeddings
#Averages them into a single vector representing the full text
get_text_embedding <- function(text, model = "mxbai-embed-large") {
  response <- ollamar::embeddings(model, text)
  return(response)
}


# Takes two numeric vectors as input
# Computes the cosine similarity between them
cosine_similarity <- function(vec1, vec2) {
  dot_product <- sum(vec1 * vec2)
  magnitude_vec1 <- sqrt(sum(vec1^2))
  magnitude_vec2 <- sqrt(sum(vec2^2))
  
  similarity <- dot_product / (magnitude_vec1 * magnitude_vec2)
  return(similarity)
}


# Function to calculate cosine similarity between a prompt vector and a set of document vectors,
# and return the top N most similar documents (default is 3)
get_top_matches <- function(prompt_vector, embedding_df, top_n = 3) {
  
  # Use sapply to compute cosine similarities over all section vectors
  similarities <- sapply(embedding_df$text_embeddings, function(doc_vector) {
    cosine_similarity(prompt_vector, doc_vector)
  })
  
  # Get top N indices
  top_indices <- order(similarities, decreasing = TRUE)[1:top_n]
  
  # Print top results
  for (i in top_indices) {
    cat("ID:", embedding_df$ID[i], "\n")
    cat("Cosine Similarity:", similarities[i], "\n\n\n")
  }
}




#**This one is the VECTOR SPACE for the CORPUS SECTIONS**
# Applying functions to our data and creating new data.frame
text_embeddings <- lapply(corpus_sections$text, get_text_embedding) # getting embeddings/vector space of each section chunk
embedding_df <- data.frame(ID = corpus_sections$ID) # creating the vector space dataframe for the SECTIONS (with their ID collected from the parent df)
embedding_df$text_embeddings <- text_embeddings # adding the respective vectors to the df

saveRDS(embedding_df, "~/my_projects/my_R_stuff/output_sets/corpus_sections_vectors_df.rds") # saving df



#**This one is the VECTOR SPACE for the CORPUS WHOLE**
# Applying functions to our data and creating new data.frame
text_embeddings_whole <- lapply(corpus_whole$text, get_text_embedding)
embedding_df_whole <- data.frame(ID = corpus_whole$ID)
embedding_df_whole$text_embeddings_whole <- text_embeddings_whole

saveRDS(embedding_df_whole, "~/my_projects/my_R_stuff/output_sets/corpus_whole_vectors_df.rds")







# COSINE SIMILARITY COMPARISON OVER **CORPUS SECTIONS**
prompt2 <- "How would I find information about carbon emmissions from the agricultural industry?"
prompt_vec2 <- get_text_embedding(prompt2)
prompt3 <- "Where can I get information about representations of class in the works of Charles Dickens?"
prompt_vec3 <- get_text_embedding(prompt3)

get_top_matches(prompt_vec3, embedding_df)
#' ID: 2240 
#' Cosine Similarity: 0.6081561 
#' 
#' ID: 1045 
#' Cosine Similarity: 0.5863628 
#' 
#' ID: 1073
#' Cosine Similarity: 0.5863628 






# COSINE SIMILARITY COMPARISON OVER **CORPUS WHOLE**
prompt2_whole <- "How would I find information about carbon emmissions from the agricultural industry?"
prompt_vec2_whole <- get_text_embedding(prompt2_whole)
prompt3_whole <- "Where can I get information about representations of class in the works of Charles Dickens?"
prompt_vec3_whole <- get_text_embedding(prompt3_whole)

get_top_matches(prompt_vec3_whole, embedding_df_whole)
#' ID: 82 
#' Cosine Similarity: 0.586531 
#' 
#' ID: 58 
#' Cosine Similarity: 0.577994 
#' 
#' ID: 13 
#' Cosine Similarity: 0.5450107 
message(corpus_whole$text[[13]])









# Example texts and prompt
doc1 <- test_data$text[[1]]
doc2 <- data$text[[25]]
prompt <- "What is the Black Studies Center?"

# Example get embeddings
vec1 <- get_text_embedding(doc1)
vec2 <- get_text_embedding(doc2)
prompt_vec <- get_text_embedding(prompt)


# Example compare similarity
similarity1 <- cosine_similarity(prompt_vec, vec1)
similarity2 <- cosine_similarity(prompt_vec, vec2)
similarity3 <- cosine_similarity(vec1, vec2)

print(similarity1)
print(similarity2)
print(similarity3)

# Example of top 3 most similar
get_top_matches(prompt_vec,embedding_df,3)






