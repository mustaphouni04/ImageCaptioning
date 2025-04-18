import evaluate
import nltk
nltk.download('wordnet')
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from os import path

def read_jayson(path):
    """Reads a JSON file containing image descriptions, predictions, and labels.

    Args:
    path (str): The path to the JSON file.

    Returns:
    tuple: A tuple containing three lists:
        - predictions: A list of predicted descriptions.
        - label: A list of ground truth descriptions.
        - image: A list of image filenames.
    """

    # Read the JSON file into a Pandas DataFrame
    df = pd.read_json("descriptions.json")

    # Extract the columns as lists
    predictions = df[0].tolist()
    label = df[1].tolist()
    image = df[2].tolist()

    # Assert that all lists have the same length
    assert len(predictions) == len(image) == len(text)

    # Iterate over the lists, cleaning up the predictions and labels
    i=0
    while i < len(predictions):
        label[i] = label[i][14:]
        predictions[i] = predictions[i][58:-1]
        i +=1
    return predictions, label, image

def compute_metrics(predicted, label):
    """
    Compute BLEU, ROUGE, and METEOR scores for a single predicted sentence
    against a single reference sentence.

    Args:
    predicted (str): The predicted sentence.
    label (str): The ground-truth reference sentence.

    Returns:
    dict: A dictionary containing BLEU, ROUGE-1, ROUGE-2, ROUGE-L, and METEOR scores.
    """
    # Initialize BLEU metric from evaluate
    bleu_metric = evaluate.load("bleu")

    # Compute BLEU score
    bleu_1 = bleu_metric.compute(predictions=[predicted], references=[[label]], max_order=1)['bleu']
    bleu_2 = bleu_metric.compute(predictions=[predicted], references=[[label]], max_order=2)['bleu']

    # Initialize ROUGE scorer
    rouge_scorer_instance = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = rouge_scorer_instance.score(label, predicted)

    # Extract ROUGE scores
    rouge_scores = {
        "ROUGE-1": scores['rouge1'].fmeasure,
        "ROUGE-2": scores['rouge2'].fmeasure,
        "ROUGE-L": scores['rougeL'].fmeasure
    }

    # Compute METEOR score (tokenizing both label and prediction)
    meteor = meteor_score([label.split()], predicted.split())

    # Return the results
    return {
        "BLEU-1": bleu_1,
        "BLEU-2": bleu_2,
        "ROUGE-1": rouge_scores["ROUGE-1"],
        "ROUGE-2": rouge_scores["ROUGE-2"],
        "ROUGE-L": rouge_scores["ROUGE-L"],
        "METEOR": meteor
    }

def evaluate_model(predictions, labels):
    """
    Evaluate a list of predictions against their corresponding single reference sentences.
    Calls `compute_metrics` for each prediction-label pair and aggregates results.

    Args:
    predictions (list of str): The predicted sentences.
    labels (list of str): The ground-truth reference sentences.

    Returns:
    dict: A dictionary with average BLEU, ROUGE-1, ROUGE-2, ROUGE-L, and METEOR scores,
          as well as a detailed breakdown of scores for each prediction.
    """
    assert len(predictions) == len(labels), "The number of predictions and labels must match."

    # Initialize accumulators for metrics
    metrics_summary = {
        "BLEU-1": [],
        "BLEU-2": [],
        "ROUGE-1": [],
        "ROUGE-2": [],
        "ROUGE-L": [],
        "METEOR": []
    }
    detailed_metrics = []

    # Compute metrics for each prediction
    for pred, label in zip(predictions, labels):
        metrics = compute_metrics(pred, label)
        detailed_metrics.append(metrics)

        for key in metrics:
            metrics_summary[key].append(metrics[key])

    # Compute average metrics
    avg_metrics = {key: sum(values) / len(values) for key, values in metrics_summary.items()}

    return {
        "Average Metrics": avg_metrics,
        "Detailed Metrics": detailed_metrics
    }

# Example Usage
predictions = ["The cat is sitting on the mat.", "The dog is running in the yard."]
labels = ["The cat is on the mat.", "The dog plays in the garden."]

results = evaluate_model(predictions, labels)

# Print average metrics
print("Average Metrics:")
for metric, score in results["Average Metrics"].items():
    print(f"{metric}: {score:.4f}")

# Optionally print detailed metrics for each prediction
print("\nDetailed Metrics:")
for i, metrics in enumerate(results["Detailed Metrics"]):
    print(f"Prediction {i+1}:")
    for metric, score in metrics.items():
        print(f"  {metric}: {score:.4f}")
