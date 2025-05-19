vector_corpus_sections <- readRDS("~/sts195/data/vector_corpus_sections.rds")
vector <- vector_corpus_sections$text_embeddings

vector_df_all <- data.frame()

for (i in 1:length(vector)) {
  unnested_vector <- unlist(vector[i])
  vector_df_row <- data.frame(unnested_vector)
  vector_df_column <- data.frame(t(vector_df_row))
  vector_df_all <- rbind(vector_df_all, vector_df_column)
}
View(vector_df_all)

unnested_vector_sections <- cbind(vector_corpus_sections$ID, vector_df_all)
colnames(unnested_vector_sections) [1] <- "ID"
rownames(unnested_vector_sections) <- NULL
View(unnested_vector_sections)

saveRDS(unnested_vector_sections, file = "~/sts195/data/unnested_vector_sections.rds")
