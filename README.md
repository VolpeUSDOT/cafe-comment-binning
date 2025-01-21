# README Outline

* Project Description
* Prerequisites
* Usage
  * Building
  * Testing
  * Execution
* Additional Notes
* Version History and Retention
* License
* Contributions
* Contact Information
* Acknowledgements

## Project Description

### ROADII Use Case - Categorizing Public Comments

* **Title:** Categorizing Public Comments for CAFE Rulemakings
* **Purpose and goals of the project:** Explore diferent AI approaches to comment categorization to gain an understanding of language processing tools and to improve the efficiency of the public comment response project. This is not intended to remove humans from the public comment response process, it is only intended to speed up the time in which comments are responded to.
* **Purpose of the source code and how it relates to the overall goals of the project:** This code represents a prototype implementation of processing public comments from plain text to binned and categorized comments. This is not a final version and does not represent the current method of processing public comments.
* **Length of the project:** This use case is currently in the exploratory phase.

## Prerequisites

This repositories dependencies are listed in the requirements.txt file. Install all dependencies by running:
```pip install -r /path/to/requirements.txt```

## LLM Approach

***

The team utilized LM Studio as with the local server and API approach to attempt to improve upon the traditional machine learning approaches to text recognition and categorization. The files for this approach can be found within the this [folder](https://github.com/ROADII-Lab/CAFE-public-comments/tree/LM_Studio/LM_Studio). Most of the code for this approach is located in this [file](https://github.com/ROADII-Lab/CAFE-public-comments/blob/LM_Studio/LM_Studio/tryingLM_Studio.py). This file just needs to be run and it will currently read an Excel sheet for comments in a particular column. It will then label those comments based on one of the labels of {legal, compliance, economics, technology, or other/unknown}. An example of the code that can be modified to run the program with various parameters is shown below.

![alt text](https://github.com/ROADII-Lab/CAFE-public-comments/blob/main/Images/Screenshot%202025-01-10%20102216.png)

### Running LM Studio

1. Click on developer tab.

![alt_text](https://github.com/ROADII-Lab/CAFE-public-comments/blob/main/Images/Dev_ss.png)

***

2. Make sure model is loaded and click Start Server (ctrl + R) button.

![alt_text](https://github.com/ROADII-Lab/CAFE-public-comments/blob/main/Images/Screenshot%202025-01-10%20103235.png)

***

3. As long as the model you identify in the code is downloaded, LM Studio will find the model and load it, if it's not already loaded. For example, it will use the Calme Legal model when instructed and switch to the Gemma model, when instructed, as shown below.

![alt_text](https://github.com/ROADII-Lab/CAFE-public-comments/blob/main/Images/code%20snippet%202.png)

***

### Models Tested

1. gemma-2-27b-it
2. Calme 2.3 LegalKit 8B
3. llama-3.2-1b-instruct-q8_0.gguf
4. llava-hf/llava-1.5-7b-hf
5. simmo/legal-llama-3
6. meta-llama/Llama-3.2-1B
7. Granite 3.1

Parameters varied between 1 and 27 billion for the models that were used.

### Process

The LLM approach utilized a tiered prompting approach due to inconsistencies with other approaches.
An overview of the steps are as follows:

1. Calme LegalKit was first prompted with the comment to determine if it was a legal-based comment or not.
2. If it returns something other than true or false, the model is reprompted to provide either a true or false response
3. If it is a legal comment, it is labeled legal and the program moves to the next comment.
4. If not a legal comment, the program then prompts the Gemma 2 model for the next category.
5. It follows this approach until either a category is found or the model is unable to determine a category and determines it as unknown.

## Traditional Neural Network(NN) Approach

***

The team utilized SciKitLearn to locally run a large selection of traditional machine learning algorithms. The files for this approach can be found within the [this folder](https://github.com/ROADII-Lab/CAFE-public-comments/MinimalComputeApproach). Eight differrent models were tested with a large selection of different dataset cleaning and oversampling techniques to determine the best approach for the final use case. The code used to test differnt approaches can be found in [this file](https://github.com/ROADII-Lab/CAFE-public-comments/MinimalComputeApproach/minimalcompute.py). The best performing approach was found to be Log Loss SGD, and the selection can be found at the top of the main.py file.

### Models Tested

1. Logistic Regression
2. Ridge Classifier
3. K Nearest Neighbors (kNN)
4. Random Forest Classifier
5. Linear Support Vector Machine (SVC)
6. Log Loss Stochastic Gradient Descent (SGD)
7. Nearest Centroid
8. Complement Naive Bayes

### Process

1. training data is read, some items are reclassified to reduce similarities between categories.
2. The selected oversampling technique modifies the training data to account for the size and category imbalance in the data set.
3. Text to be categorized is loaded and chunked using [semantic-text-splitter](https://pypi.org/project/semantic-text-splitter/).
4. Chunked text and training data are combined and vectorized/tokenized.
5. Model is trained on training data.
6. Text chunks are categorized by model.
7. Model categorization is compared to keyword classification and updated if necessary.
8. Sequential chunks with matching categorizations are combined to reduce the number of output chunks.

### Execution with Machine Learning Approach

The steps to running the main machine learning pipeline are as follows:

1. Navigate to [main.py](https://github.com/ROADII-Lab/CAFE-public-comments/main.py)
2. Update file location of training data and text file to be chunked and categorized
3. Fill in keywordDict with any keywords you would like to use for classification
4. Select True or False for human intervention when keyword and neural network don't match
5. run [main.py](https://github.com/ROADII-Lab/CAFE-public-comments/main.py)

## Testing

Basic functionality testing is built into each file and can be run by simply running the file. Testing for edge cases and comparing results to expected values is currently left to human-based quality control.

## Additional Notes

Data used for this project is not stored within the repository. See below for information on where data came from and how to access it.
Models used for this project are also not stored within the repository. Follow model instructions for local hosting and interfacing with Python.

### Context on Previous Related Work

**Known Issues:**

None identified.

**Associated datasets:**

Data for this project was supplied by the CAFE public comments team. All data is publicly available at regulations.gov under the prevoius CAFE NPRM.

## Version History and Retention

**Status:** This project is in active development phase.

**Release Frequency:** This project will be updated when there are stable developments. This will be approximately every month.

**Retention:** This project will likely remain publicly accessible indefinitely.

**Release History:**  See [CHANGELOG.md](CHANGELOG.md)**

## License

This project is licensed under the Creative Commons 1.0 Universal (CC0 1.0) License - see the [License.MD](https://github.com/usdot-jpo-codehub/codehub-readme-template/blob/master/LICENSE) for more details.

## Contributions

Please read [CONTRIBUTING.md] for details on our Code of Conduct, the process for submitting pull requests to us, and how contributions will be released.

## Contact Information

Contact Name: Eric Englin
Contact Information: <Eric.Englin@dot.gov>

Contact Name: Andrew DeCandia
Contact Information: <Andrew.DeCandia@dot.gov>

## Acknowledgements

### Citing this code

To cite this code in a publication or report, please cite our associated report/paper and/or our source code. Below is a sample citation for this code:

*Sample citation should be in the below format, with the `formatted fields` replaced with details of your source code*

*`author_surname_or_organization`, `first_initial`. (`year`).* `program_or_source_code_title` *(`code_version`) [Source code]. Provided by ITS/JPO and Volpe Center through GitHub.com. Accessed YYYY-MM-DD from `doi_url`.*

When you copy or adapt from this code, please include the original URL you copied the source code from and date of retrieval as a comment in your code. Additional information on how to cite can be found in the [ITS CodeHub FAQ](https://its.dot.gov/code/#/faqs).

### Contributors

* Andrew DeCandia (Volpe)
* Vincent Livant (Volpe)
* Jeremy Hicks (Volpe)
* Robin Wilkinson (Volpe)
* Ben Clinton (Volpe)
* Ali Brodeur (Volpe)
* Billy Chupp (Volpe)
* Eric Englin (Volpe)

The development of ROADII that contributed to this public version was funded by the U.S. Intelligent Transportation Systems Joint Program Office (ITS JPO) under IAA HWE3A122. Any opinions, findings, conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the ITS JPO.
