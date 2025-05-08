from sklearn.feature_extraction.text import TfidfVectorizer
from pytrends.request import TrendReq

#from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
#from tensorflow.keras.preprocessing import image
import numpy as np

#model = ResNet50(weights='imagenet', include_top=False)

#def thumbnail_score(img_path):
#    img = image.load_img(img_path, target_size=(224, 224))
#    x = preprocess_input(np.expand_dims(image.img_to_array(img), axis=0))
#    features = model.predict(x)
#    score = np.mean(features)
#    return round(score, 2)

"""def detect_spike(keyword):
    data = pytrends.get_historical_interest([keyword], year_start=2024, ...)
    if sudden_spike(data):
        send_alert(keyword)"""

def extract_keywords(texts):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)
    return vectorizer.get_feature_names_out()

def get_trending_topics(keyword):
    pytrends = TrendReq()
    pytrends.build_payload([keyword], timeframe='now 7-d')
    return pytrends.related_queries()

def compare_channels(channel_1_id, channel_2_id):
    stats1 = get_channel_stats(channel_1_id)
    stats2 = get_channel_stats(channel_2_id)
    return {"comp1": stats1, "comp2": stats2}

