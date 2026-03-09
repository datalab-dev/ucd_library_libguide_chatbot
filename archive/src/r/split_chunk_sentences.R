#' This file contains the code to break the sentence chunks into individual 
#' sentences. We want to record where each sentence came from (which local id -> 
#' chunk id). We also want to create a new sentence_id for each sentence. 


#' Load in the text_chunks_df.rds
text_chunks_df <- readRDS("~/Downloads/text_chunks_df.rds")

#' Load libraries
library(NLP)
library(openNLP)
library(openNLPmodels.en)
library(dplyr)
library(tidyr)


#' Create sentence annotator

sentence_annotator <- Maxent_Sent_Token_Annotator()


#' Use OpenNLP to extract sentences 

split_sentences <- function(text) {
  text_str <- as.String(text)
  sents <- annotate(text_str, Maxent_Sent_Token_Annotator())
  sapply(sents, function(sent) {
    substr(text_str, sent$start, sent$end)
  })
}


#' Split sentences

single_sentence <- text_chunks_df %>% 
  rowwise() %>%
  mutate(sentences = list(split_sentences(sub_chunks))) %>%
  unnest(sentences) %>%
  ungroup() %>%
  mutate(sentence_id = row_number()) %>%
  rename(chunk_id = local_id, sentence = sentences) %>%
  select(sentence_id, chunk_id, sentence)


#' Save the data frame 

saveRDS(single_sentence, file = "single_sentence_df.rds")
