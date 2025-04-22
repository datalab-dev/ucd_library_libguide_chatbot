library(xml2)
library(rvest)

full_data <- readRDS("/Users/quin/Documents/ucd/sts195/2025_startup_libguide_chatbot/data/added_url_recursion.rds")

# Extract the first 6 rows
test_data <- full_data[1:6, ]


# Get subheading
extract_subheading <- function(node) {
  a_node <- xml_find_first(node, ".//a[normalize-space(text()) != '']")
  if (!is.na(a_node) && nchar(xml_text(a_node)) > 0) {
    return(xml_text(a_node))
  }
  
  div <- xml_find_all(node, "//div[contains(@class, 'l-content')]")
  box_ancestor <- xml_find_first(div, "//div[contains(@class, 's-lib-box')]")
  heading <- xml_find_first(box_ancestor, ".//h2[contains(@class, 's-lib-box-title')]")
  if (!is.na(heading)) {
    return(xml_text(heading))
  }
  
  return(NA_character_)
}

# Get URL
extract_url <- function(node) {
  link <- xml_find_first(node, ".//a[@href]")
  if (!is.na(link)) {
    return(xml_attr(link, "href"))
  }
  return(NA_character_)
}


# Main function to apply
separate_text_chunks <- function(old_df, old_id) {
  raw_data <- old_df$raw_xml[old_id]
  if (is.na(raw_data)) return(NULL)
  
  extracted_data <- read_html(raw_data)
  
  # Find all content blocks
  sub_divs <- xml_find_all(extracted_data, "//div[starts-with(@id, 's-lg-content-')]") #
  if (length(sub_divs) == 0) return(NULL)
  
  #from federico's code - this is not working properly --> there are duplicates and some missing
  sub_content <- xml_find_all(
    sub_divs,
    ".//div[starts-with(@id, 's-lg-database-desc-') or starts-with(@id, 's-lg-link-desc-')]"
  )
  
  # Filter out empty or whitespace-only content
  sub_divs <- Filter(function(node) {
    text <- xml_text(node, trim = TRUE)
    return(nchar(text) > 5 || !is.na(extract_url(node)))
  }, sub_divs)
  
  
  if (length(sub_divs) == 0) return(NULL)
  
  # Extract everything
  sub_chunks <- sapply(sub_divs, html_text, trim = TRUE)
  sub_titles <- sapply(sub_divs, extract_subheading)
  sub_urls <- sapply(sub_divs, extract_url)
  
  # Assemble into data frame
  new_df <- data.frame(
    local_id = NA_integer_,
    parent_id = rep(old_id, length(sub_chunks)),
    sub_title = sub_titles,
    sub_chunks = sub_chunks,
    sub_url = sub_urls,
    stringsAsFactors = FALSE
  )
  
  return(new_df)
}

# Apply to all rows
list_of_results <- lapply(1:nrow(test_data), function(i) separate_text_chunks(test_data, i))

# Combine and finalize
text_chunks_df <- do.call(rbind, list_of_results)
text_chunks_df$local_id <- seq_len(nrow(text_chunks_df))

