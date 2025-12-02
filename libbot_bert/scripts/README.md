___

**4layer_embedding_space.py**\
creates embedding vector space using a mean pool over the last 4 hidden layers of BERT

___

**embedding_space.py**\
creates embedding vector space using a mean pool over just the last hidden layer

___

**testing_small_embedding_space.py**\
loads dataframe and selects subset of text. Computes embeddings for the subset with two methods (mean_last and las4_mean). Also has a comparison function in it to quickly check the two.

___

**search_testing.py**\
general search script

___


**compared_search_testing.py**\
Uses both embeddings from the last hidden layer, and the last 4 hidden layers.
Compares them with a search function.

___


**bert_testing.py**\
early simple testing of bert with single text chunk

___


**df_url_crawl.py**\
getting the links to all the libguides and storing into a df

___


**sql_url_crawl.py**\
getting the links to all the libguides and storing into SQLite

___
