import re

def keywordClassify(keywordDict, chunk_list):
    '''
    keywordDict: A dictionary where the keys are the categories for categorization,
    and the values are lists of key words associated with that classification

    returns:
        A list of dicts of keyword classification matches. If keywords for multiple categories are found in one chunk,
        they will be ordered where the category with the most keyword occurrences is first, and least is last
    '''

    chunkCategorization = []
    for chunk in chunk_list:
        keywordInstances = dict.fromkeys(keywordDict.keys(), 0)
        for category in keywordDict:
            for keyword in keywordDict[category]:
                instances = re.findall(keyword, chunk, re.IGNORECASE) # May need to modify the regex to avoid words within words
                keywordInstances[category] += len(instances)
        # Sort dictionary by value, remove keys with val of zero, and append to list
        # NOTE: "ordered" dictionaries were added in python 3.6
        chunkCategorization.append({k: v for k, v in sorted(keywordInstances.items(), key=lambda item: item[1], reverse=True) if v > 0})
    return chunkCategorization

if __name__ == "__main__":
    keywordDict = {
        'Hot': ['hot', 'warm', 'toasty'],
        'Cold': ['cold', 'cool', 'chilly']
    }

    chunk_list = ['This string has nothing', 'This string is cool', 'Blah blah warm toasty hot', 'chilly warm cool']

    chunk_categories = keywordClassify(keywordDict, chunk_list)
    print(chunk_categories)
