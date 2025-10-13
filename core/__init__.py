# ========================================
# core/__init__.py
# ========================================
"""
Módulo Core - Lógica Principal
"""
from .state import (
    AgentState,
    Requirements,
    Plan,
    Review,
    Solution,
    ValidationResult,
    DemandType,
    create_initial_state,
    get_requirements,
    get_plan,
    get_solution
)
from .schemas import (
    ClassificationOutput,
    ReviewOutput,
    PlanningPromptsOutput,
    PlanOutput,
    PlanStep,
    RiskItem,
    SolutionOutput,
    CodeIssue,
    CodeSuggestion,
    CodeQualityScore,
    CodeReviewOutput,
    FailedCheck,
    DeliverablesChecklist,
    ValidationOutput
)
from .graph import (
    create_agent_graph,
    get_graph_visualization,
    get_current_step_description
)

__all__ = [
    # State
    "AgentState",
    "Requirements",
    "Plan",
    "Review",
    "Solution",
    "ValidationResult",
    "DemandType",
    "create_initial_state",
    "get_requirements",
    "get_plan",
    "get_solution",
    # Schemas
    "ClassificationOutput",
    "ReviewOutput",
    "PlanningPromptsOutput",
    "PlanOutput",
    "PlanStep",
    "RiskItem",
    "SolutionOutput",
    "CodeIssue",
    "CodeSuggestion",
    "CodeQualityScore",
    "CodeReviewOutput",
    "FailedCheck",
    "DeliverablesChecklist",
    "ValidationOutput",
    # Graph
    "create_agent_graph",
    "get_graph_visualization",
    "get_current_step_description",
]
