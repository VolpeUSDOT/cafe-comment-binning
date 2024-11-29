import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Confusion matrix data
cm = np.array([[122, 41], [66, 120]])

# Create heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()