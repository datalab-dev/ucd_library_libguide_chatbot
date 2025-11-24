4layer_embedding_space.py ==> creates embedding vector space using a mean pool over the last 4 hidden layers of BERT
embedding_space.py ==> creates embedding vector space using a mean pool over just the last hidden layer
testing_small_embedding_space.py ==> creating small embedding vector spaces and testing search functions over them

search_testing.py ==> general search function (query compared to embedding vector space)
smaller_sample_search.py ==> selective search function (can specify how many rows to work with)




bert_testing.py ==> early simple testing of bert with single text chunk

df_url_crawl.py ==> getting the links to all the libguides and storing into a df
sql_url_crawl.py ==> getting the links to all the libguides and storing into SQLite
