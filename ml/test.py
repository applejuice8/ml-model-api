from sklearn.metrics import confusion_matrix, classification_report
import joblib

# Load model, data
model = joblib.load('ml/models/spam_detector.pkl')
X_test, y_test = joblib.load('ml/test_data/spam_data.pkl')

# Evaluation
y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
cr = classification_report(y_test, y_pred)

print(f'Score: {model.score(X_test, y_test)}\n')
print(f'\nConfusion matrix:\n {cm}\n')
print(f'\nClassification report:\n {cr}\n')
