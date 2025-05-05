# RAG - R translation

library(ollamar)
pull("mxbai-embed-large")

# define model 
model = "mxbai-embed-large"

# define a set of training documments + prompt from user input
documents = corpus
prompt = user_input

# cosine similarity function with two vectors

cosine_similarity <- function(prompt, documents) {
  
  max_similarity = -1
  most_similar = -1
  
  # loop through our training data and calculate vector similarity to target
  for (n in 1:length(embed_list)) {
    # calculate cosign similarity between prompt vector and training vector
    cosine_similarity = sum(embed_list[[n]] * prompt_vector) / (sqrt(sum(embed_list[[n]]^2)) * sqrt(sum(prompt_vector^2)))
    # check if this is more or less similar than last vector and update return values accordingly
    if (cosine_similarity > max_similarity) {
      max_similarity = cosine_similarity
      most_similar = n  
    } 
  }
  
  # return the most similar document fromt the training set
  if (most_similar > -1) {
    print(documents[most_similar])
  } else {
    print('Nothing similar')
  }
}

# Next task: For each text chunk, retrieve the vector space for every word in 
# the document and then average the vectors into a single vector representing 
# the entire text. Save vectors for all texts in a data.frame

