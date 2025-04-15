#' Determine XML structure/nodes we can use to extract usable text from raw_xml
#' Write a function that extracts the text
library(xml2)

# loading in the updated data (including parent_id and children as new links/rows)
data3 = readRDS("~/my_projects/my_R_stuff/data_sets/added_url_recursion.rds")
saveRDS(data3, "~/my_projects/extracted_url_text.rds")


# FUNCTION VERSION 1 (if within recursion function)
xml_to_text <- function(df, id) {
  
  raw_data <- df$raw_xml[id] # Get row data
  extracted_data <- read_html(raw_data) # Parse the raw HTML/XML
  if (is.na(raw_data)) stop("ID or xml data not found in dataframe") # Halt if data or ID not found
  
  
  # Initialize new columns if they don't exist yet
  if (!"extracted_text" %in% names(df)) df$extracted_text <- NA
  if (!"extracted_links" %in% names(df)) df$extracted_links <- NA
  
  
  
  # MAIN CONTENT INTRODUCTION
  # Get the main content container
  main_div <- xml_find_all(extracted_data, "//div[contains(@class, 'l-content')]")
  
  # Find all paragraph tags within the main content
  main_content <- xml_find_all(main_div, ".//p")
  
  # Extract text from those paragraphs
  main_text <- xml_text(main_content)
  
  
  
  # MAIN CONTENT SUBSECTIONS (TEXT)
  # Find all subsections with content IDs (used to scope later queries)
  sub_divs <- xml_find_all(extracted_data, "//div[starts-with(@id, 's-lg-content-')]")
  
  #' Some guides use a tabbed interface (e.g., "Background", "Foreground") where each tab has its own
  #' set of database descriptions. These descriptions are stored in divs with IDs like
  #' 's-lg-database-desc-' or 's-lg-link-desc-'.
  sub_content <- xml_find_all(
    sub_divs,
    ".//div[starts-with(@id, 's-lg-database-desc-') or starts-with(@id, 's-lg-link-desc-')]"
  )
  sub_text <- xml_text(sub_content)  # Extract text from description blocks
  
  
  
  # MAIN CONTENT SUBSECTIONS (LINKS)
  sub_links <- xml_find_all(sub_divs, ".//a")  # Find all anchor tags within the subsections
  sub_hrefs <- xml_attr(sub_links, "href")  # Extract the href attribute (URLs or email links)
  # Optionally: filter links vs. email addresses later (e.g., grepl("^mailto:", sub_hrefs))
  
  
  
  # Format main and subsection text giving them "Labels" for convenience later
  intro_text <- paste(main_text, collapse = "\n")
  
  if (length(sub_text) == 0) {
    combined_text <- paste("Introduction:\n", intro_text)
    all_links_text <- paste("Links:", paste(sub_hrefs, collapse = ", "))
  } else {
    subsection_text <- paste(sub_text, collapse = "\n")
    combined_text <- paste(
      "Introduction:\n", intro_text,
      "\n\nSubsections:\n", subsection_text
    ) # Setting labels
    all_links_text <- paste("Links:", paste(sub_hrefs, collapse = ", "))
  }
  
  # Adding both to df
  df$extracted_text[id] <- combined_text
  df$extracted_links[id] <- all_links_text
  
  return(df)
}


# Applying function to all rows of dataframe
for (i in seq_len(nrow(data3))) {
  data3 <- xml_to_text(data3, i)
}





