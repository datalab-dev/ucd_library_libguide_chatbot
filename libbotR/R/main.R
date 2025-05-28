#' Return Top Matching Text Entries Based on Prompt
#'
#' Given a prompt, returns the top `n` matching entries from a provided text dataset
#' based on cosine similarity of embedding vectors; includes text wrapper containing
#' appropriate titles and URLs.
#'
#' @param prompt A user-supplied character string.
#' @param top_n Number of top matches to return.
#' @param embedding_matrix_df A data frame of embedding vectors (unnested)
#' @param corpus_text_df A data frame of text content and metadata (e.g., libguide text).
#'
#' @return Printed formatted string output of the top matches.
#' @export
return_top_matches <- function(prompt, top_n, embedding_matrix_df, corpus_text_df){
  # Get vector of given prompt
  prompt_vec <- get_text_embedding(prompt)

  # Data frame of the top matches (index and cosine similarity of match)
  top_matches <- get_top_matches(prompt_vec, top_n, embedding_matrix_df, corpus_text_df)

  # Get indices from the top returned matches
  top_indices <- top_matches$index

  # Get text wrapper and text information from the corpus df
  matched_entries <- corpus_text_df[top_indices, ]

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
  # Print results
  cat(paste(result_list, collapse = ""))
}
