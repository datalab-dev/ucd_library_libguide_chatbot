#' Generate Text Embedding via Ollama
#'
#' Gets vector representation (embedding) for the input text using the specified model.
#'
#' @param text A character string of the text to embed.
#' @param model The model to use for generating the embedding. Default is "mxbai-embed-large".
#'
#' @return A numeric vector representing the text embedding.
#' @export
get_text_embedding <- function(text, model = "mxbai-embed-large") {
  response <- ollamar::embeddings(model, text)
  return(response)
}
