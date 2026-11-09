 
import nltk
from nltk.tokenize import word_tokenize
import string
import matplotlib.pyplot as plt

def analyze_text(text):
    paragraph = text
    #nltk.download('punkt')
    tokens = word_tokenize(paragraph)
    tokens = [word for word in tokens if word not in string.punctuation]
    print("Tokens:", tokens)
    print("total words count: ",len(tokens))
    print("Unique words count:", len(set(word.lower() for word in tokens)))

    frequency = {}

    for word in tokens:
        word = word.lower()
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1

    print("Words occurring only once:")
    for word, count in frequency.items():
        if count == 1:
            print(word)

    print("Five most frequently used words:")
    sorted_words = sorted(frequency.items(), key=lambda x: x[1], reverse=True)

    for word, count in sorted_words[:5]:
        print(word, ":", count)

    return {
        "tokens": tokens,
        "total_words": len(tokens),
        "unique_words": len(set(word.lower() for word in tokens)),
        "words_occurring_once": [word for word, count in frequency.items() if count == 1],
        "most_frequent_words": sorted_words[:5]
    }
