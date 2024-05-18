from typing import Dict, Any, Tuple, Optional
from llama_index.core import ChatPromptTemplate
from llama_index.core.bridge.pydantic import Field, BaseModel


DEFAULT_PROMPT_STR = """
Given previous question/response pairs, please determine if an error has occurred in the response, and suggest \
a modified question that will not trigger the error.

Examples of modified questions:
- The question itself is modified to elicit a non-erroneous response
- The question is augmented with context that will help the downstream system better answer the question.
- The question is augmented with examples of negative responses, or other negative questions.

An error means that either an exception has triggered, or the response is completely irrelevant to the question.

Please return the evaluation of the response in the following JSON format.

"""


def get_chat_prompt_template(
    system_prompt: str, current_reasoning: Tuple[str, str]
) -> ChatPromptTemplate:
    system_msg = ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
    messages = [system_msg]
    for raw_msg in current_reasoning:
        if raw_msg[0] == "user":
            messages.append(
                ChatMessage(role=MessageRole.USER, content=raw_msg[1])
            )
        else:
            messages.append(
                ChatMessage(role=MessageRole.ASSISTANT, content=raw_msg[1])
            )
    return ChatPromptTemplate(message_templates=messages)

class ResponseEval(BaseModel):
    """Evaluation of whether the response has an error."""

    has_error: bool = Field(
        ..., description="Whether the response has an error."
    )
    new_question: str = Field(..., description="The suggested new question.")
    explanation: str = Field(
        ...,
        description=(
            "The explanation for the error as well as for the new question."
            "Can include the direct stack trace as well."
        ),
    )
