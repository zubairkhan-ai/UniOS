from transformers import (
    pipeline,
    AutoTokenizer
)

from langchain_huggingface import HuggingFacePipeline


# =========================================================
# MODEL
# =========================================================

MODEL_NAME = (
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
)


# =========================================================
# TOKENIZER
# =========================================================

print(
    "Loading TinyLlama tokenizer..."
)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)


# =========================================================
# MODEL
# =========================================================

print(
    "Loading TinyLlama model..."
)

generator = pipeline(
    "text-generation",

    model=MODEL_NAME,

    tokenizer=tokenizer,

    max_new_tokens=120,

    do_sample=False,

    return_full_text=False
)


# =========================================================
# LANGCHAIN
# =========================================================

llm = HuggingFacePipeline(
    pipeline=generator
)


# =========================================================
# CLEAN ANSWER
# =========================================================

def clean_answer(response):

    response = response.strip()

    prefixes = [
        "ANSWER:",
        "Answer:",
        "AI:",
        "Assistant:"
    ]

    for prefix in prefixes:

        if response.startswith(prefix):

            response = (
                response[len(prefix):]
                .strip()
            )

    # Remove model continuation
    stop_phrases = [
        "\nQUESTION:",
        "\nQuestion:",
        "\nLECTURE CONTEXT:",
        "\nLecture Context:",
        "\nUSER:",
        "\nUser:"
    ]

    for phrase in stop_phrases:

        if phrase in response:

            response = (
                response
                .split(phrase)[0]
                .strip()
            )

    return response


# =========================================================
# GENERATE ANSWER
# =========================================================

def generate_answer(
    question,
    context
):

    messages = [

        {
            "role": "system",

            "content": (

                "You are a university study assistant. "

                "Answer ONLY from the supplied lecture "
                "context. "

                "Do not use outside knowledge. "

                "Do not invent information. "

                "Do not discuss unrelated parts of the "
                "lecture. "

                "Answer the student's exact question. "

                "If the context does not contain enough "
                "information, say: "
                "'The answer is not available in the "
                "provided lecture material.' "

                "Keep the answer concise. "

                "Return only the answer."
            )
        },

        {
            "role": "user",

            "content": (

                "LECTURE CONTEXT:\n\n"

                f"{context}\n\n"

                "QUESTION:\n\n"

                f"{question}\n\n"

                "ANSWER:"
            )
        }
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    response = llm.invoke(
        prompt
    )

    return clean_answer(
        response
    )