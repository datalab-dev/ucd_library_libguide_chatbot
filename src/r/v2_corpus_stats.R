## Cleaning Corpus & Stats ##--------------------------------------------------

library(ollamar)
library(stringr)

# original data that has sections with no title & url
text_chunks_df <- readRDS("./libbot_data/text_chunks_df.rds")

# new data frame
v2_corpus_section <- data.frame(ID = text_chunks_df$local_id, 
                                parent_ID = text_chunks_df$parent_id,
                                text = text_chunks_df$sub_chunks)
text = v2_corpus_section$text

wc <- c()
for (n in text) {
  word_count <- str_count(n, boundary("word"))
  wc <- append(wc, word_count)
}

summary(wc) 
length(wc[wc<29]) # below Q1
length(wc[wc>89]) # above Q3

# Statistics on word count (with title + url removed):
# max = 394, min = 1, Q1 = 29, Q = 83
# for wc = 1, sub_chunk only has the word "Article" -> could remove


## Parsing Sentences & Stats ##-------------------------------------------------

install.packages("rJava")
install.packages("openNLP")
Sys.setenv(JAVA_HOME='C:/Program Files/Java/jre1.8.0_451')

library(rJava)
library(openNLP)

sentence_annotator <- Maxent_Sent_Token_Annotator()

text_sentences <- lapply(text, function(x) annotate(x, sentence_annotator))

sentence_list = list()  # list that parsed each section into list of sentences
sentence_count = c()    # vector containing the sentence count for each section

for (n in 1:length(text)) {
  string_text <- as.String(text[n])
  parsed_text <- string_text[text_sentences[[n]]]
  sentence_list <- append(sentence_list, list(parsed_text))
  sentence_count <- append(sentence_count, length(parsed_text)) 
}

summary(sentence_count)
# Statistics on number of sentences in each section:
# max = 18, minimum = 1, median = 3, mean = 3.348