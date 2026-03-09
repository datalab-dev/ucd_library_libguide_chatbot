library(xml2)
library(rvest)
library(stringr)

full_data <- readRDS("~/my_projects/my_R_stuff/data_sets/extracted_url_text.rds")

# Extract the first 6 rows for testing purposes
test_data <- full_data[1:6, ]



# Get subheading
extract_subheading <- function(node) {
  
  a_node <- xml_find_first(node, ".//a[normalize-space(text()) != '']") # Look for a link with non-empty text
  
  # If a valid link is found and it's not an email, return its text
  if (!is.na(a_node) && nchar(xml_text(a_node)) > 0 && !(str_detect(html_text(a_node), "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"))) {
    return(xml_text(a_node))
  }
  
  # Otherwise, look for a heading within a 's-lib-box' div and return it
  box_ancestor <- xml_find_first(node, "//div[contains(@class, 's-lib-box')]")
  heading <- xml_find_first(box_ancestor, ".//h2[contains(@class, 's-lib-box-title')]")
  if (!is.na(heading)){
    return(xml_text(heading))
  }
  
  return(NA_character_) # If no subheading found, return NA
}

# Get URL
extract_url <- function(node) {
  # Look for a link with an 'href' attribute (for url)
  link <- xml_find_first(node, ".//a[@href]")
  
  if (!is.na(link)) {
    return(xml_attr(link, "href")) # get attribute
  }
  return(NA_character_) # If none found return NA
}


# Main function to separate and extract chunks of text, subheadings, and URLs
separate_text_chunks <- function(old_df, old_id) {
  raw_data <- old_df$raw_xml[old_id]  # Extract raw XML from the dataset for the specific row
  if (is.na(raw_data)) return(NULL) # Null if no data
  
  extracted_data <- read_html(raw_data) # parsing
  
  # Find all main content blocks
  main_div <- xml_find_all(extracted_data, "//div[contains(@class, 'l-content')]")
  
  # Find sub-content blocks within the main content (these contain the text + URLs + subheadings)
  sub_divs <- xml_find_all(main_div, ".//div[starts-with(@id, 's-lg-content-')]")
  if (length(sub_divs) == 0) return(NULL)
  
  # Process each sub-content block extracting relevant text
  filtered <- lapply(sub_divs, function(div) {
    # Extract the content block, the actual relevant text
    sub_content <- xml_find_first(
      div,
      ".//div[starts-with(@id, 's-lg-database-desc-') or starts-with(@id, 's-lg-link-desc-')]"
    )
    
    if (is.na(sub_content)) return(NULL) # If no content, skip 
    
    # Extract the subheading and URL from the same div
    list(
      chunk = html_text(sub_content, trim = TRUE),
      title = extract_subheading(div),
      url = extract_url(div)
    )
  })
  
  # Remove NULLs
  filtered <- Filter(Negate(is.null), filtered)
  
  # If no valid chunks return NULL
  if (length(filtered) == 0) return(NULL)
  
  # Assemble the new data frame from the filtered results
  # Here using sapply functions to apply the [[ function to each element of 'filtered', which extracts the “title” or "chunk" or "url" element from each list in 'filtered'
  new_df <- data.frame(
    local_id = NA_integer_,
    parent_id = rep(old_id, length(filtered)),
    sub_title = sapply(filtered, `[[`, "title"),
    sub_chunks = sapply(filtered, `[[`, "chunk"),
    sub_url = sapply(filtered, `[[`, "url"),
    stringsAsFactors = FALSE
  )
  
  return(new_df)
}

# Apply to all rows
list_of_results <- lapply(1:nrow(full_data), function(i) separate_text_chunks(full_data, i))

# Combine (in one df) and finalize
text_chunks_df <- do.call(rbind, list_of_results)

# Assigning unique local ID to each row in the final data frame (because it's more convenient to do it at the end)
text_chunks_df$local_id <- seq_len(nrow(text_chunks_df))

saveRDS(text_chunks_df, file = "text_chunks_df.rds")
