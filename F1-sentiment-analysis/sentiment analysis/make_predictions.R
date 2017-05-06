make_predictions = function(df_tweets){
  
  # preprocessing and tokenization
  it_tweets <- itoken(df_tweets$text,
                      preprocessor = prep_fun,
                      tokenizer = tok_fun,
                      #ids = df_tweets$id,
                      progressbar = TRUE)
  
  # creating vocabulary and document-term matrix
  dtm_tweets <- create_dtm(it_tweets, vectorizer)
  
  # transforming data with tf-idf
  dtm_tweets_tfidf <- fit_transform(dtm_tweets, tfidf)
  
  # loading classification model
  glmnet_classifier <- readRDS('glmnet_classifier.RDS')
  
  # predict probabilities of positiveness
  preds_tweets <- predict(glmnet_classifier, dtm_tweets_tfidf, type = 'response')[ ,1]
  
  # adding rates to initial dataset
  df_tweets$sentiment <- preds_tweets 
  df_tweets
}