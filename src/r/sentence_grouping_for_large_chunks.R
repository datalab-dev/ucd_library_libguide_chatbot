#' Dealing with larger sections of texts in the corpus
#' 
#' In an attempt to standardize the word count of responses from the chatbot, we
#' are looking at chunks that have word counts greater than the the third 
#' quartile, and breaking these large responses into sentence groups of adjacent 
#' sentences. We are also integrating this into the vector space/cosine 
#' similarity function. The goal is to have our chatbot return the most 
#' relevant group of sentences from a chunk if the query/prompt result would be
#' considered a "large" chunk of text. 
#' 
#' 
#' The next step to this issue is linking it with the vector space/cosine 
#' similarity function. 
#' 
#' This function only needs to be called if the user query 
#' has a large chunk returned, ie if the user query has a top cosine similarity
#' with a large text chunk.
#' 
#' 
#' WAYS TO LINK THIS FUNCTION WITH VECTOR SPACES FUNCTION:
#' 
#' A) We can append these shortened sentence group
#' chunks as children and get their individual vector spaces. - Append a 
#' True/False column that states whether the chunk is a long chunk. 
#' Check for true. Go to sentence group children, return the sentence group 
#' from the og chunk that has the highest cosine similarity 
#' 
#' 
#' B) We can check the word counts of query results with top cosine similarity 
#' to determine if they need any sentence grouping, if they do, create groups, 
#' compute cosine similarity of sentence groups to the prompt, and spit a new
#' "final" chatbot response with the relevant sentence group.


#' Libraries

#install.packages(
#  "openNLPmodels.en",
#  repos = "http://datacube.wu.ac.at/",
#  type = "source"
#)

library(stringr)
library(dplyr)
library(NLP)
library(openNLP)
library(openNLPmodels.en)
library(rJava)



#' 1) Load in corpus_sections (the version without titles) and urls

corpus <- readRDS("Downloads/text_chunks_df.rds")


corpus <- data.frame(ID = corpus$local_id, 
                                parent_ID = corpus$parent_id,
                                text = corpus$sub_chunks)


# 2)  Helper: count words
count_words <- function(text) {
  sapply(strsplit(text, "\\s+"), length)
}



# Make sentence groups function
make_sentence_groups <- function(df, tolerance = 0.2) {
 
   # Step 1: Count words and compute Q3
  word_counts <- count_words(df$text)
  q3 <- quantile(word_counts, 0.75, na.rm = TRUE)
  mean_wc <- mean(word_counts, na.rm = TRUE)
  lower_bound <- mean_wc * (1 - tolerance)
  upper_bound <- mean_wc * (1 + tolerance)
  
  # Sentence annotator
  sent_annotator <- Maxent_Sent_Token_Annotator()
  
  # Container for results
  result <- list()
  
  for (i in seq_along(df$text)) {
    text <- df$text[i]
    
    if (word_counts[i] > q3) {
     
       # Convert to NLP string
      nlp_str <- as.String(text)
      
      # Get sentence boundaries
      sentence_annots <- annotate(nlp_str, sent_annotator)
      sentences <- sapply(sentence_annots, function(a) {
        substr(nlp_str, a$start, a$end)
      })
      
      # Group adjacent sentences into mean-length chunks
      chunks <- list()
      current_chunk <- ""
      current_count <- 0
      
      for (sent in sentences) {
        sent_wc <- count_words(sent)
        current_chunk <- paste(current_chunk, sent)
        current_count <- current_count + sent_wc
        
        if (current_count >= lower_bound && current_count <= upper_bound) {
          chunks[[length(chunks) + 1]] <- trimws(current_chunk)
          current_chunk <- ""
          current_count <- 0
        }
      }
      
      # Catch any trailing sentences
      if (nchar(current_chunk) > 0) {
        chunks[[length(chunks) + 1]] <- trimws(current_chunk)
      }
      
      result[[i]] <- chunks
    } else {
      result[[i]] <- df$text[i]  # Keep unchanged
    }
  }
  
  return(result)
}


#check <- make_sentence_groups(corpus)
#print(check)