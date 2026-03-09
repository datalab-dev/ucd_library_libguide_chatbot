library(stringr)

# Get the intro text of parents
extracted_url_text <- readRDS("~/sts195/data/extracted_url_text.rds")
parent_text_no_sub <- str_remove(extracted_url_text$extracted_text, "(?s)Subsections:.*")
intro_text <- str_remove(parent_text_no_sub, "Introduction:\\n ")
intro_text <- ifelse(is.na(intro_text), "", intro_text)
parent_df <- data.frame(
  ID = extracted_url_text$ID,
  parent_ID = extracted_url_text$parent_ID,
  text = intro_text
)

# Append parent_df to v2_corpus_section
v2_corpus_section$ID <- 1336:(1335+nrow(v2_corpus_section))
v2_corpus_section2 <- rbind(parent_df, v2_corpus_section)


# Q1 = 29

for (i in 1:length(wc)) {
  if (wc[i] < 29) {
    small_sections <- v2_corpus_section2$text[1335+i]
    parentID <- v2_corpus_section2$parent_ID[1335+i]
    match <- which((v2_corpus_section2$ID) == parentID)
    parent <- v2_corpus_section2[match, ]$text 
    v2_corpus_section2[match, ]$text <- paste(parent, small_sections)
    v2_corpus_section2$text[1335+i] <- NA
  }
}

v2_corpus_section <- v2_corpus_section2[!is.na(v2_corpus_section2$text), ]
v2_corpus_section <- v2_corpus_section[!str_detect(v2_corpus_section$text, "^\\s*$"), ]
v2_corpus_section$text <- str_trim(v2_corpus_section$text) # remove trailing and leading white spaces

saveRDS(v2_corpus_section, file = "~/sts195/data/v2_corpus_section_no_small_chunks.rds")

# New v2_corpus_section has 6512 rows after pasting small sections to their parents.
