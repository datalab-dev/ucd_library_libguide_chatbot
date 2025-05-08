library(ollamar)
library(stringr)

text_chunks_df <- readRDS("./text_chunks_df.rds")

list <- list()

for (n in corpus_section$text) {
  word_count <- str_count(n, boundary("word"))
  if (word_count > 100) {
    list <- append(list, n)
  }
}

wc <- c()
for (n in text_chunks_df$sub_chunks) {
  word_count <- str_count(n, boundary("word"))
  wc <- append(wc, word_count)
}

length(wc) # 7416
summary(wc) 
# Q1: 29
# Q3: 83
# max: 394, min: 1

length(wc[wc>89]) 
length(wc[wc<29])

v2_corpus_section <- data.frame(ID = text_chunks_df$local_id, text = text_chunks_df$sub_chunks)
# remove title + url

