library(ollamar)

#' df containing single sentences from text chunks, as well as a parent id (called chunk_id) that points
#' to WHICH text chunk that specific sentence comes from
single_sentence_df <- readRDS("~/my_projects/my_R_stuff/output_sets/single_sentence_df.rds")
text_chunks <- readRDS("~/my_projects/my_R_stuff/data_sets/text_chunks_df.rds")

# chunk-level cosine similarity statistics
chunk_cosine_df <- readRDS("~/my_projects/my_R_stuff/output_sets/chunk_cosines_df.rds")

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


###' Got the vector space of each sentence in the single_sentence_df, and saved them into
###' a new column called sentence_vectors (this new version of single_sentence_df has been
###' uploaded to the Google Drive to replace the old one)

# sentence_vectors <- lapply(single_sentence_df$sentence, get_text_embedding)
# single_sentence_df$sentence_vectors <- sentence_vectors

# -----------------------------------------------------------------------------------------------------

# Function to calculate cosine similarities between *adjacent* sentences in the **SAME** chunk
get_chunk_cosines <- function(chunk_id) {
  # Subset rows from df where chunk_id matches
  chunk_rows <- single_sentence_df[single_sentence_df$chunk_id == chunk_id, ]
  
  n <- nrow(chunk_rows) # Get number of sentences in the chunk
  
  # If only one sentence in the chunk, return NA or numeric(0)
  if (n < 2) return(numeric(0))
  
  # Compute cosine similarities between each pair of adjacent sentence vectors
  mapply(
    cosine_similarity,
    chunk_rows$sentence_vectors[1:(n - 1)],
    chunk_rows$sentence_vectors[2:n]
  )
}

# -----------------------------------------------------------------------------------------------------

#' CONSTRUCTING DF OF COSINE SIMILARITY NUMERIC VECTORS + THRESHOLD
# Get a list of all unique chunk IDs (sorted so that we can retain the order of the chunks
#' from single_sentence_df)
unique_chunk_ids <- sort(unique(single_sentence_df$chunk_id))

# Compute cosine similarity vectors for each chunk using the above function
cosine_vectors <- lapply(unique_chunk_ids, get_chunk_cosines)

# df with chunk_id as first column
chunk_cosine_df <- data.frame(
  chunk_id = unique_chunk_ids,
  stringsAsFactors = FALSE
)

chunk_cosine_df$cosines <- cosine_vectors # Add cosine similarity vectors as a new column

# MEAN of cosine similarities for each chunk (if available), NA otherwise
chunk_cosine_df$cosine_mean <- sapply(chunk_cosine_df$cosines, function(x) if (length(x) > 0) mean(x) else NA)
# SD for each chunk (only if more than one similarity score exists)
chunk_cosine_df$cosine_sd <- sapply(chunk_cosine_df$cosines, function(x) if (length(x) > 1) sd(x) else NA)

# THRESHOLD for each chunk = mean - sd (used for splitting logic later)
chunk_cosine_df$threshold <- chunk_cosine_df$cosine_mean - chunk_cosine_df$cosine_sd

# Save the final chunk-level cosine similarity statistics to
saveRDS(chunk_cosine_df, "~/my_projects/my_R_stuff/output_sets/chunk_cosines_df.rds")


# -----------------------------------------------------------------------------------------------------
# Manual inspection for specific examples

# example 1
text_chunks$sub_chunks[4]
single_sentence_df$sentence[8:11]
chunk_cosine_df$cosines[4]
chunk_cosine_df$cosine_mean[4]
chunk_cosine_df$threshold[4]

# example 2 (longest chunk)
text_chunks$sub_chunks[3998]
single_sentence_df$sentence[13397:13414]
chunk_cosine_df$cosines[3998]
chunk_cosine_df$threshold[3998]

# example 3 (middle)
single_sentence_df$sentence[3691:3705]
chunk_cosine_df$cosines[1131]
chunk_cosine_df$threshold[1131]


# -----------------------------------------------------------------------------------------------------
# Analyze sentence distribution across chunks to check how many sentences chunks have

# Count how many sentences each chunk has; used later to get sentence grouping
sentence_counts <- table(single_sentence_df$chunk_id)
sentence_counts_ordered <- sort(table(single_sentence_df$chunk_id), decreasing = TRUE) 
# Ex: 3rd from the top
sentence_counts_ordered[26] #chunk_id = 7155, sentence_count = 11
text_chunks$sub_chunks[7155]

# -----------------------------------------------------------------------------------------------------

#'**FORMING SENTENCE GROUPS**
#' DESCRIPTION OF PROCESS:
#' - Only forming sentence groups (splitting chunks) for the chunks that have MORE than 10 sentences. This is to
#' ensure that the resulting sentence groups will still be large enough to make sense with the rest of our stored text.
#' - The chunks that ARE split, get split where there is the LOWEST cosine similarity between a sentence and the one
#' after it.
#'    - More specifically, to avoid splitting at the EDGES and thus forming single-sentence-groups, the first and
#'    last 2 cosine similarities between sentences in every chunk are ignored. This results in always 2 sentence groups
#'    for every large chunk that is split, so that we can keep most of the information together even when forming the
#'    sentence groups.
#' - The final df is formed by both whole chunks (that weren't split) and sentence groups (larger chunks that were split).

# Initialize lists to store output
group_texts <- list() 
group_chunk_ids <- c()

# Loop through each unique chunk_id
for (chunk_id in names(sentence_counts)) {
  sentence_count <- sentence_counts[[chunk_id]]
  
  # if ≤ 10 sentences Keep full chunk text
  if (sentence_count <= 10) {
    # appending text
    group_texts[[length(group_texts) + 1]] <- text_chunks$sub_chunks[as.integer(chunk_id)]
    group_chunk_ids <- c(group_chunk_ids, chunk_id)
    
  #' if > 10 sentences, get sentence rows for this chunk and combine them into sentence groups correctly
  } else {
    # getting ALL of the sentences with the chunk_id we're working with
    chunk_rows <- single_sentence_df[single_sentence_df$chunk_id == chunk_id, ]
    n <- nrow(chunk_rows)
    
    # Get cosine similarities for this specific chunk, to see where to combine sentences
    cosines <- chunk_cosine_df$cosines[[which(chunk_cosine_df$chunk_id == chunk_id)]]
    
    #' Skip FIRST and LAST 2 similarities to avoid splitting near edges; this should create
    #' similarly sized sentence groups and avoid specific sentences ending up on their own
    middle_indices <- 3:(length(cosines) - 2) # using a range from 3rd to 3rd to last
    
    #' using the middle_indices range to look at those cosine similarities
    #' get index of the smallest cosine similarity (splitting where the semantic
    #' similarity is the smallest); storing this as the spot where we split into groups
    split_index <- middle_indices[which.min(cosines[middle_indices])]    
    
    
    
    # Create sentence group 1 ----------------------
    # paste the correct sentences together
    text1 <- paste(chunk_rows$sentence[1:split_index], collapse = " ")
    group_texts[[length(group_texts) + 1]] <- text1 # add this sentence group to the list
    # keep track of the chunk_id for this sentence group and add it to the id numeric vector
    group_chunk_ids <- c(group_chunk_ids, chunk_id)
    
    
    
    # Create sentence group 2 ----------------------
    # paste the correct sentences together
    text2 <- paste(chunk_rows$sentence[(split_index+1):n], collapse = " ")
    group_texts[[length(group_texts) + 1]] <- text2 # add this sentence group to the list
    group_chunk_ids <- c(group_chunk_ids, chunk_id)
  }
}

# final df
sentence_groups_df <- data.frame(
  local_id = seq_along(group_texts),
  chunk_id = group_chunk_ids,
  text = unlist(group_texts),
  stringsAsFactors = FALSE
)

# saving sentence group df
saveRDS(sentence_groups_df, "~/my_projects/my_R_stuff/output_sets/sentence_groups_df.rds")
