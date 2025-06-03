library(xml2)
library(rvest)
library(stringr)

df <- readRDS("C:/Users/HOME/libbot_data/lib_guides_2025_02_28.rds")
df2 <- readRDS("C:/Users/HOME/libbot_data/extracted_url_text.rds")

# "scraping title" function

scrape_title <- function(df, id) {
  data <- df$raw_xml[id]
  
  if (is.na(data)) {
    data <- df$raw_xml[df$parent_id[id]]
  }
  
  if (is.na(data)) {
    return(NA)
  }
  
  doc = read_html(data)
  div <- xml_find_all(doc, "//h1[@class='page-title u-space-mb']")
  title <- xml_text(div) 
  new_title <- str_remove_all(title, '\r\n +') # remove junk
  return(new_title)
}

# create vector + add to df

all_title <- c()
for (i in 1:nrow(df)) {
  all_title <- append(all_title, scrape_title(df, i))
}

length(all_title) <- nrow(df2)
df2$title = all_title
df2

saveRDS(df2, 'C:/Users/Home/libbot_data/added_parent_title.rds')

# update 5/19: scrape libguide title for all

added_parent_title <- readRDS("C:/Users/HOME/libbot_data/added_parent_title.rds")

added_parent_title[161,]

all_title <- c()
for (i in 1:1335) {
  all_title <- append(all_title, scrape_title(added_parent_title, i))
}
nrow(added_parent_title)
View(added_parent_title[765,])
all_title

added_parent_title[is.na(added_parent_title$raw_xml),]

added_parent_title$raw_xml[added_parent_title$parent_ID[772]]
