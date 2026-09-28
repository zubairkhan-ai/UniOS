# ===================================
# QUESTION REWRITER
# ===================================


# ===================================
# CLEAN TOPIC
# ===================================

def clean_topic(topic):

    topic = topic.strip()

    # Remove question mark
    topic = topic.rstrip("?").strip()

    # Remove accidental leading words
    prefixes = [
        "the ",
        "a ",
        "an "
    ]

    for prefix in prefixes:

        if topic.lower().startswith(prefix):

            topic = topic[len(prefix):].strip()

    return topic


# ===================================
# WEAK TOPICS
# ===================================

def is_weak_topic(topic):

    if not topic:
        return True

    topic = topic.lower().strip()

    weak_topics = [

        # Pronouns
                # Pronouns
        "it",
        "this",
        "that",
        "they",
        "them",
        "these",
        "those",
        "its",
        "its functions",
        "what are its functions",
        "what are the functions",
        "functions",

        # Advantages
        "the advantages",
        "the advantage",
        "advantages",
        "advantage",
        "its advantages",
        "its advantage",
        "what are its advantages",
        "what are its advantage",
        "what are the advantages",
        "what are the advantage",

        # Benefits
        "the benefits",
        "benefits",
        "benefit",
        "its benefits",
        "what are its benefits",
        "what are the benefits",

        # Disadvantages
        "the disadvantages",
        "the disadvantage",
        "disadvantages",
        "disadvantage",
        "its disadvantages",
        "its disadvantage",
        "what are its disadvantages",
        "what are the disadvantages",

        # Uses
        "the uses",
        "uses",
        "use",
        "its uses",
        "what are its uses",
        "what are the uses",

        # Types
        "the types",
        "types",
        "type",
        "its types",
        "what are its types",
        "what are the types",

        # Features
        "the features",
        "features",
        "feature",
        "its features",
        "what are its features",
        "what are the features",

        # How it works
        "how it works",
        "how it work",
        "how does it work",
        "how does this work",
        "how this works",
        "how this work",

        # How to use
        "how do we use it",
        "how do i use it",
        "how to use it",
        "how do we use this",
        "how do i use this",
        "how to use this",

        # Why important
        "why is it important",
        "why is this important",
        "why is that important",

        # Definition follow-ups
        "what is it",
        "what is this",
        "what is that"
    ]

    return topic in weak_topics


# ===================================
# EXTRACT TOPIC
# ===================================

def extract_topic(question):

    question = (
        question
        .strip()
        .rstrip("?")
        .strip()
    )

    question_lower = question.lower()

    # ===================================
    # FOLLOW-UP QUESTIONS
    # ===================================

    if is_weak_topic(question):

        return None

    # ===================================
    # "WHAT ARE THE ADVANTAGES OF X?"
    # ===================================

    patterns = [

        "what are the advantages of ",
        "what are the benefits of ",
        "what are the disadvantages of ",
        "what are the uses of ",
        "what are the types of ",
        "what are the features of ",
        "what are the applications of ",
        "what are the methods of ",
        "what are the steps of "
    ]

    for pattern in patterns:

        if question_lower.startswith(pattern):

            topic = question[
                len(pattern):
            ]

            topic = clean_topic(topic)

            if not is_weak_topic(topic):

                return topic

    # ===================================
    # "ADVANTAGES OF X"
    # ===================================

    for phrase in [

        "advantages of ",
        "benefits of ",
        "disadvantages of ",
        "uses of ",
        "types of ",
        "features of ",
        "applications of ",
        "methods of ",
        "steps of "
    ]:

        if phrase in question_lower:

            index = question_lower.find(
                phrase
            )

            topic = question[
                index + len(phrase):
            ]

            topic = clean_topic(topic)

            if not is_weak_topic(topic):

                return topic

    # ===================================
    # DEFINITION
    # ===================================

    definition_patterns = [

        "what is ",
        "what are ",
        "define ",
        "definition of ",
        "meaning of ",
        "what about "
    ]

    for pattern in definition_patterns:

        if question_lower.startswith(pattern):

            topic = question[
                len(pattern):
            ]

            topic = clean_topic(topic)

            if not is_weak_topic(topic):

                return topic

            return None

    # ===================================
    # HOW DO WE USE X?
    # ===================================

    use_patterns = [

        "how do we use ",
        "how do i use ",
        "how to use "
    ]

    for pattern in use_patterns:

        if question_lower.startswith(pattern):

            topic = question[
                len(pattern):
            ]

            topic = clean_topic(topic)

            if not is_weak_topic(topic):

                return topic

            return None

    # ===================================
    # HOW DOES X WORK?
    # ===================================

    if question_lower.startswith(
        "how does "
    ):

        topic = question[
            len("how does "):
        ]

        if topic.lower().endswith(" work"):

            topic = topic[:-5].strip()

        topic = clean_topic(topic)

        if not is_weak_topic(topic):

            return topic

        return None

    # ===================================
    # HOW DO X WORK?
    # ===================================

    if question_lower.startswith(
        "how do "
    ):

        topic = question[
            len("how do "):
        ]

        if topic.lower().endswith(" work"):

            topic = topic[:-5].strip()

        topic = clean_topic(topic)

        if not is_weak_topic(topic):

            return topic

        return None

    # ===================================
    # FALLBACK
    # ===================================

    return question


# ===================================
# FIND PREVIOUS TOPIC
# ===================================

def find_previous_topic(chat_history):

    for message in reversed(chat_history):

        previous_question = message.get(
            "user",
            ""
        )

        topic = extract_topic(
            previous_question
        )

        if topic and not is_weak_topic(topic):

            return topic

    return None


# ===================================
# QUESTION REWRITER
# ===================================

def rewrite_question(
    question,
    chat_history
):

    # No history = nothing to rewrite
    if not chat_history:

        return question

    current = (
        question
        .strip()
        .rstrip("?")
        .strip()
    )

    current_lower = current.lower()
    # ===================================
    # WHAT ABOUT X?
    # ===================================

    if current_lower.startswith("what about "):

        topic = current[
            len("what about "):
        ].strip()

        topic = clean_topic(topic)

        if topic and not is_weak_topic(topic):

            return f"What is {topic}?"
    # ===================================
    # CHECK IF THIS IS A NEW QUESTION
    # ===================================

    current_topic = extract_topic(
        question
    )

    # IMPORTANT:
    # If the current question already contains
    # its own topic, DO NOT use an old topic.
    #
    # Example:
    #
    # Previous:
    # What is TCP?
    #
    # Current:
    # What is an operating system?
    #
    # Result:
    # operating system
    #
    # NOT:
    # TCP

    if (
        current_topic
        and not is_weak_topic(current_topic)
    ):

        print("\nDetected topic:")
        print(current_topic)

        return question

    # ===================================
    # FIND PREVIOUS TOPIC FOR FOLLOW-UPS
    # ===================================

    topic = find_previous_topic(
        chat_history
    )

    if not topic:

        return question

    print("\nDetected topic:")
    print(topic)

    # ===================================
    # ADVANTAGES
    # ===================================

    if current_lower in [
        "what are its advantages",
        "what are its advantage",
        "its advantages",
        "its advantage",
        "what are the advantages",
        "what are the advantage",
        "advantages"
    ]:

        return (
            f"What are the advantages of {topic}?"
        )

    # ===================================
    # BENEFITS
    # ===================================

    if current_lower in [
        "what are its benefits",
        "its benefits",
        "what are the benefits",
        "benefits"
    ]:

        return (
            f"What are the benefits of {topic}?"
        )

    # ===================================
    # DISADVANTAGES
    # ===================================

    if current_lower in [
        "what are its disadvantages",
        "its disadvantages",
        "what are the disadvantages",
        "disadvantages"
    ]:

        return (
            f"What are the disadvantages of {topic}?"
        )

    # ===================================
    # USES
    # ===================================

    if current_lower in [
        "what are its uses",
        "its uses",
        "what are the uses",
        "uses"
    ]:

        return (
            f"What are the uses of {topic}?"
        )

    # ===================================
    # TYPES
    # ===================================

    if current_lower in [
        "what are its types",
        "its types",
        "what are the types",
        "types"
    ]:

        return (
            f"What are the types of {topic}?"
        )

    # ===================================
    # FEATURES
    # ===================================

    if current_lower in [
        "what are its features",
        "its features",
        "what are the features",
        "features"
    ]:

        return (
            f"What are the features of {topic}?"
        )

    # ===================================
    # FUNCTIONS
    # ===================================

    if current_lower in [
        "what are its functions",
        "its functions",
        "what are the functions",
        "functions"
    ]:

        return (
            f"What are the functions of {topic}?"
        )

    # ===================================
    # HOW TO USE
    # ===================================

    if current_lower in [
        "how do we use it",
        "how do i use it",
        "how to use it",
        "how do we use this",
        "how do i use this",
        "how to use this"
    ]:

        return (
            f"How is {topic} used?"
        )

    # ===================================
    # HOW IT WORKS
    # ===================================

    if current_lower in [
        "how it works",
        "how it work",
        "how does it work",
        "how does this work",
        "how this works",
        "how this work"
    ]:

        return (
            f"How does {topic} work?"
        )

    # ===================================
    # WHY IS IT IMPORTANT
    # ===================================

    if current_lower in [
        "why is it important",
        "why is this important",
        "why is that important"
    ]:

        return (
            f"Why is {topic} important?"
        )

    # ===================================
    # WHAT IS IT
    # ===================================

    if current_lower in [
        "what is it",
        "what is this",
        "what is that"
    ]:

        return (
            f"What is {topic}?"
        )

    # ===================================
    # FOLLOW-UP WITH IT / THIS
    # ===================================

    follow_up_words = [
        "it",
        "this",
        "that",
        "they",
        "them",
        "these",
        "those"
    ]

    words = current_lower.split()

    if any(
        word in words
        for word in follow_up_words
    ):

        return (
            f"{topic}. {current}"
        )

    # ===================================
    # NO REWRITE NEEDED
    # ===================================

    return question