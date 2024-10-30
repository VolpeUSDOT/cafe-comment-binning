# Author: Bentley Clinton (bentley.clinton@dot.gov)

library(rstudioapi)
setwd(dirname(getActiveDocumentContext()$path))

## Aside: there's something going on here with a few docs that appeared prior to the docket open date.
#  See those that appear at the beginning of the following file.  That said, this also includes some for "EPA-HQ-OAR-2022-0829-0452"??
#  "https://api.regulations.gov/v4/comments?filter[searchTerm]=EPA-HQ-OAR-2022-0985&sort=lastModifiedDate,documentId&api_key=DEMO_KEY"

require(httr)
require(jsonlite)
require(dplyr)
require(readr)

source("_scalars.R")

apiBase.d <- "https://api.regulations.gov/v4/documents?"
apiBase.c <- "https://api.regulations.gov/v4/comments?"

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Identify run number (and create file index directory if none exists)
#dir.create(file.path(pathWd, "file_index"), showWarnings = FALSE)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Extract summary info from api

temp <- list()
i <- 1
nextFlag <- TRUE
while (nextFlag) {
  docketCall <- paste0(apiBase.d, "filter[docketId]=", docketId, 
                       "&page[size]=250", 
                       "&page[number]=", i, 
                       "&api_key=", apiKey)
  docketResult <- GET(docketCall)
  
  if (docketResult$status_code == 200) {
    # Extract content and data (Status code 200 = success)
    docketContent <- docketResult$content %>% rawToChar() %>% fromJSON()
    docketDataTemp <- docketContent$data %>% jsonlite::flatten() %>% as_tibble()
    
    temp[[i]] <- docketDataTemp
    
    # Get number of results on that page
    pageRows <- nrow(temp[[i]])
    
    # If page has fewer than 250 records (specified "&page[size]=250" above), then end
    if (pageRows < 250) {
      next_flag <- FALSE
    }
    
    i <- i + 1

  } else {
    error_code <- docket_result$status_code
    cat(paste("Exited with code", error_code, "\n"))
    nextFlag <- FALSE
  }
 
}

docketData <- bind_rows(temp)

docketData %>% filter(attributes.openForComment == TRUE) %>% print.AsIs()
## Note: it looks like there are 3 documents with comments open
## NHTSA-2023-0022-0004 	
## NHTSA-2023-0022-1509
## NHTSA-2023-0022-1510

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Objective: extract comments from proposed rule.  
#  So, search column labeled "attributes.documentType" and confirm "proposed rule" 
#  is one of the options.
extractDocType <- "Proposed Rule"

# Count total comments ####

# Identify specified document type and those with comment periods
documentsWithComments <- docketData %>%
  filter(attributes.documentType == extractDocType ,
         !is.na(attributes.commentStartDate)
         )

documentsWithComments %>%
  select(id, attributes.objectId, attributes.title) %>%
  print()

# Placeholder in case need to loop through multiple documents
for (docId in documentsWithComments$attributes.objectId) {
  print(docId)
}

# Identify comment id (for now, manually work through the next few rows to see if it captures all comments)
dd <- 3
docId <- documentsWithComments$attributes.objectId[dd]
documentsWithComments$id

# Identify total comment counts (necessary to cycle through comment extract)
# Must cycle page-by-page for extract (see: https://open.gsa.gov/api/regulationsgov/)
# Specifically the heading under "Retrieve all comments for a docket where number of comments is less than 5000"
documentCall <- paste0(apiBase.c, "filter[commentOnId]=", docId, "&api_key=", apiKey)

documentCall <- paste0(apiBase.c, "filter[docketId]=", docketId, "&api_key=", apiKey)

documentResult <- GET(documentCall)

if (documentResult$status_code == 200) {
  documentContent <- documentResult$content %>% rawToChar() %>% fromJSON()
} else {
  documentResult %>% print()
}

totalComments <- documentContent$meta$totalElements
totalComments

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Collect comment info ####

# Note: max within "iteration" is 5000 documents
iterationCount <- 1
commentsAll <- data.frame()
flagEnd <- FALSE # Figure out a better way to do this (for the "while" loop)

while (nrow(commentsAll) < totalComments) {
  
  i <- 1 # Reset page number
  
  # Cycle through pages until page identified as "last page" in API
  while (!flagEnd) {
    
    # For first iteration, pull documents from the beginning
    # For subsequent iterations, pull documents after last date of prior iteration
    if(iterationCount == 1) {
      tempCall <- paste0(apiBase.c, "filter[docketId]=", docketId, "&page[size]=250", "&page[number]=", i, "&sort=lastModifiedDate,documentId&api_key=", apiKey) %>% 
        URLencode()
    } else {
      tempCall <- paste0(apiBase.c, "filter[docketId]=", docketId, "&filter[lastModifiedDate][ge]=", tempLastDate, "&page[size]=250&page[number]=", i, "&sort=lastModifiedDate,documentId&api_key=", apiKey) %>% 
        URLencode()
    }
    
    tempResult <- GET(tempCall)
    
    print(paste("Iteration:", iterationCount, "Page:", i, "Code:", tempResult$status_code))
    
    if (tempResult$status_code == 200) {
      tempContent <- tempResult$content %>% rawToChar() %>% fromJSON()
      tempData <- tempContent$data %>% jsonlite::flatten()
      
      # Append to full comment list
      commentsAll <- bind_rows(commentsAll, tempData)
      
      # Identify if this is the last comment page
      flagEnd <- tempContent$meta$lastPage
    } else {
      tempResult %>% print()
    }
    
    print(paste("Page", i, "complete."))
    i <- i + 1 # Increment page number
    
  }
  
  # If last page, identify the date of last comment on this page
  flagEnd <- FALSE
  tempLast <- tempData %>% tail(n = 1)
  tempLastDate0 <- tempLast$attributes.lastModifiedDate
  
  # Covert last date to eastern time
  tempLastDate1 <- tempLastDate0 %>% 
    strptime(format = "%Y-%m-%dT%H:%M:%SZ", tz = "GMT") %>%
    as.POSIXct()
  attr(tempLastDate1, "tzone") <- "America/New_York"
  tempLastDate <- tempLastDate1 %>% 
    strftime()
  
  print(paste("Last comment date:", tempLastDate))
  
  iterationCount <- iterationCount + 1 # Increment iteration counter
  
  print(paste("Beginning iteration", iterationCount, "from comment date above."))
  
}

# For example: 477 comments listed under "browse comments" on regulations.gov
## https://www.regulations.gov/document/EPA-HQ-OAR-2021-0208-0116
## Note that the sidebar says "Comments Received" equal 161,047 as of 9/30/2021

# Convert to tibble
commentsAll <- commentsAll %>% as_tibble()

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Export comment data ####
csvFileName <- paste0("01_comment-list_", docketId, "_", indexId, ".csv")
logFileName <- paste0("00_log_", docketId, "_", indexId, ".txt")

commentsAll %>% 
  write_csv(file = paste0("../index/", csvFileName), na = "")

# Update log with progress
cat("comment-list exported:\t\t", paste(Sys.time()), "\n", 
    file = paste0("../index/", logFileName), append = TRUE)

# OLD BELOW
# commentTracker <- commentsAll %>%
#   select(id, attributes.title, links.self) %>%
#   mutate(statusCode = NA)
# 
# write_rds(commentTracker, file = paste0(pathBase, "file-index/", docketId, "_comment-tracker.rds"))

