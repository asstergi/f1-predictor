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
  #print(unique(df_tweets$created_at_date))
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


qplot(df_tweets$sentiment,
      geom="histogram",
      binwidth = 0.05,  
      main = "Histogram for Sentiment", 
      xlab = "Sentiment",  
      fill=I("blue"),
      col=I("blue"),
      alpha=I(.5))


# summary(HAM$sentiment)
# plot_tweets(HAM, 0.5)
# summary(ALO$sentiment)
# plot_tweets(ALO, 0.2)

#'#f1, #formula1, @lewishamilton, @valtteribottas, @danielricciardo, @max33verstappen, @schecoperez, @oconesteban, @massafelipe19, @lance_stroll, @alo_oficial, @svandoorne, @dany_kvyat, @Carlossainz55, @rgrosjean, @kevinmagnussen, @nicohulkenberg, @jolyonpalmer, @ericsson_marcus, @pwehrlein, @mercedesamgf1, @redbullracing, @scuderiaferrari, @forceindiaf1, @williamsracing, @mclarenf1, @tororossospy, @haasf1team, @renaultsportf1, @sauberf1team'

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

saveData("drivers_df")
saveData("teams_df")

library(googlesheets)
#table <- "drivers_data"

saveData <- function(filename) {
  # Add the data as a new row
  gs_upload(file = paste(filename,".csv",sep = ''), sheet_title = filename)
}

z = gs_ls()
z[z$sheet_title=='teams_df',]["sheet_key"]


loadData <- function(driver_or_team='driver') {
  # Grab the Google Sheet
  if (driver_or_team=='driver'){
    sheet <- gs_key('1u0XMrV0n1UJMTc8QyoRhWgtJ8H216nCyFjp3sm17QRE')
  } else {
    sheet <- gs_key('1MvDrJYKSC3c1AKpWsjWVhEdNcoRVnFohVYm9sB-1E8g')
  }
  
  # Read the data
  data <- gs_read_csv(sheet, col_names=T)
  data.frame(data)
}

removeFirst <- function(x) {
  substr(x,2,nchar(x))
}
toDate <- function(x) {
  as.Date(substr(x,2,nchar(x)), format = '%m.%d.%Y')
  #as.POSIXct(as.Date(x, origin="1970-01-01"))
}

zz <- function(x) {
  as.Date(x, origin="1970-01-01")
}

data = loadData('team')
colnames(data)
newCols = sapply(colnames(data), toDate)
newCols[1] <- "Drivers"
colnames(data) <- newCols

as.Date(17275, origin="1970-01-01")

# first remember the names
n <- data$X1
data <- as.data.frame(t(data[,-1]))
colnames(data) <- n
#row.names(data) <- sapply(row.names(data), toDate)
# data$Date = row.names(data)
# data$Date2 = sapply(data$Date, removeFirst)
# data$Date3 = as.Date(data$Date2, format = '%m.%d.%Y')
data$Date = as.Date(sapply(row.names(data), removeFirst), format = '%m.%d.%Y')
head(data)


ggplot(data, aes( Date,data$lewis)) 
    + geom_line(col='red')  
    + geom_line(mapping = aes(y=data$bottas, col=4))

races <- read.csv("races.csv")
races$Date = as.Date(races$Date, format = '%d/%m/%Y')

melted_data <- melt(data[,c(9,10,20)], id=c("Date")) #Drivers
names(melted_data) <- c("Date", "Driver", "Sentiment")

melted_data <- melt(data[,c(1,6,11)], id=c("Date")) #Teams
names(melted_data) <- c("Date", "Driver", "Sentiment")

library(ggplot2)
z = ggplot(melted_data, aes(x=Date, y=Sentiment, group=Driver)) +
  #geom_line(aes(color=Driver),size=0.5)+
  stat_smooth(aes(y = Sentiment, colour=Driver), se=F, span=0.2)+
  #stat_smooth(aes(y = Sentiment, colour='Drivers'), se=F, span=0.1)+
  #geom_point(aes(color=Driver))+
  geom_vline(data = races, aes(xintercept=as.numeric(races$Date)),
             linetype=4, colour="black") 
  #coord_cartesian(ylim = c(0, 1)) + 
  geom_text(aes(x = rep(rr$Date,2), y = rep(0.2, 156),
                              label = rep(rr$GP,2)),
             angle=0, size=2)
plot(z)

ggplot_build(z)$layout$panel_ranges[[1]]$y.range

for (r in 1:dim(races)[1]){
  z = z + geom_label(aes(x = races$Date[r], 
                        y = 0,
                        label = races$GP[r],
                        angle = 45))
}

plot(z)
  geom_label(data = races, aes(x = as.numeric(races$Date)[1], y = 0,
                label = races$GP[1]))
  # geom_label(aes(x = races$Date[2], y = 0,
  #                label = races$GP[2]))+
  # geom_label(aes(x = races$Date[3], y = 0,
  #                label = races$GP[3]))
