import matplotlib.pyplot as plt
import os

def create_word_chart(words):
    chart_path = os.path.join("static", "word_chart.png")

    word_list = [word for word, count in words]
    counts = [count for word, count in words]

    plt.figure(figsize=(16,7))

    plt.bar(word_list, counts)

    plt.title("Word Frequency")
    plt.xlabel("Words")
    plt.ylabel("Frequency")

    plt.tight_layout()

    plt.savefig(chart_path)
    plt.close()

    return chart_path