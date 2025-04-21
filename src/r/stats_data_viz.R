library(ggplot2)
library(stringr)
library(gridExtra)
library(grid)

# function that adds word counts and character counts to df
get_basic_stats <- function(df, chunk){
  # word count
  word_count <- str_count(df[[chunk]], boundary("word"))
  
  # character count
  chunk_cat <- str_remove_all(df[[chunk]], " ")
  character_count <- str_length(chunk_cat)
  
  # add word_count and character_count as new columns of df
  df <- cbind(df, word_count, character_count)
  return(df)
}


# function that generates boxplots 
make_box <- function(df, col, title) {
  ggplot(df) +
    aes(x = {{col}}) +
    geom_boxplot() +
    labs(title = title)
}


# function that generates histograms 
histogram <- function(df, col, title, xlab) {
  ggplot(df) +
    aes(x = {{col}}) +
    geom_histogram(binwidth = 25)+
    labs(title = title,
         x = xlab,
         y = "Frequencies")
}



# create and save the new df containing word and character counts
chunks_count <- get_basic_stats(text_chunks_df, "sub_chunks")
saveRDS(chunks_count, file = "/Users/sebrina/sts195/data/word_character_count.rds")


# create and save the box plots
word_box <- make_box(chunks_count, word_count, "Word Counts of Subchunk Text")
character_box <- make_box(chunks_count, character_count, "Character Counts of Subchunk Text")
ggsave(plot = word_box, "/Users/sebrina/sts195/word_count_boxplot.pdf")
ggsave(plot = character_box, "/Users/sebrina/sts195/character_count_boxplot.pdf")


# create and save the summary tables of word and character counts
summary_table <- function(df, col, filename){
  table <- summary(df[[col]])
  table_df <- data.frame(Statistics = names(table),
                         Value = format(unname(table))) # convert the "table" to a df
  pdf(filename)
  grid.table(table_df)
  dev.off()
} 
summary_table(chunks_count, "character_count", "/Users/sebrina/sts195/character_count_summary.pdf")
summary_table(chunks_count, "word_count", "/Users/sebrina/sts195/word_count_summary.pdf")


# create and save the histogram plots
word_hist <- histogram(chunks_count, word_count, "Word Counts Bin by 25", "Word Counts")
character_hist <- histogram(chunks_count, character_count, "Character Counts Bin by 25", "Character Counts")
ggsave(plot = word_hist, "/Users/sebrina/sts195/word_count_hist.pdf")
ggsave(plot = character_hist, "/Users/sebrina/sts195/character_count_hist.pdf")
