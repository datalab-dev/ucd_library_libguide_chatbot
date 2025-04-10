# Write a function(url, ID = optional) that get raw xml for url then adds a 
# new row if there is no existing ID, otherwise updates the value in the dataframe.

get_html <- function(url, ID) {
  # check if the given url exists in the df and if so, print its raw_xml 
  url_exist <- url == lib_guides_2025_02_28[, "url"]
   print(lib_guides_2025_02_28[url_exist, "raw_xml"])
   
   # if the given url does not exist in the df already, add a new row to the df
   if (sum(url_exist) == 0) {
     new_url <- data.frame(
       ID = nrow(lib_guides_2025_02_28) + 1,
       url = url,
       raw_xml = fetch_url_contents(url)
     )
     lib_guides_2025_02_28 <- rbind(lib_guides_2025_02_28, new_url)
   }
}

# generalize to any df + update raw_xml value
get_html <- function(url, dataframes, ID) {
  # check if the given url exists in the df and if so, print its raw_xml 
  url_exist <- url == dataframes[, "url"]
  dataframes[url_exist, "raw_xml"] <- fetch_url_contents(url_exist) # look
  
  # if the given url does not exist in the df already, add a new row to the df
  if (sum(url_exist) == 0) {
    new_url <- data.frame(
      ID = nrow(dataframes) + 1,
      url = url,
      raw_xml = fetch_url_contents(url)
    )
    dataframes <- rbind(dataframes, new_url)
  }
}