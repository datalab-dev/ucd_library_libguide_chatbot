#install.packages("xml2")
#install.packages("rvest")

library(xml2)
library(rvest)
library(httr)

# load the data
datafile <- readRDS("/Users/ayanacarpenter/Downloads/lib_guides_2025_02_28.rds")

# function that takes a chunk of raw html and returns the 
# sublinks from the sidebar menu
get_sublink_chunk <- function(conts) {
  doc = read_html(conts)
  ret_nodeset1 <- xml_find_all(doc, "//ucdlib-lg-sidenav")
  ret_links <- xml_find_all(ret_nodeset1, "//li/a[@title = '' and @class = '']")
  justlinks <- xml_attr(ret_links, "href")
  return(justlinks) 
}

# get a list of lists of sublinks from all starting pages
sublinks <- lapply(datafile$raw_xml, get_sublink_chunk)

# make sublinks df (data frame of children)
sublinks_df <- do.call(rbind, lapply(seq_along(sublinks), function(i) {
  if (length(sublinks[[i]]) == 0) return(NULL)  # Skip if no sublinks
  data.frame(
    parent_ID = i,
    url = sublinks[[i]],
    stringsAsFactors = FALSE
  )
}))

# fetch the url contents for all of the sublinks (CAUTION this took forever
# when I ran it below)
fetch_url_contents <- function(urls) {
  sapply(urls, function(url) {
    tryCatch({
      Sys.sleep(3)  # Pause to avoid hammering the server
      print(url)
      response <- GET(url)
      if (status_code(response) == 200) {
        content(response, as = "text", encoding = "UTF-8")
      } else {
        NA
      }
    }, error = function(e) {
      NA
    })
  })
}

# apply the raw_xml information to the sublinks_df (THIS TOOK FOREVER)
sublinks_df$raw_xml <- fetch_url_contents(sublinks_df$url)


# give NA parent_id to the original datafile 
datafile$parent_ID <- NA

# add ids to sublinks_df, start the count from the end of datafile
sublinks_df$ID <- seq(nrow(datafile) + 1, nrow(datafile) + nrow(sublinks_df))

# save the sublink rds as lib_guide_children 
saveRDS(sublinks_df, file = "lib_guide_children.rds")


# reorder columns in both data frames to match: ID, url, raw_xml, parent_ID
datafile <- datafile[, c("ID", "url", "raw_xml", "parent_ID")]
sublinks_df <- sublinks_df[, c("ID", "url", "raw_xml", "parent_ID")]

# combine into a single data frame
parents_children <- rbind(datafile, sublinks_df)


# save the file
saveRDS(parents_children, file = "parents_children.rds")






# Notes from the original get_sub_pages.R function - 
# I think steps 1-3 can be checked off

# next I need to
# 1.  Add a column to the master dataframe that tracks the
#.    parent link.  Set to 0 for starting list
#
# 2.  write a function that goes and gets the raw html
#.    for all of the sub links collected for each page
#.    then adds that to the master dataframe setting
#.    the appropriate parent
#
# 3.  Write a function that extracts just the text conent
#.    from the raw html saved for each url
# 
# 4.  Go and get just the text content from the raw
#.    html for every page and saves just the text 
#.    content as a new column in the dataframe.  Do this
#.    in anoyther code file.
