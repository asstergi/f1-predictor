
# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(shinyjs)
library(ggplot2)
library(ggrepel)

source("utils.R")

drivers_data = loadData('driver')
teams_data = loadData('team')

my_min <- 1
my_max <- 3

# Define server logic for random distribution application
shinyServer(function(input, output, session) {
  observe({
    toggleState("driverCheckGroup", input$radio == "Drivers")
    toggleState("teamCheckGroup", input$radio == "Teams")
  })
  
  #Allows only the selection of certain number of choices
  observe({
    if(length(input$driverCheckGroup) > my_max)
    {
      showNotification(paste0("You can select up to ", my_max, " drivers"), duration = 5, type = "error")
      updateCheckboxGroupInput(session, "driverCheckGroup", selected= head(input$driverCheckGroup, my_max))
    }
    if(length(input$driverCheckGroup) < my_min)
    {
      updateCheckboxGroupInput(session, "driverCheckGroup", selected= "@alo_oficial")
    }
  })
  
  observe({
    if(length(input$teamCheckGroup) > my_max)
    {
      showNotification(paste0("You can select up to ", my_max, " teams"), duration = 5, type = "error")
      updateCheckboxGroupInput(session, "teamCheckGroup", selected= head(input$teamCheckGroup, my_max))
    }
    if(length(input$teamCheckGroup) < my_min)
    {
      updateCheckboxGroupInput(session, "teamCheckGroup", selected= "@scuderiaferrari")
    }
  })
  
  #Check the file every 60 seconds
  pollRaces <- reactivePoll(10*1000, session, 
                           # This function returns the time that the file was last
                           # modified
                           checkFunc = function() {
                             z = gs_ls()
                             z[z$sheet_title=='races',]["updated"]
                           },
                           # This function returns the content of the file
                           valueFunc = function() {
                             read_races()
                           }
  )
  
  # Reactive expression to generate the requested dataset. This is 
  # called whenever the inputs change.
  data_d <- reactive({
    if (input$radio == "Drivers"){
      drivers_data[drivers_data[,2] %in% input$driverCheckGroup & 
                     drivers_data$Date>=input$date_range[1] & 
                     drivers_data$Date<=input$date_range[2],]
    } else {
      teams_data[teams_data[,2] %in% input$teamCheckGroup &
                   teams_data$Date>=input$date_range[1] & 
                   teams_data$Date<=input$date_range[2],]
    }
  })
  
  # Generate a plot of the data
  output$plot <- renderPlot({
    d = data_d()
    races <- pollRaces()
    
    rr = merge(x = data.frame(Date = unique(d$Date)), 
               y = races, 
               by = "Date", 
               all.x = TRUE)
    init_n_rows = nrow(rr)
    
    if (input$radio == "Drivers"){
      rr = rr[rep(seq_len(nrow(rr)), length(input$driverCheckGroup)), ]
      rr[init_n_rows:dim(rr)[1],2] = NA
      plt <- ggplot(d, aes(x=Date, y=Sentiment, group=Driver)) +
        stat_smooth(aes(y = Sentiment, colour=Driver), se=F, span=input$smoother)+
        geom_vline(data = races, aes(xintercept=as.numeric(races$Date)),
                   linetype=4, colour="black") +
        theme(legend.position = "bottom")
      
      if (length(ggplot_build(plt)$data[[1]])==0){
        plt <- ggplot(d, aes(x=Date, y=Sentiment, group=Driver)) +
          geom_line(aes(color=Driver),size=0.5)+
          geom_point(aes(color=Driver))+
          geom_vline(data = races, aes(xintercept=as.numeric(races$Date)),
                     linetype=4, colour="black") +
          theme(legend.position = "bottom")
      }
    } else {
      rr = rr[rep(seq_len(nrow(rr)), length(input$teamCheckGroup)), ]
      rr[init_n_rows:dim(rr)[1],2] = NA
      plt <-ggplot(d, aes(x=Date, y=Sentiment, group=Team)) +
        stat_smooth(aes(y = Sentiment, colour=Team), se=F, span=input$smoother)+
        geom_vline(data = races, aes(xintercept=as.numeric(races$Date)),
                   linetype=4, colour="black") +
        theme(legend.position = "bottom")
      
      if (length(ggplot_build(plt)$data[[1]])==0){
        plt <-ggplot(d, aes(x=Date, y=Sentiment, group=Team)) +
          geom_line(aes(color=Team),size=0.5)+
          geom_point(aes(color=Team))+
          geom_vline(data = races, aes(xintercept=as.numeric(races$Date)),
                     linetype=4, colour="black") +
          theme(legend.position = "bottom")
      }
    }
    #Get the minimum of the y-axis
    min_y = ggplot_build(plt)$layout$panel_ranges[[1]]$y.range[1]
    plt <- plt + 
      geom_label_repel(aes(x = rr$Date, 
                            y = rep(min_y, dim(rr)[1]),
                            label = rr$GP),
                            angle=0, 
                            size=4)
    plt
  })
  
  output$dates <- renderUI({
    d = data_d()
    sliderInput("date_range",
                "Date Range:",
                min = min(drivers_data$Date), max = max(drivers_data$Date),
                value = c(min(d$Date), max(d$Date)),
                width='100%')
  })
})
