library(dplyr)


# this file is for creating the relationship data frame
# it uses the rds file of urls that were added recursively to match parents and
# children + cleans the dataframe up

# I can try to make the function more dynamic 



# load the added_url_recursion file (all of the urls and parent info are on this)
relationship_df <- readRDS("~/Downloads/added_url_recursion.rds")

# change ID and parent_ID to character to help with matching
relationship_df$ID <- as.character(relationship_df$ID)
relationship_df$parent_ID <- as.character(relationship_df$parent_ID)

# make the children column
relationship_df$children <- sapply(relationship_df$ID, function(id) {
  kids <- relationship_df$ID[!is.na(relationship_df$parent_ID) & relationship_df$parent_ID == id]
  if (length(kids) == 0) NA else paste(kids, collapse = ",")
})


# remove xml content from relationship data frame
relationship_df <- relationship_df %>% select(-raw_xml)

# change the row names because some had urls as row names 
rownames(relationship_df) <- relationship_df$ID

# save the rds file
saveRDS(relationship_df, file = "relationship_df.rds")

# during our meeting on 4/14 we decided that it would be best to append 
# the children in a a new column, but make it a column with the children 
# separated by commas to make this file useful if we needed it to be csv down 
# the line

# we also noticed that my initial lib_guides_children file had fewer rows than 
# added_url_recursion.rds. This was just because the function I had
# wasn't under the the recursive function yet!!!

