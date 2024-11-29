import spacy
from sklearn.metrics import accuracy_score, classification_report
from classy_classification import *
import pandas as pd
import random
import numpy as np
import time

data = {
    "legal": ["The proposed NHTSA standards are not as strong as what EPA has proposed. These two rules, if aligned, could benefit lung health by ensuring that new cars are less polluting.", "NHTSA should adopt EPA’s approach for modeling the Clean Vehicle Credit and the Commercial Credit jointly. Since the Treasury Department clarified that leased vehicles qualify for the Commercial Credit, many more vehicles now qualify for federal incentives leading to reduced cost of ownership and greater EV penetration.", "NHTSA projects that manufacturers will pay over $14 billion in non-compliance penalties, effecting one in every two light trucks in 2027-2032, and one in every three passenger cars in 2027-2029. The number of non-compliant vehicles and manufacturers projected exceeds reason and simply put, will increase costs to the American consumer with absolutely no environmental or fuel savings benefits. The projected $3,000 average price increase over today’s vehicles is likely to decrease sales and increase the average age of vehicles on our roads. Although NHTSA may balance its statutory considerations that were established by Congress, it cannot minimize consideration of technological feasibility and economic practicability to the extent that they are rendered meaningless."],

    "non-legal": ["Estimates for the benefits of the CAFE standards are also undoubtedly inflated. For starters, NHTSA does not consider opportunity costs in their cost-benefit analysis. Improving the fuel efficiency of vehicles requires removing other features to reduce weight, such as trunk space and towing capacity. Michael Buschbacher and James Conde, Shocking Candor on Fuel Standards, The Wall Street Journal, August 23, 2023, https://www.wsj.com/articles/transportation-department-fuel- standards-car-ev-electricvehicle-auto-industry-climate-change-388d6dd0, (Accessed October 11, 2023). Incorporating these tradeoffs is necessary to produce accurate cost-benefit analyses and would reduce net benefits for all three categories further.", "NHTSA should phase out off-cycle fuel consumption improvement values for all vehicle types—EVs and internal combustion—in the CAFE program. NHTSA itself acknowledges that “There is not currently a mechanism to confirm that the off-cycle technologies provide fuel savings commensurate with” the menu values, even in internal combustion vehicles. Therefore, NHTSA should treat EVs and conventional vehicles the same and eliminate off-cycle values for all vehicles beginning in model year 2027. If the agency elects to keep any off-cycle credits, we urge NHTSA to accelerate the cap phasedown to zero by model year 2030."]
}

nlp = spacy.load('en_core_web_md')
nlp.add_pipe("classy_classification", config={
    "data": data,
    "model": "spacy"
})

# Load Excel file
FILE_PATH = "legalVnon_legal.xlsx"
DATA_FRAME = pd.read_excel(FILE_PATH)

# Apply classification to column A and append results to column C
DATA_FRAME['Predicted Label'] = DATA_FRAME['Comments'].apply(lambda x: nlp(x)._.cats)

DATA_FRAME['Predicted Label'] = DATA_FRAME['Predicted Label'].apply(lambda x: 'legal' if x['legal'] > x['non-legal'] else 'non-legal')

# Save updated DataFrame to Excel
DATA_FRAME.to_excel('updated_legalVnon_legal.xlsx', index=False)

accuracy = accuracy_score(DATA_FRAME['Actual Label'], DATA_FRAME['Predicted Label'])
print("Accuracy:", accuracy)
print("Classification Report:")
print(classification_report(DATA_FRAME['Actual Label'], DATA_FRAME['Predicted Label']))
