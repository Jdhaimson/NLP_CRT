# Codebase - Predicting Efficacy of Cardiac Resynchronization Therapy Using NLP and ML
## - _Charlotta Lindvall, Josh Haimson, Alex Forsynth, Michael Traub, Austin Freel_

## Description:

The project code can be categorized into 3 groups:
1. Data management and extraction
2. Transformers for data pipeline
3. Methods for queueing, building, and exceuting tests

Below I will group the file names by these categories, and all
files not mentioned are miscelaneous, superfluous or unimportant.

(1) DATA MANAGEMENT, EXTRACTION AND VALIDATION
    
    anonymizer.py -- anonymizes MRNs, SSNs and names from free text during initial data transformation
    extract_data.py -- misc data extraction functions
    free_text_jsonifyer.py -- Extracts meta data from free text files
    language_processing.py -- used to clean extracted values
    loader.py -- Loads patient data from disk
    tables.py -- generates table statistics for paper
    validate.py -- Generates statistics to validate results
    generateTurkTasks.py -- Creates a csv file for localturk to efficiently do manual extraction

(2) TRANSFORMERS

    baseline_transformer.py -- contains all structured data transformers
    doc2vec_trainer.py -- Creates doc2vec models to be used by doc2vec transformer
    doc2vec_transformer.py -- Transforms arbitrary length text into fixed dimensional semantic representation
    icd_transformer.py -- Transforms ICD9 code into hierarchical numeric representation
    value_extractor_transformer.py -- contains the Regex extractors

(3) QUEUING, BUILDING, AND EXECUTING TESTS

    decision_model.py -- contains the hard-coded clincical guideline
    experiment_runner.py -- Daemon process to continually run tests
    model_builder.py -- Build ML/NLP models to test
    model_tester.py -- Used by experiment runer to run a test on a given model
    queue_test.py -- Helper function to queue up tests
    run_test.py -- Standalone code to run an individual model and test
