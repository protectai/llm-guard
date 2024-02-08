BERT_BASE_NER_CONF = {
    "PRESIDIO_SUPPORTED_ENTITIES": [
        "LOCATION",
        "PERSON",
        "ORGANIZATION",
    ],
    "DEFAULT_MODEL_PATH": "dslim/bert-base-NER",
    "ONNX_MODEL_PATH": "dslim/bert-base-NER",
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
    "ONNX_MODEL_PATH": "dslim/bert-large-NER",
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

BERT_ZH_NER_CONF = {
    "PRESIDIO_SUPPORTED_ENTITIES": [
        "LOCATION",
        "PERSON",
        "ORGANIZATION",
    ],
    "DEFAULT_MODEL_PATH": "gyr66/bert-base-chinese-finetuned-ner",
    "ONNX_MODEL_PATH": "ProtectAI/gyr66-bert-base-chinese-finetuned-ner-onnx",
    "LABELS_TO_IGNORE": ["O", "CARDINAL"],
    "DEFAULT_EXPLANATION": "Identified as {} by the gyr66/bert-base-chinese-finetuned-ner NER model",
    "SUB_WORD_AGGREGATION": "simple",
    "DATASET_TO_PRESIDIO_MAPPING": {
        "MISC": "O",
        "address": "LOCATION",
        "company": "ORGANIZATION",
        "name": "PERSON",
    },
    "MODEL_TO_PRESIDIO_MAPPING": {
        "MISC": "O",
        "address": "LOCATION",
        "company": "ORGANIZATION",
        "name": "PERSON",
    },
    "CHUNK_OVERLAP_SIZE": 40,
    "CHUNK_SIZE": 600,
    "ID_SCORE_MULTIPLIER": 0.4,
    "ID_ENTITY_NAME": "ID",
}

ALL_RECOGNIZER_CONF = [
    BERT_BASE_NER_CONF,
    BERT_LARGE_NER_CONF,
    BERT_ZH_NER_CONF,
]
