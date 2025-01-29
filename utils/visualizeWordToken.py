import matplotlib.pyplot as plt
import tiktoken


# a funciton that createa hsitogram of the word count in all rows of SoP
def createHistogram(df):
    wordCounts = [
        len(cleanString(row["statement_of_purpose"]).split())
        for index, row in df.iterrows()
    ]
    tokenCounts = [
        len(
            tiktoken.encoding_for_model("gpt-4o").encode(
                cleanString(row["statement_of_purpose"])
            )
        )
        for index, row in df.iterrows()
    ]
    plt.hist(wordCounts, bins=range(0, max(wordCounts) + 100, 100))
    plt.xlabel("Word Count")
    plt.ylabel("Frequency")
    plt.title("Histogram of Word Counts in SoP")
    plt.show()

    # create a new histogram for the token counts
    plt.hist(tokenCounts, bins=range(0, max(tokenCounts) + 100, 100))
    plt.xlabel("Token Count")
    plt.ylabel("Frequency")
    plt.title("Histogram of Token Counts in SoP")
    plt.show()
