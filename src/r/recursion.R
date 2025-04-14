#data <- read.RDS()
#flag = FALSE
#i = 1
#n = numrows(data)
#
#Do until(flag==TRUE}{
#  
#  (if added url to the dataframe){
#    n = n+1
#  }
#  i = 1 +1
#  if ( i ==n){flag==TRUE}
#}

library(xml2)
library(rvest)
library(httr)


#load RDS data
data <- readRDS('/Users/quin/Documents/ucd/sts195/2025_startup_libguide_chatbot/data/lib_guides_2025_02_28.rds')

# sublinks from the sidebar menu
get_sublink_chunk <- function(conts) {
  if (is.na(conts) || conts == "") return(character(0))  # skip bad content
  doc = read_html(conts)
  ret_nodeset1 <- xml_find_all(doc, "//ucdlib-lg-sidenav")
  ret_links <- xml_find_all(ret_nodeset1, "//li/a[@title = '' and @class = '']")
  justlinks <- xml_attr(ret_links, "href")
  return(justlinks) 
}

# get a list of lists of sublinks from all starting pages
sublinks <- lapply(data$raw_xml, get_sublink_chunk)

# make sublinks df (data frame of children)
sublinks_df <- do.call(rbind, lapply(seq_along(sublinks), function(i) {
  data.frame(
    parent_ID = i,
    url = sublinks[[i]],
    stringsAsFactors = FALSE
  )
}))

# Fetch raw HTML content
fetch_url_contents <- function(urls) {
  sapply(urls, function(url) {
    tryCatch({
      Sys.sleep(2)  # Slow down to be nice to servers
      print(paste("Fetching:", url))
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

# Check if URL already exists in dataframe
unique_url_checker <- function(url, dataframes) {
  url_exist <- url == dataframes[, "url"]
  if (any(url_exist)) {
    return(dataframes[url_exist, "ID"])
  } else {
    return(NA)
  }
}


#recursive function that take in data as parameter
recursive_add_url <- function(data) {
  #intializes variables
  flag <- TRUE
  i <- 1
  n <- nrow(data)
  
  
  #while loop: Do until(flag==FALSE) -> stop when flag == FALSE
  while(flag) {
    #let the parent url be the url from data
    parent_url <- data$url[i]
    #let the parent id be the id from data
    parent_id <- data$ID[i]
    
    # extract sublinks from the current page
    raw_xml <- data$raw_xml[i]
    #skip na
    if (is.na(raw_xml) || raw_xml == "") {
      i <- i + 1
      next  # skip to next iteration
    }
    sublinks <- get_sublink_chunk(raw_xml)
    
    #for loop    
    #check if the url exist every child (?) -> calling (unique url checker function)
    if (length(sublinks) > 0) {
      for (child_url in sublinks) {
        # check if child URL already exists
        existing_id <- unique_url_checker(child_url, data)
        
        #if id doesn't exist
        if (is.na(existing_id)) {
          # New URL — fetch HTML and assign new ID
          child_raw <- fetch_url_contents(child_url)
          child_id <- nrow(data) + 1
          
          new_row <- data.frame(
            ID = child_id,
            url = child_url,
            raw_xml = child_raw,
            parent_ID = parent_id,
            stringsAsFactors = FALSE
          )
          
          # add unique ID column if it doesn't exist
          if (!"ID" %in% colnames(data)) {
            data$ID <- seq_len(nrow(data))
          }
          
          # add parent_ID column if missing
          if (!"parent_ID" %in% colnames(data)) {
            data$parent_ID <- NA
          }
          
          data <- rbind(data, new_row)
          n <- n + 1  # increase total number of rows
        } else {
          # else: already exists — add parent-child link only
          child_id <- existing_id
        }
      }
    }         
    
    
    i <- i + 1
    if (i > n) {
      flag <- FALSE
    }
  }
  
  return(data)
}


result_df <- recursive_add_url(data) 
#not sure if the importance of this error after calling the function: 
#<error/rlang_error>
#  Error in `read_xml()`:
#  ! `x` must be a single string, not a character `NA`.

#save rds
saveRDS(result_df, file = "/Users/quin/Documents/ucd/sts195/2025_startup_libguide_chatbot/data/added_url_recursion.rds")


  
