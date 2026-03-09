install.packages("xml2")
install.packages("rvest")

library(xml2)
library(rvest)

# load the data
datafile <- readRDS("/Users/cstahmer/workspaces/projects/2025_lib_guide_rag/data/lib_guides_2025_02_28.rds")

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
