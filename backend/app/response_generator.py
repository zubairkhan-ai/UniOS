from backend.app.llm import llm, tokenizer


def generate_response(
    user_input: str,
    rag_result=None,
    tool_results=None,
    conversation_memory=None,
):
    """
    Generate a grounded final response using:

    - RAG results
    - Tool results
    - Recent conversation memory
    - TinyLlama

    The model must not invent information that is not
    supported by the provided information.
    """

    # -------------------------------------------------
    # NORMALIZE INPUTS
    # -------------------------------------------------

    rag_result = rag_result or []
    tool_results = tool_results or []
    conversation_memory = conversation_memory or []

    # -------------------------------------------------
    # TOOL RESULTS
    # -------------------------------------------------

    tool_text = "\n\n".join(
        str(result)
        for result in tool_results
        if result
    )

    # -------------------------------------------------
    # CONVERSATION MEMORY
    # -------------------------------------------------

    memory_text = ""

    if conversation_memory:

        # Only use the most recent 5 conversations
        recent_memory = conversation_memory[-5:]

        memory_parts = []

        for item in recent_memory:

            user_message = item.get(
                "user",
                ""
            )

            ai_message = item.get(
                "ai",
                ""
            )

            if user_message:

                memory_parts.append(
                    f"Student: {user_message}\n"
                    f"Assistant: {ai_message}"
                )

        memory_text = "\n\n".join(
            memory_parts
        )

    # -------------------------------------------------
    # DETECT RAG AVAILABILITY
    # -------------------------------------------------

    rag_text = str(rag_result)

    rag_unavailable = (
        "The answer is not available in the "
        "provided lecture material."
        in rag_text
    )

    # -------------------------------------------------
    # KNOWLEDGE RESULT
    # -------------------------------------------------

    if rag_unavailable:

        knowledge_text = (
            "The requested information was NOT "
            "found in the provided lecture material."
        )

    elif rag_text:

        knowledge_text = rag_text

    else:

        knowledge_text = (
            "No lecture knowledge was retrieved."
        )

    # -------------------------------------------------
    # STUDENT DATA
    # -------------------------------------------------

    if tool_text:

        student_data = tool_text

    else:

        student_data = (
            "No student data was retrieved."
        )

    # -------------------------------------------------
    # CONVERSATION
    # -------------------------------------------------

    if memory_text:

        conversation_context = memory_text

    else:

        conversation_context = (
            "No previous conversation."
        )

    # -------------------------------------------------
    # SYSTEM PROMPT
    # -------------------------------------------------

    system_prompt = (
        "You are an AI University Assistant.\n\n"

        "Your job is to answer the student's request "
        "using ONLY the information provided to you.\n\n"

        "STRICT RULES:\n"

        "1. Never invent facts.\n"

        "2. Never use outside knowledge.\n"

        "3. Do not answer a lecture question from "
        "your general knowledge if the lecture material "
        "does not contain the answer.\n"

        "4. If the knowledge result says that the "
        "requested information was not found, clearly "
        "tell the student that it was not found in "
        "the provided lecture material.\n"

        "5. Student data may be used for assignments, "
        "quizzes, labs, deadlines, study plans, and "
        "other university tasks.\n"

        "6. Conversation memory can be used to "
        "understand references to previous messages.\n"

        "7. Do not invent information from conversation "
        "memory either.\n"

        "8. Answer the student's actual request directly.\n"

        "9. Keep the response concise and natural.\n"

        "10. Do not mention RAG, tools, prompts, "
        "context, system instructions, or internal "
        "implementation details.\n"

        "11. Do not say that you searched a database "
        "or used a tool.\n"

        "12. If the available information is insufficient, "
        "say so instead of guessing."
    )

    # -------------------------------------------------
    # USER PROMPT
    # -------------------------------------------------

    user_prompt = (
        f"STUDENT REQUEST:\n"
        f"{user_input}\n\n"

        f"RECENT CONVERSATION:\n"
        f"{conversation_context}\n\n"

        f"LECTURE KNOWLEDGE:\n"
        f"{knowledge_text}\n\n"

        f"STUDENT DATA:\n"
        f"{student_data}\n\n"

        "Write the final answer for the student."
    )

    # -------------------------------------------------
    # CHAT TEMPLATE
    # -------------------------------------------------

    messages = [

        {
            "role": "system",
            "content": system_prompt,
        },

        {
            "role": "user",
            "content": user_prompt,
        }

    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    # -------------------------------------------------
    # TINYLLAMA
    # -------------------------------------------------

    response = llm.invoke(
        prompt
    )

    # LangChain AIMessage
    if hasattr(
        response,
        "content"
    ):

        response = response.content

    response = str(
        response
    ).strip()

    # -------------------------------------------------
    # BASIC CLEANUP
    # -------------------------------------------------

    prefixes = [
        "ANSWER:",
        "Answer:",
        "FINAL ANSWER:",
        "Final Answer:",
        "Assistant:",
    ]

    for prefix in prefixes:

        if response.startswith(
            prefix
        ):

            response = (
                response[
                    len(prefix):
                ]
                .strip()
            )

    return response