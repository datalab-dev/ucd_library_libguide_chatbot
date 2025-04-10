unique_url_checker <- function(url) {
  url_exist <- url == lib_guides_2025_02_28[, "url"]
  print(lib_guides_2025_02_28[url_exist, "ID"])
  
  if (sum(url_exist) == 0) {
    print(NA)
  }
}
