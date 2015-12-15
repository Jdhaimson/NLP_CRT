################################################################

    6.806 Final Project
    Austin Freel, Josh Haimson, Michael Traub

################################################################

The project code can be categorized into 3 groups:
    1. Data management and extraction
    2. Transformers for data pipeline
    3. Methods for queueing, building, and exceuting tests

Below I will group the file names by these categories, and all
files not mentioned are miscelaneous, superfluous or unimportant.

(1) DATA MANAGEMENT AND EXTRACTION
    anonymizer.py -- we had to anonymize the data before we could use it
    extract_data.py
    free_text_jsonifyer.py
    language_processing.py -- used to clean extracted values
    loader.py

(2) TRANSFORMERS
    baseline_transformer.py -- contains all structured data transformers
    doc2vec_trainer.py
    doc2vec_transformer.py
    icd_transformer.py
    value_extractor_transformer.py -- contains the Regex extractors

(3) QUEUING, BUILDING, AND EXECUTING TESTS
    decision_model.py -- contains the hard-coded clincical guideline
    experiment_runner.py
    model_builder.py
    model_tester.py
    queue_test.py

################################################################

BRIEF EXPLANATION OF QUEUEING PROCESS

In order to run our CPU and time intensive tests in the background
so that we did not need to be connected to the server to see the
output, we designed a daeomon process to execute these tests
based on a CSV input file and write to a CSV output file. 
