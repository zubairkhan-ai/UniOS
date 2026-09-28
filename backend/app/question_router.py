# ===================================
# QUESTION ROUTER
# ===================================


def classify_question(question):

    question_lower = (
        question
        .lower()
        .strip()
    )


    # ===================================
    # ADVANTAGE
    # ===================================

    advantage_patterns = [

        "what are the advantages",
        "what is the advantage",
        "what are its advantages",
        "what is its advantage",
        "advantages of",
        "advantage of"
    ]


    for pattern in advantage_patterns:

        if question_lower.startswith(pattern):

            return "advantage"


    # ===================================
    # DISADVANTAGE
    # ===================================

    disadvantage_patterns = [

        "what are the disadvantages",
        "what is the disadvantage",
        "what are its disadvantages",
        "disadvantages of",
        "disadvantage of"
    ]


    for pattern in disadvantage_patterns:

        if question_lower.startswith(pattern):

            return "disadvantage"


    # ===================================
    # BENEFITS
    # ===================================

    benefit_patterns = [

        "what are the benefits",
        "what are its benefits",
        "benefits of"
    ]


    for pattern in benefit_patterns:

        if question_lower.startswith(pattern):

            return "benefit"


    # ===================================
    # USES
    # ===================================

    use_patterns = [

        "what are the uses",
        "what are its uses",
        "uses of"
    ]


    for pattern in use_patterns:

        if question_lower.startswith(pattern):

            return "use"


    # ===================================
    # TYPES
    # ===================================

    type_patterns = [

        "what are the types",
        "what are its types",
        "types of"
    ]


    for pattern in type_patterns:

        if question_lower.startswith(pattern):

            return "type"


    # ===================================
    # FEATURES
    # ===================================

    feature_patterns = [

        "what are the features",
        "what are its features",
        "features of"
    ]


    for pattern in feature_patterns:

        if question_lower.startswith(pattern):

            return "feature"


    # ===================================
    # DEFINITION
    # ===================================

    definition_patterns = [

        "what is ",
        "what are ",
        "define ",
        "definition of ",
        "meaning of "
    ]


    for pattern in definition_patterns:

        if question_lower.startswith(pattern):

            return "definition"


    # ===================================
    # EXPLANATION
    # ===================================

    explanation_patterns = [

        "explain",
        "how does",
        "how do",
        "how ",
        "why",
        "describe"
    ]


    for pattern in explanation_patterns:

        if question_lower.startswith(pattern):

            return "explanation"


    # ===================================
    # GENERAL
    # ===================================

    return "general"