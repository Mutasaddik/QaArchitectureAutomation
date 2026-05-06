from typing import Dict

QA_SYSTEM_PROMPT = """
You are an expert QA Engineer assistant with strong domain knowledge in ERP systems, microfinance, and financial applications.
Your role is to help generate complete, professional QA testing artifacts based on Change Requests, SRS documents, and historical knowledge.
Always be structured, clear, and actionable. Consider positive, negative, edge, and boundary cases.
"""

TEST_PLAN_PROMPT_TEMPLATE = """
You are generating a complete Test Plan for a new Change Request.

=== NEW CHANGE REQUEST ===
{cr_text}

=== KNOWLEDGE BASE CONTEXT ===
{context}

Generate a complete Test Plan with these sections:
1. CR SUMMARY - Title, Description, Impacted Modules, Dependencies
2. TEST STRATEGY - Smoke, Sanity, Regression, Integration, UAT scope
3. TEST SCOPE - In Scope and Out of Scope
4. RISK AREAS - High, Medium, Low risks
5. TEST ENVIRONMENT CONSIDERATIONS - Test data, known QA issues, preconditions
6. REQUIRED TEST DATA - Specific data, edge case data, user roles needed
7. ENTRY AND EXIT CRITERIA
8. ESTIMATED EFFORT - Test case count estimate, priority order
"""

TEST_CASE_PROMPT_TEMPLATE = """
You are generating detailed Test Cases for a Change Request.

=== NEW CHANGE REQUEST ===
{cr_text}

=== TEST PLAN SUMMARY ===
{test_plan_summary}

=== SIMILAR EXISTING TEST CASES ===
{existing_test_cases}

Generate test cases using this EXACT format for each test case:

FOLDER | NAME | PRECONDITION | STEPS | TEST DATA | EXPECTED RESULT | PRIORITY

Rules:
- FOLDER: module path like /OTC/Loan Management/Repayment
- NAME: start with Verify or Create
- PRECONDITION: semicolon-separated conditions
- STEPS: numbered like 1. Do this. 2. Do that.
- TEST DATA: specific values or N/A
- EXPECTED RESULT: clear expected outcome
- PRIORITY: High, Medium, or Low

Generate minimum 10 test cases covering positive, negative, edge cases.
"""

CHAT_PROMPT_TEMPLATE = """
You are a QA Assistant helping a QA Engineer.
The knowledge base context below contains REAL content extracted from uploaded CR and SRS PDF documents.
READ it carefully and use it to answer the question.

=== KNOWLEDGE BASE CONTEXT ===
{kb_context}

=== CR CONTEXT ===
{cr_context}

=== QUESTION ===
{user_question}

INSTRUCTIONS:
- Use the knowledge base context above to answer
- Be specific and reference actual content from the knowledge base
- Never say you have no information if the knowledge base context has relevant content
"""

CLARIFICATION_PROMPT_TEMPLATE = """
You are reviewing a Change Request for completeness before generating a test plan.

=== CHANGE REQUEST ===
{cr_text}

Analyze this CR and identify:
1. UNCLEAR REQUIREMENTS
2. MISSING INFORMATION
3. ASSUMPTIONS MADE
4. CLARIFICATION QUESTIONS
"""


def build_test_plan_prompt(cr_text: str, context: str) -> str:
    return TEST_PLAN_PROMPT_TEMPLATE.format(cr_text=cr_text, context=context)


def build_test_case_prompt(cr_text: str, test_plan_summary: str, existing_test_cases: str) -> str:
    return TEST_CASE_PROMPT_TEMPLATE.format(
        cr_text=cr_text,
        test_plan_summary=test_plan_summary,
        existing_test_cases=existing_test_cases
    )


def build_chat_prompt(cr_context: str, kb_context: str, chat_history: str, user_question: str) -> str:
    return CHAT_PROMPT_TEMPLATE.format(
        cr_context=cr_context,
        kb_context=kb_context,
        chat_history=chat_history,
        user_question=user_question
    )


def build_clarification_prompt(cr_text: str) -> str:
    return CLARIFICATION_PROMPT_TEMPLATE.format(cr_text=cr_text)


if __name__ == "__main__":
    prompt = build_chat_prompt("test cr", "test kb", "no history", "test question")
    print("Prompt built OK, length:", len(prompt))
