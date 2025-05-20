# Replacing NAs with libguide titles --------------------------------------

added_parent_title <- readRDS("./libbot_data/added_parent_title.rds")

parent_ID <- added_parent_title$parent_ID
title <- added_parent_title$title

for (i in 161:1335) {
  title[i] <- added_parent_title$title[parent_ID[i]]
}
added_parent_title$title <- title

saveRDS(added_parent_title, './libbot_data/fine_tune_test1.rds') # for fine tuning



# Cleaning df into "libguide_data" ----------------------------------------

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

saveRDS(libguide_full_data, "./libbot_data/libgude_full_data.rds")



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

# Preparing to paste libguide links and extracted links -------------------

sentence_groups_df$full_text <- NA

for (i in 1:nrow(sentence_groups_df)) {
  id <- as.numeric(parent_ID[i])
  sentence_groups_df$full_text[i] <- paste(libguide_full_data$title[id],
                                           '\n', libguide_full_data$sub_title[id],
                                           '\n', libguide_full_data$sub_title[id],
                                           '\n', sentence_groups_df$text[i],
                                           '\n', libguide_full_data$sub_url[id])
}


