# Replacing NAs with libguide titles --------------------------------------

added_parent_title <- readRDS("./libbot_data/added_parent_title.rds")

parent_ID <- added_parent_title$parent_ID
title <- added_parent_title$title

for (i in 161:1335) {
  title[i] <- added_parent_title$title[parent_ID[i]]
}
added_parent_title$title <- title

saveRDS(added_parent_title, './libbot_data/fine_tune_test1.rds') # for fine tuning



# Cleaning df into "libguide_full_data" ----------------------------------------

text_chunks_df <- readRDS('./libbot_data/text_chunks_df.rds')
libguide_data <- text_chunks_df
libguide_data$original_id <- NA
libguide_data$url <- NA
libguide_data$title <- NA

for (i in 1:nrow(libguide_data)) {
  original_id <- added_parent_title$parent_ID[text_chunks_df$parent_id[i]]
  if (is.na(original_id)) {
    original_id <- added_parent_title$ID[text_chunks_df$parent_id[i]]
  }
  libguide_data$original_id[i] = original_id
  libguide_data$title[i] = added_parent_title$title[text_chunks_df$parent_id[i]]
  libguide_data$url[i] = added_parent_title$url[text_chunks_df$parent_id[i]]
}

libguide_full_data <- libguide_data[c("local_id", "parent_id", "original_id",
                                      "title", "url", "sub_title", "sub_chunks", "sub_url")]

libguide_full_data$section_url <- NA

for (i in 1:nrow(libguide_full_data)) {
  parent_id <- libguide_full_data$parent_id[i]
  if (parent_id>160) {
    libguide_full_data$section_url[i] <- added_url_recursion$url[parent_id] 
  }
}

libguide_full_data <- libguide_full_data[c("local_id", "parent_id", "original_id",
                                           "title", "url", "sub_title", "section_url", "sub_chunks", "sub_url")]


# Pasting libguide titles AND subsection titles ---------------------------

# given sentence_groups_df.rds with ~8k rows, column: ID, parent_ID, text

sentence_groups_df <- readRDS("C:/Users/HOME/libbot_data/sentence_groups_df.rds")

sentence_groups_df$pasted_text <- NA

parent_ID <- sentence_groups_df$chunk_id

for (i in 1:nrow(sentence_groups_df)) {
  id <- as.numeric(parent_ID[i])
  sentence_groups_df$pasted_text[i] <- paste(libguide_full_data$title[id],
                                             libguide_full_data$sub_title[id],
                                             sentence_groups_df$text[i])
}

saveRDS(sentence_groups_df, "./libbot_data/sentence_groups_df.rds")

# Cleaning df into 'text_full_libguide' ---------------------------------------

text_full_libguide <- sentence_groups_df[-4] # delete pasted text
sentence_groups_df$chunk_id <- as.numeric(sentence_groups_df$chunk_id)

# adding new columns
text_full_libguide$parent_id <- NA
text_full_libguide$libguide_title <- NA
text_full_libguide$libguide_url <- NA
text_full_libguide$chunk_title <- NA
text_full_libguide$chunk_url <- NA
text_full_libguide$external_url <- NA

for (i in 1:nrow(text_full_libguide)) {
  chunk_id <- text_chunks_df$parent_id[sentence_groups_df$chunk_id[i]]
  original_id <- added_parent_title$parent_ID[chunk_id]
  text_full_libguide$chunk_url[i] <- added_parent_title$url[chunk_id]
  if (is.na(original_id)) {
    original_id <- added_parent_title$ID[text_chunks_df$parent_id[sentence_groups_df$chunk_id[i]]]
    text_full_libguide$chunk_url[i] <- NA
  } else if (original_id > 160) {
    not_original_id <- original_id
    original_id <- added_parent_title$parent_ID[not_original_id]
  }
  text_full_libguide$parent_id[i] = chunk_id
  text_full_libguide$libguide_title[i] = added_parent_title$title[original_id]
  text_full_libguide$libguide_url[i] = added_parent_title$url[original_id]
  text_full_libguide$external_url[i] = text_chunks_df$sub_url[chunk_id]
  text_full_libguide$chunk_title[i] = text_chunks_df$sub_title[sentence_groups_df$chunk_id[i]]
}

text_full_libguide <- text_full_libguide[c("local_id", "parent_id", "text", "libguide_title",
                                           "libguide_url", "chunk_title", "chunk_url", "external_url")]

# Note: chunk_url is NA when the text "chunk" belongs to original libguide, i.e.
# when chunk_url == libguide_url

saveRDS(text_full_libguide, "./libbot_data/text_full_libguide.rds")
dim(text_full_libguide)
