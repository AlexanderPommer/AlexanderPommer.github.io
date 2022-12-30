import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """

    contents = dict()
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.sep.join([root, file])
            with open(filepath, encoding="utf-8") as f:
                value = f.read()
                contents[file] = value

    return (contents)


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    stopwords = set(nltk.corpus.stopwords.words("english"))
    punctuation = set(string.punctuation)

    return [word.lower() for word in nltk.word_tokenize(document) if (word.lower() not in stopwords) and word.isalpha() and all([char not in punctuation for char in word])]


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    words = set()
    for filename in documents:
        words.update(documents[filename])

    idfs = dict()
    for word in words:
        frequency = sum(word in documents[filename] for filename in documents)
        idf = math.log(len(documents) / frequency)
        idfs[word] = idf

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    tfs = dict()
    ranking = dict()
    for filename in files:
        tf = dict()
        ranking[filename] = 0
        for word in query:
            tf[word] = 0
        # count how many times wach word in the query appears in each document (term frequencies)
        for word in files[filename]:
            if word in tf:
                tf[word] += 1
        # compute term frequency * inverse document frequency
        tfs[filename] = tf
        for word in tfs[filename]:
            frequency = tfs[filename][word]
            # add tf-idfs to file rankings
            ranking[filename] += frequency * idfs[word]
    
    rankedFilenames = sorted(ranking.items(), key=lambda d: d[1], reverse=True)

    return([x[0] for x in rankedFilenames][:n])


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    # maps sentence key to a list [matching word measure, query term density]
    matchValue = dict()
    for s in sentences:
        matchValue[s] = [0,0]
        # compute matching word measure
        for word in set(sentences[s]):
            if word in query and word in idfs:
                matchValue[s][0] += idfs[word]
        # compute query term density
        for word in sentences[s]:
            if word in query:
                matchValue[s][1] += 1
        matchValue[s][1] /= len(sentences[s])

    rankedSentences = sorted(matchValue.items(), key=lambda d: d[1], reverse=True)

    return([x[0] for x in rankedSentences][:n])


if __name__ == "__main__":
    main()
