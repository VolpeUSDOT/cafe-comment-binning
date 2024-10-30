# Author: Bentley Clinton (bentley.clinton@dot.gov)

library(rstudioapi)
setwd(dirname(getActiveDocumentContext()$path))

require(tools)
require(dplyr)
require(readr)
require(tidyr)
require(purrr)

source("_scalars.R")

attachFileName <- paste0("02b_attachments_", docketId, "_", indexId, ".csv")

# attachmentsAll %>% 
#   write_csv(file = file.path(pathBase, "file-index", attachFileName), na = "")

attachmentData <- read_csv(file = paste0("../index/", attachFileName), na = "")

if (is.null(attachmentData$id)) {
  fileList <- attachmentData
  print("No attachments")
} else {
  sleepInterval <- 5
  
  fileList <- attachmentData %>%
    select(commentId, note, id, fileUrl) %>%
    mutate(status = NA)
  
  print(paste(fileList %>% filter(!is.na(fileUrl)) %>% nrow(), "files to download"))
  
  iMax <- nrow(fileList)
  #iMax <- 2
  
  for (i in 1:iMax) {
    # i <- 1
    selectedUrl <- fileList$fileUrl[i]
    
    if (!is.na(selectedUrl)) {
      
      # Construct filename (concatenate id and attachment number)
      fileName <- substr(selectedUrl, 
                         nchar("https://downloads.regulations.gov/")+1, 
                         nchar(selectedUrl)) %>%
        gsub("/", "_", .)
      
      localFile.orig <- paste0("../attachments/", fileName)
      
      # Added skip name for some files to skip in automated search
      localFile.skip <- paste0("../attachments/", paste0(file_path_sans_ext(fileName), file_ext(fileName), ".skip")) 
      #localFile <- paste0(pathBase, "comment-docs/", fileName)
      
      if (file.exists(localFile.orig) | file.exists(localFile.skip)) {
        print(paste(paste0("(",i, "/", iMax, ")"), "File", file_path_sans_ext(fileName), "already exists."))
        fileList <- fileList %>%
          mutate(status = ifelse(
            fileUrl == selectedUrl,
            "Already exists.",
            status
          ))
      } else {
        download.file(selectedUrl, destfile = localFile.orig, mode = "wb")
        print(paste(paste0("(",i, "/", iMax, ")"), "Downloaded: ", fileName))
        fileList <- fileList %>%
          mutate(status = ifelse(
            fileUrl == selectedUrl,
            "Downloaded.",
            status
          ))
        Sys.sleep(sleepInterval)
      }
    } else {
      print(paste(paste0("(",i, "/", iMax, ")"), "No url"))
    }
  }
}  

statusFileName <- paste0("03_download-status_", docketId, "_", indexId, ".csv")

fileList %>%
  write_csv(file = paste0("../index/", statusFileName), na = "")

logFileName    <- paste0("00_log_", docketId, "_", indexId, ".txt")

cat("attachment download last run:\t", paste(Sys.time()), "\n", 
    file = paste0("../index/", logFileName), append = TRUE)

