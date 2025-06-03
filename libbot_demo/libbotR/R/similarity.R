#' Compute Cosine Similarity Between Two Vectors
#'
#' Calculates the cosine similarity between two numeric vectors, which measures the
#' angle between them in the vector space (i.e. semantic relationship/similarity between text)
#'
#' @param vec1 Numeric vector
#' @param vec2 Numeric vector
#' @return Cosine similarity between two vectors
#' @export
cosine_similarity <- function(vec1, vec2) {
  dot_product <- sum(vec1 * vec2)
  magnitude_vec1 <- sqrt(sum(vec1^2))
  magnitude_vec2 <- sqrt(sum(vec2^2))

  similarity <- dot_product / (magnitude_vec1 * magnitude_vec2)
  return(similarity)
}

#' Return Top Matching Vector and its Index Based on Prompt Vector
#'
#' Given a prompt, returns the top `n` matching vectors from a provided vector space
#' (unnested vector store) based on cosine similarity of embedding vectors.
#'
#' @param prompt_vec Numeric vector of prompt supplied by return_top_matches function
#' @param top_n Number of top matches to return.
#' @param embedding_matrix_df A data frame of embedding vectors (unnested)
#' @param corpus_text_df A data frame of text content and metadata (e.g., libguide text).
#' @return A data frame containing necessary data for top results.
#' @importFrom utils head
#' @export
get_top_matches <- function(prompt_vec, top_n = 3, embedding_matrix_df, corpus_text_df) {
  # Convert to matrix for speed and safety
  embedding_matrix <- as.matrix(embedding_matrix_df)

  # Compute cosine similarities across corpus vector space
  similarities <- apply(embedding_matrix, 1, function(vec) cosine_similarity(prompt_vec, vec))

  # Create a data frame with index, similarity, and corresponding text
  result_df <- data.frame(
    index = seq_along(similarities),
    similarity = similarities,
    text = corpus_text_df$text  # Gets corpus text from the df
  )

  # Remove duplicate texts (keep first occurrence); there are some cases where specific
  # guides refer to the same text and external link on multiple pages, so this removes duplicates
  result_df_unique <- result_df[!duplicated(result_df$text), ]

  # Order by similarity and select top_n
  top_results <- result_df_unique[order(result_df_unique$similarity, decreasing = TRUE), ]
  top_results <- head(top_results, top_n)

  # Returning all of the components of top_results is helpful for when debugging or looking
  # into the individual cosine similarities of results
  return(top_results)
}
