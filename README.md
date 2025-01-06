# README Outline:
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

# Project Description

### ROADII Use Case - Categorizing Public Comments

- **Title:** Categorizing Public Comments for CAFE Rulemakings
- **Purpose and goals of the project:**
- **Purpose of the source code and how it relates to the overall goals of the project:**
- **Length of the project:** This use case is currently in the exploratory phase.


# Prerequisites

Requires:

# Usage

## Building

The [Code](https://github.com/ITSJPO-TRIMS/R25-IncidentDetection/tree/main/Code) folder contains the code and installation instructions of the ROADII-Lab exploration of the traffic incident detection use case. It will be populated with functions, model code, training parameters, and eductional materials to help potential users or stakeholders with the development process for the deployment of their own traffic incident detection system.



## Testing

Basic functionality testing is built into each file and can be run by running the file. Testing for edge cases and comparing results to expected values is currently left to human quality control.

## Execution

The steps to running the main pipeline are as follows:

1. Navigate to main.py
2. Update file location of training data and text file to be chunked and categorized
3. Fill in keywordDict with any keywords you woould like to use for classification
4. Select True or False for human intervention when keyword and NN don't match
5. run main.py

# Additional Notes



## Context on Previous Related Work

**Known Issues:**

None identified.

**Associated datasets:**



# Version History and Retention

**Status:** This project is in active development phase.

**Release Frequency:** This project will be updated when there are stable developments. This will be approximately every month.

**Retention:** This project will likely remain publicly accessible indefinitely.

**Release History:**  See [CHANGELOG.md](CHANGELOG.md)**


# License
This project is licensed under the Creative Commons 1.0 Universal (CC0 1.0) License - see the [License.MD](https://github.com/usdot-jpo-codehub/codehub-readme-template/blob/master/LICENSE) for more details.

# Contributions
Please read [CONTRIBUTING.md](https://github.com/ITSJPO-TRIMS/R25-IncidentDetection/blob/main/Contributing.MD) for details on our Code of Conduct, the process for submitting pull requests to us, and how contributions will be released.

# Contact Information

Contact Name: Eric Englin
Contact Information: Eric.Englin@dot.gov

Contact Name: Andrew DeCandia
Contact Information: Andrew.DeCandia@dot.gov


# Acknowledgements

*Sample citation should be in the below format, with the `formatted fields` replaced with details of your source code*

_`author_surname_or_organization`, `first_initial`. (`year`)._ `program_or_source_code_title` _(`code_version`) [Source code]. Provided by ITS/JPO and Volpe Center through GitHub.com. Accessed YYYY-MM-DD from `doi_url`._

## Citing this code

To cite this code in a publication or report, please cite our associated report/paper and/or our source code. Below is a sample citation for this code:

> ROADII Team. (2024). _ROADII README Template_ (0.1) [Source code]. Provided by ITS JPO through GitHub.com. Accessed 20214-02-23 from https://doi.org/xxx.xxx/xxxx.

When you copy or adapt from this code, please include the original URL you copied the source code from and date of retrieval as a comment in your code. Additional information on how to cite can be found in the [ITS CodeHub FAQ](https://its.dot.gov/code/#/faqs).

## Contributors

- Andrew DeCandia (Volpe)
- Vincent Livant (Volpe)
- Jeremy Hicks (Volpe)
- Robin Wilkinson (Volpe)
- Ben Clinton (Volpe)
- Ali Brodeur (Volpe)
- Billy Chupp (Volpe)
- Eric Englin (Volpe)

The development of ROADII that contributed to this public version was funded by the U.S. Intelligent Transportation Systems Joint Program Office (ITS JPO) under IAA HWE3A122. Any opinions, findings, conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the ITS JPO.
