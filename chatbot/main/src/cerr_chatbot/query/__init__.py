"""Query-side helpers for the chatbot read path.

Public surface (re-exported here):
- semantic catalog: `SEMANTIC_CATALOG`, `SemanticView`, `SemanticViewColumn`
- SQL safety + execution: `validate`, `ValidatedSql`, `SqlGuardError`,
  `ALLOWED_VIEWS`, `DEFAULT_LIMIT`, `MAX_LIMIT`, `execute`, `QueryResult`
- LLM SQL planner: `build_planner_prompt`, `parse_planner_response`,
  `PlannerDecision`, `DecisionKind`, `ALLOWED_KINDS`, `PlannerParseError`
- Service orchestration: `QueryService`, `QueryServiceResult`, `ServiceKind`,
  `Planner`

No HTTP API, no answer-generation step, no real LLM network call from this
package - planners are injected.
"""

from cerr_chatbot.query.answer import NULL_DISPLAY, Answer, compose_answer
from cerr_chatbot.query.answer_brief import (
    AnswerBrief,
    AnswerType,
    build_answer_brief,
    render_brief_for_prompt,
)
from cerr_chatbot.query.conversational_router import (
    CAPABILITY_REPLY,
    GREETING_REPLY,
    HELP_REPLY,
    OUT_OF_SCOPE_REPLY,
    ConversationalResponse,
    ConversationKind,
)
from cerr_chatbot.query.conversational_router import (
    classify as classify_intent,
)
from cerr_chatbot.query.evidence import (
    MAX_CONTEXT_QUERIES,
    EvidenceKind,
    EvidencePack,
    EvidencePlanner,
    EvidencePlanParseError,
    EvidenceQueryResult,
    EvidenceServiceResult,
    ParsedContextQuery,
    ParsedEvidencePlan,
    evidence_ask,
    parse_evidence_plan,
)
from cerr_chatbot.query.evidence_narrator import (
    EvidenceLlmNarrator,
    build_evidence_prompt,
)
from cerr_chatbot.query.evidence_planner import (
    EvidenceLlmPlanner,
    build_evidence_planner_prompt,
    make_evidence_planner_from_settings,
)
from cerr_chatbot.query.example_bank import (
    EXAMPLES,
    PromptExample,
    select_examples,
)
from cerr_chatbot.query.executor import QueryResult, execute
from cerr_chatbot.query.llm_planner import (
    LlmPlanner,
    LlmPlannerError,
    TwoStageLlmPlanner,
    make_planner_from_settings,
)
from cerr_chatbot.query.metric_resolver import (
    FORBIDDEN_DERIVATIONS,
    METRIC_ALIASES,
    METRIC_TO_VIEW,
    ResolverHint,
    augment_schema_link,
    resolve,
)
from cerr_chatbot.query.narrator import (
    DeterministicNarrator,
    LlmNarrator,
    Narrator,
    build_narrator_prompt,
    make_narrator_from_settings,
)
from cerr_chatbot.query.narrator_safety import (
    DerivedCalc,
    EnvelopeParseError,
    NarratorEnvelope,
    extract_row_numbers,
    is_answer_grounded,
    parse_envelope,
    safe_eval_formula,
    verify_calculation,
)
from cerr_chatbot.query.pipeline import (
    EMPTY_QUESTION_RESPONSE,
    EvidencePipeline,
    LegacyPipeline,
    Pipeline,
    make_pipeline_from_settings,
)
from cerr_chatbot.query.planner_models import DecisionKind, PlannerDecision
from cerr_chatbot.query.planner_parser import (
    ALLOWED_KINDS,
    PlannerParseError,
    parse_planner_response,
)
from cerr_chatbot.query.planner_prompt import build_planner_prompt, build_sql_prompt
from cerr_chatbot.query.schema_linker import (
    ALLOWED_PATTERNS,
    SchemaLink,
    SchemaLinkParseError,
    build_schema_linking_prompt,
    parse_schema_linking_response,
)
from cerr_chatbot.query.semantic_catalog import (
    SEMANTIC_CATALOG,
    SemanticView,
    SemanticViewColumn,
)
from cerr_chatbot.query.service import (
    Planner,
    QueryService,
    QueryServiceResult,
    ServiceKind,
)
from cerr_chatbot.query.session_memory import (
    InMemorySessionMemoryStore,
    MemorySnapshot,
    SessionMemoryStore,
    build_snapshot_from_evidence_result,
)
from cerr_chatbot.query.sql_guard import (
    ALLOWED_VIEWS,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    SqlGuardError,
    ValidatedSql,
    validate,
)

__all__ = [
    "ALLOWED_KINDS",
    "ALLOWED_PATTERNS",
    "ALLOWED_VIEWS",
    "CAPABILITY_REPLY",
    "ConversationKind",
    "ConversationalResponse",
    "DEFAULT_LIMIT",
    "AnswerBrief",
    "AnswerType",
    "build_answer_brief",
    "render_brief_for_prompt",
    "DerivedCalc",
    "DeterministicNarrator",
    "EXAMPLES",
    "EnvelopeParseError",
    "EvidenceKind",
    "EMPTY_QUESTION_RESPONSE",
    "EvidenceLlmNarrator",
    "EvidenceLlmPlanner",
    "EvidencePack",
    "EvidencePipeline",
    "LegacyPipeline",
    "Pipeline",
    "build_evidence_planner_prompt",
    "make_evidence_planner_from_settings",
    "make_pipeline_from_settings",
    "EvidencePlanParseError",
    "EvidencePlanner",
    "EvidenceQueryResult",
    "EvidenceServiceResult",
    "GREETING_REPLY",
    "HELP_REPLY",
    "InMemorySessionMemoryStore",
    "MemorySnapshot",
    "SessionMemoryStore",
    "build_snapshot_from_evidence_result",
    "LlmNarrator",
    "MAX_CONTEXT_QUERIES",
    "Narrator",
    "NarratorEnvelope",
    "ParsedContextQuery",
    "ParsedEvidencePlan",
    "build_evidence_prompt",
    "evidence_ask",
    "extract_row_numbers",
    "is_answer_grounded",
    "parse_envelope",
    "parse_evidence_plan",
    "safe_eval_formula",
    "verify_calculation",
    "OUT_OF_SCOPE_REPLY",
    "build_narrator_prompt",
    "classify_intent",
    "make_narrator_from_settings",
    "FORBIDDEN_DERIVATIONS",
    "METRIC_ALIASES",
    "METRIC_TO_VIEW",
    "PromptExample",
    "ResolverHint",
    "augment_schema_link",
    "resolve",
    "SchemaLink",
    "SchemaLinkParseError",
    "build_schema_linking_prompt",
    "build_sql_prompt",
    "parse_schema_linking_response",
    "select_examples",
    "Answer",
    "DecisionKind",
    "LlmPlanner",
    "LlmPlannerError",
    "TwoStageLlmPlanner",
    "make_planner_from_settings",
    "MAX_LIMIT",
    "NULL_DISPLAY",
    "Planner",
    "PlannerDecision",
    "PlannerParseError",
    "QueryResult",
    "QueryService",
    "QueryServiceResult",
    "SEMANTIC_CATALOG",
    "SemanticView",
    "SemanticViewColumn",
    "ServiceKind",
    "SqlGuardError",
    "ValidatedSql",
    "build_planner_prompt",
    "compose_answer",
    "execute",
    "parse_planner_response",
    "validate",
]
