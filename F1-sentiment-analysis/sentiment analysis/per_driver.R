library(stringr)
library(dplyr)

connect_files = function(filenames){
  df_tweets <- read_csv(filenames[1], col_names = TRUE) %>%
                dmap_at('text', conv_fun)
  print(dim(df_tweets))
  for (filename in filenames[-c(1)]){
    this_tweets <- read_csv(filename, col_names = TRUE) %>%
                    dmap_at('text', conv_fun)
    df_tweets = rbind(df_tweets, this_tweets)
    print(dim(df_tweets))
  }
  df_tweets
}

to_date <- function(x){
  tryCatch({
    as.Date(tolower(x), format='%a %b %d')
  },
  error=function(cond) {
    return("___")
  })
}

process_tweets = function(df_tweets){
  df_tweets$created_at_date = lapply(df_tweets$created_at, to_date)
  df_tweets$text = lapply(df_tweets$text, tolower)
  df_tweets$created_at_date[is.na(df_tweets$created_at_date)] = "___"
  df_tweets = df_tweets[!c(df_tweets$created_at_date== "___"),]
  df_tweets = data.frame(df_tweets)
  df_tweets
}

produce_df = function(df_tweets, drivers_or_teams, FUN=mean){
  dates = c()
  for (day in unique(df_tweets$created_at_date)){
    dates = c(dates, day)
  }
  dates = sort(dates)
  
  cols = c()
  for (dd in unique(df_tweets$created_at_date)){
    cols = c(cols, as.character(dd))
  }
  print (cols)
  
  df = data.frame(matrix(nrow=length(drivers_or_teams), ncol=length(dates)))
  rownames(df) = drivers_or_teams
  colnames(df) = cols
  
  for (driver_or_team in drivers_or_teams){
    driver_or_team = tolower(driver_or_team)
    this_df_tweets = df_tweets %>%
      filter(str_detect(text, driver_or_team))
    driver_avgs = rep(NA, length(dates))
    names(driver_avgs) = dates
    driver_avgs_init = tapply(this_df_tweets$sentiment, factor(unlist(this_df_tweets$created_at_date)), FUN)
    driver_avgs[names(driver_avgs_init)] = driver_avgs_init
    if (is.logical(driver_avgs)){
      df[driver_or_team,] = rep(NA, length(dates))
    } else {
      df[driver_or_team,] = driver_avgs
    }
  }
  return(df)
}

filenames = c("F1_tweets_W07_2017_sched.csv", 
              "F1_tweets_W08_2017_sched.csv", 
              "F1_tweets_W09_2017_sched.csv", 
              "F1_tweets_W10_2017_sched.csv", 
              "F1_tweets_W11_2017_sched.csv",
              "F1_tweets_W12_2017_sched.csv",
              "F1_tweets_W13_2017_sched.csv",
              "F1_tweets_W14_2017_sched.csv",
              "F1_tweets_W15_2017_sched.csv",
              "F1_tweets_W16_2017_sched.csv",
              "F1_tweets_W17_2017_sched.csv",
              "F1_tweets_W18_2017_sched.csv")

df_tweets = connect_files(filenames)
print(dim(df_tweets))
df_tweets = make_predictions(df_tweets)
df_tweets = process_tweets(df_tweets)

mode <- which.max(table(df_tweets$sentiment))
print (mode)

df_tweets = df_tweets[df_tweets$sentiment<0.7021043 | 
                      df_tweets$sentiment>0.7021044,]

drivers = c("@lewishamilton", "@valtteribottas", 
            "@danielricciardo", "@max33verstappen", 
            "@schecoperez", "@oconesteban", 
            "@massafelipe19", "@lance_stroll", 
            "@alo_oficial", "@svandoorne", 
            "@dany_kvyat", "@Carlossainz55", "@Carlossainz", 
            "@rgrosjean", "@kevinmagnussen", 
            "@nicohulkenberg", "@jolyonpalmer", 
            "@ericsson_marcus", "@pwehrlein")

teams = c("@mercedesamgf1", "@redbullracing", 
          "@scuderiaferrari", "@forceindiaf1", 
          "@williamsracing", "@mclarenf1", 
          "@tororossospy", "@haasf1team", 
          "@renaultsportf1", "@sauberf1team")



drivers_df = produce_df(df_tweets, tolower(drivers), mean)
teams_df = produce_df(df_tweets, tolower(teams), mean)

write.csv(drivers_df, "drivers_df.csv")
write.csv(teams_df, "teams_df.csv")
