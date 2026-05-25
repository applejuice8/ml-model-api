import kagglehub
from kagglehub import KaggleDatasetAdapter
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
import joblib


def load_dataset():
    # https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset?select=spam.csv
    return kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        'uciml/sms-spam-collection-dataset',
        'spam.csv',
        pandas_kwargs={"encoding": "latin-1"}
    )


def split_X_y_train_test(df):
    X = df['v2']
    y = df['v1']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=0.3, stratify=y
    )

    # Transform spam, ham to 0, 1
    le = LabelEncoder()
    y_train = le.fit_transform(y_train)
    y_test = le.transform(y_test)

    return X_train, X_test, y_train, y_test


def setup_pipe():
    vectorizer = TfidfVectorizer(
        binary=True,
        max_df=0.9,
        min_df=0.001,
        stop_words='english',
        sublinear_tf=True
    )

    model = MLPClassifier(
        alpha=0.1, 
        hidden_layer_sizes=(20, 30, 20),
        max_iter=4000, 
        random_state=42
    )

    return Pipeline([
        ('vec', vectorizer),
        ('model', model)
    ])


def train():
    df = load_dataset()
    X_train, X_test, y_train, y_test = split_X_y_train_test(df)
    pipe = setup_pipe()
    pipe.fit(X_train, y_train)

    # Save model, data
    joblib.dump(pipe, 'ml/models/spam_detector.pkl')
    joblib.dump((X_test, y_test), 'ml/test_data/spam_data.pkl')

if __name__ == '__main__':
    train()
