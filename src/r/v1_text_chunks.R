library(xml2)
library(rvest)


# First 6 rows of the data, for testing 
test_data <- readRDS("~/my_projects/my_R_stuff/data_sets/testing_data_2.rds")



# Define a function that extracts and structures text chunks from a specific row
separate_text_chunks <- function(old_df, old_id) {
  
  raw_data <- old_df$raw_xml[old_id] # Get row data
  extracted_data <- read_html(raw_data) # Parse the raw HTML/XML
  
  # Find all main content divs (those with ids starting with "s-lg-content-")
  sub_divs <- xml_find_all(extracted_data, "//div[starts-with(@id, 's-lg-content-')]")
  
  # Within those, find text blocks
  sub_content <- xml_find_all(
    sub_divs,
    ".//div[starts-with(@id, 's-lg-database-desc-') or starts-with(@id, 's-lg-link-desc-')]"
  )
  
  # Extract the text content from those divs
  sub_text <- html_text(sub_content)
  
  
  # If there's no extracted text, skip this row by returning NULL
  if (length(sub_text) == 0) return(NULL)
  
  # Create a new mini-dataframe where each text chunk gets its own row
  new_rows <- data.frame(
    id = NA_integer_,                          # id gets added below 
    parent_id = rep(old_id, length(sub_text)), # original row number to know which page it came from
    sub_chunks = sub_text,                     # each chunk of extracted text
    sub_title = NA_character_,                 # placeholder; still working on getting these
    sub_url = NA_character_,                   # placeholder; still working on getting these
    stringsAsFactors = FALSE
  )
  
  return(new_rows)
}


# Apply the function to every row in the original dataframe
# This produces a list of dataframes, one per row
list_of_dfs <- lapply(1:nrow(test_data), function(i) separate_text_chunks(test_data, i))

# Combine all the individual dataframes into one master dataframe
text_chunks_df <- do.call(rbind, list_of_dfs)

# Add a unique ID to each row (now that the dataframe is finalized)
text_chunks_df$id <- seq_len(nrow(text_chunks_df))

