urls <- read.csv("/Users/cstahmer/Desktop/libguides.csv", header=FALSE)
colnames(urls) <- c("url")

library(httr)

fetch_url_contents <- function(urls) {
  contents <- sapply(urls, function(url) {
    tryCatch({
      Sys.sleep(3)
      print(url)
      response <- GET(url)
      if (status_code(response) == 200) {
        return(content(response, as = "text", encoding = "UTF-8"))
      } else {
        return(NA)  # Return NA if the request fails
      }
    }, error = function(e) {
      return(NA)  # Return NA if an error occurs
    })
  })
  return(contents)
}

raw_conts <- fetch_url_contents(urls$url)

urls$raw_xml <- raw_conts

urls2 <- data.frame(1:160, urls$url, urls$raw_xml)

colnames(urls2) <- c("ID", "url", "raw_xml")

saveRDS(urls2, "/Users/cstahmer/Desktop/lib_guides_2025_02_28.rds")


