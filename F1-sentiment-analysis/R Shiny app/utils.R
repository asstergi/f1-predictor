library(googlesheets)
library(reshape2)
library(Hmisc)

loadData <- function(driver_or_team='driver') {
  # Grab the Google Sheet
  if (driver_or_team=='driver'){
    sheet <- gs_key('key-to-drivers-data-file')
  } else {
    sheet <- gs_key('key-to-teams-data-file')
  }
  
  # Read the data
  data <- gs_read_csv(sheet, col_names=T)
  data <- data.frame(data)
  
  # Make data transformations
  n <- data$X1
  data <- as.data.frame(t(data[,-1]))
  colnames(data) <- n
  data$Date = as.Date(sapply(row.names(data), removeFirst), format = '%m.%d.%Y')
  melted_data <- melt(data, id=c("Date"))
  names(melted_data) <- c("Date", capitalize(driver_or_team), "Sentiment")
  melted_data
}

removeFirst <- function(x) {
  substr(x,2,nchar(x))
}

read_races <- function() {
  sheet <- gs_key('key-to-races-file')
  # Read the data
  data <- gs_read_csv(sheet, col_names=T)
  data <- data.frame(data)
  data$Date = as.Date(data$Date, format = '%d/%m/%Y')
  data
}