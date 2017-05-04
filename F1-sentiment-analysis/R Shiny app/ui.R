
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(shinyjs)

shinyUI(fluidPage(
  #This is only needed for hiding driver or team
  #check box group based on the radio button
  useShinyjs(),

  sidebarPanel(
    tags$head(tags$style(type="text/css", "
             #loadmessage {
                         position: fixed;
                         top: 0px;
                         left: 0px;
                         width: 100%;
                         padding: 5px 0px 5px 0px;
                         text-align: center;
                         font-weight: bold;
                         font-size: 100%;
                         color: #FFFFFF;
                         background-color: #009688;
                         z-index: 105;
                         }
                         ")),
    
    conditionalPanel(condition="$('html').hasClass('shiny-busy')",
                     tags$div("Loading...",id="loadmessage")),
    
    radioButtons("radio", label = h3("Drivers or team comparison"),
                 choices = list("Drivers" = "Drivers", "Teams" = "Teams"),
                 selected = "Drivers", inline=TRUE),

    fluidRow(
      column(6, checkboxGroupInput("driverCheckGroup", label = h3("Drivers"),
                                   choices = list("Hamilton" = "@lewishamilton",
                                                  "Bottas" = "@valtteribottas",
                                                  "Ricciardo" = "@danielricciardo",
                                                  "Verstappen" = "@max33verstappen",
                                                  "Perez" = "@schecoperez",
                                                  "Ocon" = "@oconesteban",
                                                  "Massa" = "@massafelipe19",
                                                  "Stroll" = "@lance_stroll",
                                                  "Alonso" = "@alo_oficial",
                                                  "Vandoorne" = "@svandoorne",
                                                  "Kvyat" = "@dany_kvyat",
                                                  "Sainz" = "@carlossainz55",
                                                  "Grosjean" = "@rgrosjean",
                                                  "Magnussen" = "@kevinmagnussen",
                                                  "Hulkenberg" = "@nicohulkenberg",
                                                  "Palmer" = "@jolyonpalmer",
                                                  "Ericsson" = "@ericsson_marcus",
                                                  "Wehrlein" = "@pwehrlein"),
                                   selected = c("@lewishamilton", "@alo_oficial"))),
      column(6, checkboxGroupInput("teamCheckGroup", label = h3("Teams"),
                                   choices = list("Mercedes" = "@mercedesamgf1",
                                                  "Ferrari" = "@scuderiaferrari",
                                                  "Red Bull" = "@redbullracing",
                                                  "Force India" = "@forceindiaf1",
                                                  "Williams" = "@williamsracing",
                                                  "McLaren" = "@mclarenf1",
                                                  "Toro Rosso" = "@tororossospy",
                                                  "Haas" = "@haasf1team",
                                                  "Renault" = "@renaultsportf1",
                                                  "Sauber" = "@sauberf1team"),
                                   selected = c("@mercedesamgf1", "@scuderiaferrari")))
    ),

    sliderInput("smoother", label = h3("Smoothing"), min = 0,
                max = 1, value = 0.4, step=0.05),

    width = 4
  ),

  mainPanel(
    tags$style(type="text/css",
               ".shiny-output-error { visibility: hidden; }",
               ".shiny-output-error:before { visibility: hidden; }"
    ),
    tabsetPanel(
      tabPanel("Sentiment Plot",
               plotOutput("plot"),
               uiOutput("dates"))
    )
  )
))