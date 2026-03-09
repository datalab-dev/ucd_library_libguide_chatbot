# Task 1: Write a function to check if a url exists in any dataframe and if so returns the ID, otherwise returns NA.

unique_url_checker <- function(url) {
  url_exist <- url == lib_guides_2025_02_28[, "url"]
  print(lib_guides_2025_02_28[url_exist, "ID"])
  
  if (sum(url_exist) == 0) {
    print(NA)
  }
}

# generalize the function for any dataframe

unique_url_checker <- function(url, dataframes) { # new argument
  url_exist <- url == dataframes[, "url"]
  print(dataframes[url_exist, "ID"])
  
  if (sum(url_exist) == 0) {
    print(NA)
  }
}

