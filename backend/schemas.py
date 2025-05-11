from typing import Annotated, Sequence, List, Literal 
from pydantic import BaseModel, Field 




class TaskSummarizer(BaseModel):
    next: Literal["supervisor"] = Field(
        description="Based on the user's input, summarize the task"
                    "Provide an action plan using Chain of Thought reasoning"
                    "and provide a list of steps to complete the task."
    )
    reason: str = Field(
        description="Detailed justification for the routing decision, explaining the rationale behind selecting the particular specialist and how this advances the task toward completion."
    )    


class Supervisor(BaseModel):
    next: Literal["researcher", "coder"] = Field(
        description="Determines which specialist to activate next in the workflow sequence: "
                    "'researcher' when additional facts, context, or data collection is necessary, "
                    "'coder' when implementation, computation, or technical problem-solving is required."
    )
    reason: str = Field(
        description="Detailed justification for the routing decision, explaining the rationale behind selecting the particular specialist and how this advances the task toward completion."
    )


class UserQuery(BaseModel):
    query: str = Field(
        description="The user's input or question that needs to be addressed by the agent."
    )

