import sys
import os
import html
import json
import requests
import pandas as pd
import time

from datetime import datetime

# NOTE: Ensure below user values and run options are set to desired values before running.

# region /------ User Values ------/

# Set personal API key with which to make requests. One can be obtained at https://open.gsa.gov/api/regulationsgov
api_key = "mb9QFdMuWnHBebkYicehel4pq6vuld2112wIi5CD"

# Set target docket using ID, visible in "Document Details" -> "Agency/Docket Number"
# A new folder is created for each docket ID to prevent data loss between multiple runs.
docket_id = "NHTSA-2025-0491"

# The directory in which all outputs will be saved. If changing location between runs ensure previous work is transfered.
BASE_DIR = "C://Users//Vincent.Livant//Desktop//CommentBinning//test/"

# The name of the file used to save pulled comment info. 
# This file is used to determine the last comments pulled and resume progress.
# The file must be in the ".csv" format.
LOG_FILE = BASE_DIR + docket_id + "/log" + ".csv"

# regulations.gov checks for and blocks requests for attachments from "bots." This value should work, but
# if getting 403 errors when requesting attachments find your browser user-agent by opening the console in your browser 
# development tools and typing "navigator.userAgent."
user_agent = {
       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
    }

# endregion /-------------------------/

# region /------ Run Options ------/

# When the API key's hourly request limit is reached,
#   If True: the script will wait for one hour while continuing to run, then resume.
#   If False: the script will be terminated and must be restarted by the user to resume.
wait_for_rate_limit = True

# If True: after docket comments are pulled docket documents will be checked for comments.
# If False: docket documents will be ignored.
pull_document_comments = False

# endregion /-----------------------/

# region /------ Constants ------/

get_docket_comments_base_string = "https://api.regulations.gov/v4/comments?sort=lastModifiedDate&filter[docketId]={}&include=attachments&page[size]=250&page[number]={}&api_key={}"
get_docket_comments_lastModified_string = "https://api.regulations.gov/v4/comments?sort=lastModifiedDate&filter[lastModifiedDate][ge]={}&filter[docketId]={}&include=attachments&page[size]=250&page[number]={}&api_key={}"
get_docs_base_string = "https://api.regulations.gov/v4/documents?sort=lastModifiedDate&filter[docketId]={}&api_key={}"
get_document_comments_base_string = "https://api.regulations.gov/v4/comments?sort=lastModifiedDate&filter[commentOnId]={}&include=attachments&page[size]=250&page[number]={}&api_key={}"


headers = ["entryType", "modifyDate", "docketId", "commentOnDocumentId", "id", "organization", "firstName", "lastName", "title", "comment", "attachments", "url"]


# endregion /------------------------/


#region Docket-Level Methods

def get_docket_documents(docket_id):
    '''
    docket_id: The docket for which to pull documents.

    returns: a list of document IDs and their URL links for all documents associated with the given docket ID.
    '''    
    print("Checking docket documents...")

    # Grab all docs associated with docket
    request_str = get_docs_base_string.format(docket_id, api_key)
    response = json.loads(requests.get(request_str).text)

    if ("error" in response) and (response["error"]["code"] == "OVER_RATE_LIMIT"):
        delay_for_rate_limit()
        response = json.loads(requests.get(request_str).text)

    data = response["data"]
    ids = []
    links = []

    for doc in range(len(data)):
        ids.append(data[doc]["attributes"]["objectId"])
        links.append(data[doc]["links"]["self"])

    return ids, links

def get_docket_comments(docket_id, log, last_dateModified):
    '''
    docket_id: The docket for which to pull comments.
    log: The data frame associated with the log file specified in User Values.
    last_dateModified: The date modified of the last pulled entry. Comments will be pulled for entries later than or
                       equal to this given time. If value is None all comments will be pulled.

    returns: a list of comment IDs and their URL links for all comments associated with the given docket ID.
    '''    
    comment_ids = []
    comment_urls = []

    # Grab all comments associated with docket
    if last_dateModified:
        print(f"Checking for new comments since last set of requests on {last_dateModified}...\n")
        request_str = get_docket_comments_lastModified_string.format(last_dateModified, docket_id, '1', api_key)
    else:
        print("Checking for all comments...\n")
        request_str = get_docket_comments_base_string.format(docket_id, '1', api_key)

    response = json.loads(requests.get(request_str).text)
    
    if ("error" in response) and (response["error"]["code"] == "OVER_RATE_LIMIT"):
        delay_for_rate_limit()
        response = json.loads(requests.get(request_str).text)
    
    num_pages = response["meta"]["totalPages"]

    append_docket_request_comments(response, comment_ids, comment_urls, log)
    
    for page_num in range(2, num_pages):
        request_str = get_docket_comments_base_string.format(docket_id, page_num, api_key)
        response = json.loads(requests.get(request_str).text)

        append_docket_request_comments(response, comment_ids, comment_urls)
       
    print(f"{len(comment_ids)} new comments found!\n")

    return comment_ids, comment_urls

def append_docket_request_comments(response, comment_ids, comment_urls, log):
    '''
    response: The value returned from an API request for comments associated with a docket.
    comment_ids: The list of comment IDs for which to append new comments, used for the download queue.
    comment_urls: The list of comment URLs for which to append new comments, used for the download queue.
    log: The data frame associated with the log file specified in User Values.

    Appends all comment IDs and URLs not previously logged to queue list.
    '''
    data = response["data"]
    for comment in data:
        if comment["id"] not in log['id']:
            comment_ids.append(comment["id"])
            comment_urls.append(comment["links"]["self"])
    return

#endregion

#region Document-Level Methods

def get_all_documents_comments(document_ids, log, last_dateModified):
    '''
    document_ids: A list of document IDs for which to pull comments.
    log: The data frame associated with the log file specified in User Values.
    last_dateModified: The date modified of the last pulled entry. Comments will be pulled for entries later than or
                       equal to this given time. If value is None all comments will be pulled.

    returns: a list of comment IDs and their URL links for all comments associated with the given document IDs.
    '''   
    document_comment_ids = []
    document_comment_urls = []

    for i in range(1, len(document_ids)):
        ids, urls = get_document_comments(document_ids[i], log, last_dateModified)
        document_comment_ids.extend(ids)
        document_comment_urls.extend(urls)
    
    return document_comment_ids, document_comment_urls

def get_document_comments(document_id, log, last_dateModified):
    '''
    document_id: The document ID for which to pull comments.
    log: The data frame associated with the log file specified in User Values.
    last_dateModified: The date modified of the last pulled entry. Comments will be pulled for entries later than or
                       equal to this given time. If value is None all comments will be pulled.

    returns: a list of comment IDs and their URL links for the given document and adds them to the queue.
    '''   
    comment_ids = []
    comment_urls = []

    if last_dateModified:
        print(f"Checking for new comments on {document_id} since {last_dateModified}...\n")
        request_str = get_docket_comments_lastModified_string.format(last_dateModified, docket_id, '1', api_key)
    else:
        print(f"Checking for all comments on {document_id}...\n")
        request_str = get_docket_comments_base_string.format(docket_id, '1', api_key)

    # First request gets page count
    request_str = get_document_comments_base_string.format(document_id, 1, api_key)
    response = json.loads(requests.get(request_str).text)

    if ("error" in response) and (response["error"]["code"] == "OVER_RATE_LIMIT"):
        delay_for_rate_limit()
        response = json.loads(requests.get(request_str).text)

    append_document_request_comments(response, comment_ids, comment_urls, log)

    num_pages = response["meta"]["totalPages"]
    for page in range(2, num_pages):
        request_str = get_document_comments_base_string.format(document_id, page, api_key)
        response = json.loads(requests.get(request_str).text)
        append_document_request_comments(response, comment_ids, comment_urls, log)

    print(f"{len(comment_ids)} new comments found!\n")

    return comment_ids, comment_urls

def append_document_request_comments(response, comment_ids, comment_urls, log):
    '''
    response: The value returned from an API request for comments associated with a document.
    comment_ids: The list of comment IDs for which to append new comments, used for the download queue.
    comment_urls: The list of comment URLs for which to append new comments, used for the download queue.
    log: The data frame associated with the log file specified in User Values.

    Description: Appends all comment IDs and URLs not previously logged to download queue.
    '''
    if len(response["data"]) == 0:
        return 
    for comment in response["data"]:
        if comment["id"] not in log['id']:
            comment_ids.append(comment["id"])
            comment_urls.append(comment["links"]["self"])
    return

#endregion

#region Content-Level Methods

def get_all_details(item_ids, urls, dir_path, log, are_comments):
    '''
    item_ids: A list of item IDs for which to download all attachments and comment text of, then log.
    urls: The URLs associated with each item_id, used to make API requests.
    dir_path: The path in which to save all downloaded content.
    log: The data frame associated with the log file specified in User Values.
    are_comments: Whether or not the items being processed are comments.

    returns: The given log file, updated with each successfully processed item.

    Description: Acquires and saves the details, attachments and entry comment text for each of the given item IDs and 
    URLs to the given directory. Each entry is logged after successful parsing.
    '''
    progress_substring = "comments" if are_comments else "documents"
    for i in range(len(item_ids)):
        details = get_details(item_ids[i], urls[i], dir_path, are_comments)
        log = pd.concat([log, details])
        save_work(log)
        if i%10 == 0:
            print(f"{len(item_ids) - i} {progress_substring} remaining.")

    return log

def get_details(item_id, url, dir_path, is_comment):
    '''
    item_id: The item ID for which to download all attachments and comment text of, then log.
    urls: The URL associated with the given item_id, used to make API requests.
    dir_path: The path in which to save all downloaded content.
    log: The data frame associated with the log file specified in User Values.
    is_comments: Whether or not the item being processed is a comment.

    Description: Acquires and logs all details for the given entry and associated URL, downloading all attachments and 
    saving comment text to a new folder, named after he item ID, in the given directory.
    '''
    request_str = url + "?api_key=" + api_key
    response = json.loads(requests.get(request_str).text)

    if ("error" in response) and (response["error"]["code"] == "OVER_RATE_LIMIT"):
        delay_for_rate_limit()
        response = json.loads(requests.get(request_str).text)

    entry_dir = create_dir_for_entry(item_id)

    attributes = response["data"]["attributes"]
    df = pd.DataFrame(columns = headers)

    df.at[0, 'entryType'] = 'comment' if is_comment else 'document'
    df.at[0, 'id'] = item_id
    date_modified_str = attributes['modifyDate'].replace('T', ' ').replace('Z', '')
    df.at[0, 'modifyDate'] = datetime.strptime(date_modified_str, "%Y-%m-%d %H:%M:%S")
    df.at[0, 'docketId'] = attributes["docketId"]
    df.at[0, 'organization'] = attributes["organization"]
    df.at[0, 'firstName'] = attributes["firstName"]
    df.at[0, 'lastName'] = attributes["lastName"]
    df.at[0, 'title'] = attributes["title"]
    df.at[0, 'url'] = url
    df.at[0, 'commentOnDocumentId'] = attributes["commentOnDocumentId"] if is_comment else None

    if is_comment:
        comment = html.unescape(attributes["comment"])
        df.at[0, 'comment'] = comment
        if comment:
            file_path = entry_dir + attributes["title"] + ".txt"
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(comment)

    attachments = download_attachments(url, entry_dir)

    df.at[0, 'attachments'] = attachments
    
    # Delete directory if empty
    if len(os.listdir(entry_dir)) == 0:
        os.remove(entry_dir)

    return df

def download_attachments(entry_url, dir_path):
    '''
    entry_url: The URL associated with a comment, for which to download all attachments.
    dir_path: The directory in which to saved the attachments.

    Description: Saves all attachments associated with the given URL in the specified directory.
    '''
    attachments = []
    request_str = entry_url + "/attachments?api_key=" + api_key
    response = json.loads(requests.get(request_str).text)

    if ("error" in response) and (response["error"]["code"] == "OVER_RATE_LIMIT"):
        delay_for_rate_limit()
        response = json.loads(requests.get(request_str).text)

    data = response["data"]
    for attachment in data:
        attributes = attachment["attributes"]
        # Need to check if each attachment is restricted, otherwise could get 403 and crash
        if attributes["restrictReasonType"] == None:
            url = attributes["fileFormats"][0]["fileUrl"]
            file_name = os.path.basename(url)
            attachments.append((file_name, url))

    # attachment_dir = dir_path + "/attachments"
    for attachment in attachments:
        save_attachment(attachment, dir_path)

    return attachments

def save_attachment(attachment, dir_path):
    '''
    attachment: A tuple containing the file name and URL for an attachment to be saved.
    dir_path: The directory path in which to save the attachment.

    Description: Makes an API request for the given attachment information and saves it to the specified directory.
    '''
    file_name, url = attachment
    url_req = url + "?api_key=" + api_key

    response = requests.get(url_req, headers=user_agent, stream=True)

    with open(dir_path + file_name, 'wb') as file:
        file.write(response.content)
    return

#endregion

#region Helpers

def save_work(log):
    '''
    log: The data frame associated with the log file specified in User Values.

    Description: Saves processed entries to the log file using the given data frame.
    '''
    file_path = LOG_FILE
    log.to_csv(file_path, index=False)

def get_progress_data():
    '''
    Returns progress data saved in the log file if it exists in the form of a data frame, otherwise returns None.

    Remark: The returned data frame is later used to make API requests filtered such that only comments and documents 
    last modified after the last logged entry are processed.
    '''
    file_path = LOG_FILE
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return None

def delay_for_rate_limit():
    '''
    If runtime setting "wait_for_rate_limit" is set to:
        True: delays comment pulling for one hour when API request limit is reset.
        False: terminates comment pulling and exits gracefully.
    '''
    if wait_for_rate_limit:
        print("[" + str(datetime.datetime.now()) + "] Hourly API request limit reached. Progress will resume in ~1 hour...")
        time.sleep(3660)
        print("["  + str(datetime.datetime.now()) + "] Progress resuming...")
        return
    else:
        print("[" + str(datetime.datetime.now()) + "] Hourly API request limit reached. Progress is saved.  Exiting...")
        exit()

def create_dir_for_entry(entry_id):
    '''
    Creates a new directory for a given entry ID if it doesn't already exist.
    '''
    dir_path = BASE_DIR + docket_id + '/' + entry_id + '/'

    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    return dir_path

def get_unique_file_name_from_url(url, dir_path):
    '''
    Returns the file name embedded in the given url, applying numbered suffixes if the name already exists in the given 
    directory.
    '''
    suffix = 0

    file_name= os.path.basename(url)
    file_path = dir_path + file_name
    while os.path.exists(file_path):
        file_path = dir_path + file_name + f'({suffix})'
        suffix += 1
    return file_path

def get_most_recent_modified(log):
    if log.size < 1:
        return None
    return log['modifyDate'].max()

#endregion

if __name__ == "__main__":
    docket_dir = BASE_DIR + docket_id

    # Load data-frame from previous runs if exits, or create a new one.
    # Then pass it to details-getters and check last date-modified and adjust requests accordingly
    log = get_progress_data() if os.path.exists(LOG_FILE) else pd.DataFrame(columns = headers)
    last_dateModified = get_most_recent_modified(log)
    
    print(f"{log.shape[0]} previous entries pulled. Checking for new comments...")

    # Setup directory
    if not os.path.isdir(docket_dir):
        os.mkdir(docket_dir)

    # Pull comments
    comment_ids, comment_urls = get_docket_comments(docket_id, log, last_dateModified)
    log = get_all_details(comment_ids, comment_urls, docket_dir, log, True)
    
    # Setup directory and pull documents if setting is set to True
    if pull_document_comments:
        docket_document_dir = docket_dir + "/documents/"
        if not os.path.isdir(docket_document_dir):
            os.mkdir(docket_document_dir)

        document_ids, document_urls = get_docket_documents(docket_id)
        document_comment_ids, document_comment_urls = get_all_documents_comments(document_ids, log, last_dateModified)

        print(f"A total of {len(document_comment_ids)} new comments on documents found!")

        log = get_all_details(document_comment_ids, document_comment_urls, docket_document_dir, log, False)
    
    print("\nWork completed!")