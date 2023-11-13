BERT_BASE_NER_CONF = {
    "PRESIDIO_SUPPORTED_ENTITIES": [
        "LOCATION",
        "PERSON",
        "ORGANIZATION",
    ],
    "DEFAULT_MODEL_PATH": "dslim/bert-base-NER",
    "ONNX_MODEL_PATH": "laiyer/bert-base-NER-onnx",
    "LABELS_TO_IGNORE": ["O", "CARDINAL"],
    "DEFAULT_EXPLANATION": "Identified as {} by the dslim/bert-base-NER NER model",
    "SUB_WORD_AGGREGATION": "simple",
    "DATASET_TO_PRESIDIO_MAPPING": {
        "MISC": "O",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "PER": "PERSON",
    },
    "MODEL_TO_PRESIDIO_MAPPING": {
        "MISC": "O",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "PER": "PERSON",
    },
    "CHUNK_OVERLAP_SIZE": 40,
    "CHUNK_SIZE": 600,
    "ID_SCORE_MULTIPLIER": 0.4,
    "ID_ENTITY_NAME": "ID",
}

BERT_LARGE_NER_CONF = {
    "PRESIDIO_SUPPORTED_ENTITIES": [
        "LOCATION",
        "PERSON",
        "ORGANIZATION",
    ],
    "DEFAULT_MODEL_PATH": "dslim/bert-large-NER",
    "ONNX_MODEL_PATH": "laiyer/bert-large-NER-onnx",
    "LABELS_TO_IGNORE": ["O", "CARDINAL"],
    "DEFAULT_EXPLANATION": "Identified as {} by the dslim/bert-large-NER NER model",
    "SUB_WORD_AGGREGATION": "simple",
    "DATASET_TO_PRESIDIO_MAPPING": {
        "MISC": "O",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "PER": "PERSON",
    },
    "MODEL_TO_PRESIDIO_MAPPING": {
        "MISC": "O",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "PER": "PERSON",
    },
    "CHUNK_OVERLAP_SIZE": 40,
    "CHUNK_SIZE": 600,
    "ID_SCORE_MULTIPLIER": 0.4,
    "ID_ENTITY_NAME": "ID",
}

BERT_LARGE_CASED_FINETUNED_COLL03_ENGLISH_CONF = {
    "PRESIDIO_SUPPORTED_ENTITIES": [
        "LOCATION",
        "PERSON",
        "ORGANIZATION",
    ],
    "DEFAULT_MODEL_PATH": "dbmdz/bert-large-cased-finetuned-conll03-english",
    "ONNX_MODEL_PATH": "laiyer/bert-large-cased-finetuned-conll03-english-onnx",
    "LABELS_TO_IGNORE": ["O"],
    "DEFAULT_EXPLANATION": "Identified as {} by the dbmdz/bert-large-cased-finetuned-conll03-english NER model",
    "SUB_WORD_AGGREGATION": "simple",
    "DATASET_TO_PRESIDIO_MAPPING": {
        "MISC": "O",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "PER": "PERSON",
    },
    "MODEL_TO_PRESIDIO_MAPPING": {
        "MISC": "O",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "PER": "PERSON",
    },
    "CHUNK_OVERLAP_SIZE": 40,
    "CHUNK_SIZE": 600,
    "ID_SCORE_MULTIPLIER": 0.4,
    "ID_ENTITY_NAME": "ID",
}

ALL_RECOGNIZER_CONF = [
    BERT_BASE_NER_CONF,
    BERT_LARGE_NER_CONF,
    BERT_LARGE_CASED_FINETUNED_COLL03_ENGLISH_CONF,
]
