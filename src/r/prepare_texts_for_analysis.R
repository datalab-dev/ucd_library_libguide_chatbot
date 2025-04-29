
# this script will create the corpus dataframes
# This needs to be rerun once the ENG03 page is scraping correctly
# I can upload the parent titles with no missing titles to outputs because that 
# is working fine


# df corpus_sections
#   id, text 
#   id of the subsection
#   text in this case refers to page title, subsection title and it's text


# df corpus_whole
#     id, text
#     id of the root 
#     text in this case refers to page title, all subsection titles and all of 
#     the subsection text


# load libraries
library(dplyr)


# load in added_parent_title.rds and use columns: ID, url, parent_id, title

added_parent_title <- readRDS("~/Downloads/added_parent_title.rds")
colnames(added_parent_title)
added_parent_title <- added_parent_title[, c("ID", "url", "parent_ID", "title")]


# FIX NA TITLES IN ADDED_PARENT_TITLES

# add root titles to the children iteratively

# create a lookup environment for fast access
id_to_parent <- setNames(added_parent_title$parent_ID, added_parent_title$ID)
id_to_title <- setNames(added_parent_title$title, added_parent_title$ID)

# function to find the grand or great grand title
find_title <- function(id) {
  current_id <- id
  while (!is.na(current_id)) {
    title <- id_to_title[[as.character(current_id)]]
    if (!is.na(title)) {
      return(title)
    }
    current_id <- id_to_parent[[as.character(current_id)]]
  }
  return(NA)
}

# apply it to every row
added_parent_title$title <- sapply(added_parent_title$ID, find_title)


# check for NA - should be 160 unique
unique(added_parent_title$title)

saveRDS(added_parent_title, file = "parent_titles_no_na.rds")


# load in text_chunks_df.rds and use all columns

text_chunks_df <- readRDS("~/Downloads/text_chunks_df.rds")


# MAKE A CENTRAL DATAFRAME TO USE FOR MAKING 2 CORPUSES

corpus_work <- text_chunks_df %>% 
  left_join(added_parent_title %>% select(ID, title), by = c("parent_id" = "ID"))


# REORDER AND RENAME

# reorder
corpus_work <- corpus_work[, c("local_id", 
                               "parent_id", 
                               "title", 
                               "sub_title", 
                               "sub_chunks", 
                               "sub_url")]

# rename 
corpus_work <- corpus_work %>%
  rename(
    local_id = local_id,
    parent_id = parent_id,
    lib_title = title,
    sub_title = sub_title,
    sub_title_text = sub_chunks,
    sub_title_url = sub_url)


saveRDS(corpus_work, file = "corpus_work.rds")



# CHECK THE DATAFRAME
unique(corpus_work$lib_title)
# ^ this only maps 159 unique libtitles - there is a special case where ENG 3 
# has multiple tabs on the page that are not being scraped



list159 <- unique(corpus_work$lib_title)  
list160 <- unique(id_title_lookup$title)

missing_item <- setdiff(list160, list159)



# RERUN TO MAKE TWO CORPUSES AFTER FIXING THE ENG 03 CASE


# MAKE CORPUS_SECTIONS

corpus_sections <- data.frame(
  ID = corpus_work$local_id,
  text = paste(corpus_work$lib_title, 
               corpus_work$sub_title, 
               corpus_work$sub_title_text,
               corpus_work$sub_title_url,
               sep = " : "),
  stringsAsFactors = FALSE
)
  
 

# MAKE CORPUS_WHOLE

corpus_working <- corpus_work

corpus_working$lib_title <- as.character(corpus_working$lib_title)

corpus_working <- corpus_working %>%
  mutate(sub_text = paste(sub_title, sub_title_text, sub_title_url, sep = " : "))

corpus_whole <- corpus_working %>%
  group_by(lib_title) %>%
  summarise(
    text = paste(sub_text, collapse = " / "),
    .groups = "drop"
  ) %>%
  mutate(
    text = paste(lib_title, text, sep = " / "), 
    ID = row_number()
  ) %>%
select(ID, text)



