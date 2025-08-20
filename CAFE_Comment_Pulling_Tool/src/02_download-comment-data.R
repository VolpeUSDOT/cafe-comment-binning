# Author: Bentley Clinton (bentley.clinton@dot.gov)

library(rstudioapi)
setwd(dirname(getActiveDocumentContext()$path))

require(httr)
require(jsonlite)
require(dplyr)
require(readr)
require(tidyr)
require(purrr)

source("_scalars.R")

clistFileName <- paste0("01_comment-list_", docketId, "_", indexId, ".csv")
commentTracker <- read_csv(file = paste0("../index/", clistFileName), na = "")
commentTracker <- commentTracker %>%
  select(id, attributes.title, links.self)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#### Flag docs already downloaded

if (lastVersion != "none") {
  clistFileName.last <- paste0("01_comment-list_", docketId, "_", lastVersion, ".csv")
  commentTracker.last <- read_csv(file = paste0("../index/", clistFileName.last), na = "") %>%
    select(id) %>%
    mutate(complete_flag = 1)
  
  commentTracker.new <- commentTracker %>% 
    full_join(commentTracker.last,
              by = "id")
  
  commentTracker.new <- commentTracker.new %>%
    filter(is.na(complete_flag))
  
  print(paste0(commentTracker.new %>% nrow(), " new comments since ", lastVersion))
} else {
  #### To download all
  commentTracker.new <- commentTracker
}
#### 

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
commentlogFileName    <- paste0("00a_comment-log_", docketId, "_", indexId, ".txt")

attachmentData <- tibble()
commentInfo <- tibble()

#iMax <- 2 # For testing
iMax <- nrow(commentTracker.new)

for (i in 1:iMax) {
  #for (i in 670:675) { 
  #i <- 1 #672
  commentId <- commentTracker.new[i, ]$id
  tempAttachments <- tibble(commentId = commentId)
  tempData <- tibble(id = commentId)
  
  tryCatch(
    expr = {
      # Call to API for comment info
      commentResult <- GET(paste0("https://api.regulations.gov/v4/comments/", commentId, "?include=attachments", "&api_key=", apiKey))
      
      # Store results
      if (commentResult$status_code == 200) {
        commentData <- commentResult %>% .$content %>% rawToChar() %>% fromJSON()
      } else {
        commentResult %>% print()
        print(paste("Limit:", commentResult$headers$`x-ratelimit-limit`,
                    "Remaining:", commentResult$headers$`x-ratelimit-remaining`))
        Sys.sleep(5*60)
        commentResult <- GET(paste0("https://api.regulations.gov/v4/comments/", commentId, "?include=attachments", "&api_key=", apiKey))
        print(paste("Status code:", commentResult$status_code,
                    "Limit:", commentResult$headers$`x-ratelimit-limit`,
                    "Remaining:", commentResult$headers$`x-ratelimit-remaining`))
      }
      
      # Manually store comment attributes. Note there are possible instances with 
      #  NULL values, which do not work with a simple data.frame() call.  Must
      #  replace these with NA.
      tempData <- 
        list(statusCode = commentResult$status_code,
             id = commentData$data$id,
             type = commentData$data$type,
             duplicateComments = commentData$data$attributes$duplicateComments,
             docAbstract = commentData$data$attributes$docAbstract,
             comment = commentData$data$attributes$comment,
             documentType = commentData$data$attributes$documentType,
             objectId = commentData$data$attributes$objectId,
             subtype = commentData$data$attributes$subtype,
             title = commentData$data$attributes$title,
             withdrawn = commentData$data$attributes$withdrawn,
             hasAttachment = !is.null(commentData$included))
      
      tempData[sapply(tempData, is.null)] <- NA
      tempData <- tempData %>% rbind.data.frame()
      
      # Extract attachment info if present
      if (tempData$hasAttachment) {
        
        tempAttachments <- tibble()
        
        tempAttachments.data <- commentData$included %>% jsonlite::flatten() 
        
        # fileFormats is a list of data.frame elements (fileURL, format, size).
        #  Must extract these to single row
        for (j in 1:nrow(tempAttachments.data)) {
          
          temp <- data.frame()
          
          tempAttachments.ff <- tempAttachments.data[j,] %>% 
            .$attributes.fileFormats
          
          if (!is.na(tempAttachments.ff)) {
            temp <- tempAttachments.ff %>% 
              do.call(rbind.data.frame, .) %>% 
              mutate(note = "")
          }
          
          if (nrow(temp) == 0) {
            temp <- data.frame(note = "No attachment content")
          }
          
          temp2 <- tempAttachments.data[j,] %>%
            select(-attributes.fileFormats) %>%
            # Convert author list to comma-separated string:
            mutate(attributes.authors = map_chr(attributes.authors, toString)) %>%
            bind_cols(., temp) %>%
            mutate(commentId = commentId, .before = 1)
          
          tempAttachments <- bind_rows(temp2, tempAttachments)
        }
      } else {
        tempAttachments <- tibble(commentId = commentId,
                                  note = "No attachments")
      }
      
  },
  error = function(e) {
    print(paste(paste0("(", i, "/", iMax, ")"), 
                commentId, "error."))
    cat("(", i, "/", iMax, ")", 
        commentId, "complete.", "Remaining:", 
        commentResult$headers$`x-ratelimit-remaining`, 
        "ERROR", "\n", 
        file = paste0("../index/", commentlogFileName), append = TRUE)
  },
  warning = function(w) {
    print(paste(paste0("(", i, "/", iMax, ")"), 
                commentId, "warning."))
    cat("(", i, "/", iMax, ")", 
        commentId, "complete.", "Remaining:", 
        commentResult$headers$`x-ratelimit-remaining`, 
        "WARNING", "\n", 
        file = paste0("../index/", commentlogFileName), append = TRUE)
  },
  finally = {
    attachmentData <- bind_rows(attachmentData, tempAttachments) 
    commentInfo <- bind_rows(commentInfo, tempData)
    
    print(paste(paste0("(", i, "/", iMax, ")"), 
                commentId, "complete.", "Remaining:", 
                commentResult$headers$`x-ratelimit-remaining`))
    
    cat("(", i, "/", iMax, ")", 
        commentId, "complete.", "Remaining:", 
        commentResult$headers$`x-ratelimit-remaining`, 
        "dupe:", tempData$duplicateComments,
        "title:", tempData$title, "\n", 
        file = paste0("../index/", commentlogFileName), append = TRUE)
    
    Sys.sleep(4)
  })
  
}

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Export comment data ####

logFileName    <- paste0("00_log_", docketId, "_", indexId, ".txt")
infoFileName   <- paste0("02a_comment-info_", docketId, "_", indexId, ".csv")
attachFileName <- paste0("02b_attachments_", docketId, "_", indexId, ".csv")

commentInfo %>% 
  write_csv(file = paste0("../index/", infoFileName), na = "")
  
attachmentData %>% 
  write_csv(file = paste0("../index/", attachFileName), na = "")

cat("info and attachments exported:\t", paste(Sys.time()), "\n", 
    file = paste0("../index/", logFileName), append = TRUE)


# OLD BELOW

# Address multiple authors
# attachmentData2 <- attachmentsData %>%
#   mutate(attributes.authors = map_chr(attributes.authors, toString))

# write_rds(attachmentData, file = paste0(pathBase, "file-index/", docketId, "_attachment-files.rds"))
# write_csv(attachmentData, file = paste0(pathBase, "file-index/", docketId, "_attachment-files.csv"), na = "")
# 
# write_rds(commentInfo, file = paste0(pathBase, "file-index/", docketId, "_comment-data.rds"))
# write_csv(commentInfo, file = paste0(pathBase, "file-index/", docketId, "_comment-data.csv"), na = "")

