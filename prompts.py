TAMIL_SUBJECTS = {
    "tamil", "தமிழ்", "tamil language", "tamil literature",
    "தமிழ் இலக்கியம்", "தமிழ் மொழி"
}

def is_tamil_subject(subject: str) -> bool:
    """Returns True if the subject name (or code-name string) refers to Tamil."""
    s = subject.strip().lower()
    # Match full string or check if any known keyword appears in it
    if s in TAMIL_SUBJECTS:
        return True
    for keyword in ("tamil", "தமிழ்"):
        if keyword in s:
            return True
    return False

def tamil_language_instruction(subject: str, lang_pref: str = "tamil") -> str:
    """Returns a Tamil language block if subject is Tamil AND user chose Tamil.
    lang_pref: 'tamil' → generate in Tamil script
               'english' → generate in English (even for Tamil subject)
    """
    if is_tamil_subject(subject) and lang_pref == "tamil":
        return """
MULTI-LANGUAGE INSTRUCTION:
This is a Tamil language / literature subject. The student has chosen Tamil as the output language.
- Generate ALL content (summary, notes, questions, answers, MCQs) in TAMIL LANGUAGE (தமிழில்).
- Use proper Tamil script (Unicode). Do NOT transliterate into English letters.
- MCQ options, answers, and explanations must also be in Tamil.
- YouTube links must search in Tamil (add 'tamil' or 'தமிழ்' to query).
"""
    if is_tamil_subject(subject) and lang_pref == "english":
        return """
LANGUAGE INSTRUCTION:
This is a Tamil language / literature subject. The student has chosen English as the output language.
- Generate ALL content (summary, notes, questions, answers, MCQs) in ENGLISH.
- Keep subject-specific Tamil literary terms in Tamil script where necessary, but explain them in English.
"""
    return ""

def get_coding_instruction(subject: str) -> str:
    """Returns coding section prompt instruction unless subject is Tamil."""
    if is_tamil_subject(subject):
        return ""
    return """
[OPTIONAL CODING SECTION RULE]
Based on the Subject: {subject}
Decide if this is a technical/engineering/computing subject.
If YES (Highly Recommended for any CS/IT/ECE/EEE/Mechanical/Civil subject):
You MUST create a new heading:
## CODING EXAMPLES
Then provide VERY CONCISE core logic code in C and Python:
- C Implementation (CORE LOGIC ONLY, NO main function, NO headers)
- Python Implementation (CORE LOGIC ONLY)
- Algorithm (Brief step by step)
- Time and Space Complexity

If NO (e.g., Pure Language, Management, Arts):
DO NOT write the '## CODING EXAMPLES' heading.
"""

def get_mode_instruction(mode: str) -> str:
    if mode == "simplify":
        return """
[MODE: SIMPLIFY]
- Use very simple language and relatable analogies.
- Focus on the 'Why' and 'Core Idea' rather than complex math or theory.
- Use bullet points for readability.
- Explain technical terms using plain English.
- Keep sentences short.
"""
    return """
[MODE: DETAILED]
- Provide exhaustive technical depth and rigorous explanations.
- Include all relevant formulas, proofs, and mathematical models.
- Discuss edge cases and advanced theoretical implications.
- Use precise professional terminology.
- Compare with advanced state-of-the-art alternatives.
"""

def get_prompt(subject, topic, lang_pref="english", mode="detailed"):
    lang = tamil_language_instruction(subject, lang_pref)
    mode_inst = get_mode_instruction(mode)
    return f"""
You are an expert Anna University professor with 20 years of experience.
Generate HIGHLY {mode.upper()} and COMPREHENSIVE study material for exam preparation.
{lang}
{mode_inst}
Subject: {subject}
Topic: {topic}

IMPORTANT: Use EXACTLY these section headings. Generate maximum content for each section. 
- Use a highly structured layout with bullet points, numbered lists, and bold subheadings. 
- Avoid long blocks of text; break content into clear, logical points.
- Be extremely detailed and exhaustive.
    
## SUMMARY
Write an extensive 15-18 line summary covering:
- Exhaustive definition and deep concept of {topic}
- Core principles, governing laws, and properties
- Comprehensive types and classifications
- Wide range of real-world applications (at least 4)
- Critical importance in the context of {subject}
- Historical background and evolution
- [MODE SPECIFIC] Apply the {mode} tone here.

## SHORT NOTES
Write MASSIVE, high-depth detailed notes (minimum 50-60 lines) covering:
- Technical definition with complex examples
- All types and classifications with exhaustive sub-explanations
- Nuanced step-by-step working principle
- All relevant formulas, equations, and mathematical derivations
- Highly descriptive diagrams explanation (at least 2 diagrams)
- In-depth SWOT analysis (Advantages, Disadvantages, Opportunities, Threats)
- 5-7 distinct real-world applications with specific scenarios
- Expert-level comparison with at least 3 related concepts
- Detailed Time and space complexity analysis
- Dictionary of minimum 10 important terminologies
- Current trends and future scope of {topic}
- [DIAGRAMS] You MUST provide at least one complex technical diagram using Mermaid.js syntax. 
  Example: ```mermaid \n flowchart TD \n A[Start] --> B[End] \n ```
- [MODE SPECIFIC] Ensure the level of detail is PhD-level for {mode} mode.
{get_coding_instruction(subject).format(subject=subject, topic=topic)}

## MCQs
Generate 5 high-quality multiple choice questions. YOU MUST FOLLOW THIS FORMAT EXACTLY:
Q1. [Question Text]
a) [Option A]
b) [Option B]
c) [Option C]
d) [Option D]
Answer: [Option Letter, e.g., a]
Explanation: [Detailed explanation of why this answer is correct and why others are wrong]

## YOUTUBE LINKS
Generate exactly 5 clickable YouTube search links for this topic. Format them EXACTLY as markdown links:
- [Topic Name Tutorial](https://www.youtube.com/results?search_query=topic+name+tutorial)
"""

def get_prompt_with_pdf(subject, topic, pdf_text, lang_pref="english", mode="detailed"):
    lang = tamil_language_instruction(subject, lang_pref)
    mode_inst = get_mode_instruction(mode)
    return f"""
You are an expert Anna University professor with 20 years of experience.
Use the reference material below to generate HIGHLY {mode.upper()} study material.
{lang}
{mode_inst}
--- REFERENCE MATERIAL ---
{pdf_text}
--- END OF REFERENCE ---

Subject: {subject}
Topic: {topic}

IMPORTANT: Use EXACTLY these section headings. Generate maximum content. 
- Use a highly structured layout with bullet points, numbered lists, and bold subheadings. 
- Avoid long paragraphs; provide information in clear, actionable points.
- Be extremely exhaustive.

## SUMMARY
Write an extensive 15-18 line summary based on the reference covering:
- Deep definition and concept of {topic}
- All key principles extracted from the reference
- Full spectrum of types and classifications mentioned
- Detailed applications discussed in reference
- Critical points and nuances highlighted by the author
- [MODE SPECIFIC] Apply the {mode} tone based on the reference data.

## SHORT NOTES
Write MASSIVE, high-depth detailed notes based on reference (minimum 50-60 lines):
- Technical definition with reference-specific examples
- Detailed breakdown of all types and classifications
- Exhaustive step-by-step working principle
- All formulas, equations, and derivations from the reference
- Detailed description of all diagrams/figures in the reference
- Advantages and disadvantages mentioned or implied
- All real-world applications found in the material
- Advanced comparison with related concepts
- Complexity analysis if applicable
- Full glossary of terminologies from the reference
- [DIAGRAMS] You MUST provide at least one complex technical diagram using Mermaid.js syntax based on the reference.
  Example: ```mermaid \n flowchart TD \n A[Start] --> B[End] \n ```
- [MODE SPECIFIC] PHD-level detail matching {mode} mode.
{get_coding_instruction(subject).format(subject=subject, topic=topic)}

## MCQs
Generate 5 MCQs based on reference. YOU MUST FOLLOW THIS FORMAT EXACTLY:
Q1. [Question Text]
a) [Option A]
b) [Option B]
c) [Option C]
d) [Option D]
Answer: [Option Letter, e.g., a]
Explanation: [Detailed explanation of the correct logic based on the reference]

## YOUTUBE LINKS
Generate exactly 5 clickable YouTube search links for explaining concepts in this reference. Format them EXACTLY as markdown links:
- [Reference Concept Tutorial](https://www.youtube.com/results?search_query=reference+concept+tutorial)
"""

def get_pyq_from_pdf(subject, topic, pyq_text, lang_pref="english"):
    lang = tamil_language_instruction(subject, lang_pref)
    return f"""
You are an expert Anna University professor.
The following is content from a previous year question paper.
{lang}
--- PREVIOUS YEAR QUESTION PAPER ---
{pyq_text}
--- END ---

Subject: {subject}
Topic: {topic}

Part-A
[INSTRUCTION: List all 2 mark questions with brief answers.]

Part-B
[INSTRUCTION: List all 13 mark questions with detailed answers.]

Part-C
[INSTRUCTION: List all 15 mark questions with detailed answers.]

Important Topics from QP:
List all repeated and important topics found.
"""

def get_blooms_prompt(subject, topic, lang_pref="english", mode="detailed"):
    lang = tamil_language_instruction(subject, lang_pref)
    mode_inst = get_mode_instruction(mode)
    return f"""
You are an expert Anna University professor.
Generate questions based on Bloom's Taxonomy (all 6 levels) for:
{lang}
{mode_inst}
Subject: {subject}
Topic: {topic}

IMPORTANT RULES:
- Use EXACTLY the headings below (e.g., ## REMEMBER).
- Generate EXACTLY 3 questions per level, each with a short answer.
- Use the CORRECT cognitive verb for each level.
- Format each question as "Q1. [Question]" and answer as "Answer: [Answer]".

## REMEMBER
(Use verbs: Define, List, State, Recall, Name, Identify)
1. Define {topic} and state its key characteristics.
   Answer: [concise factual answer]
2. List the main types/components of {topic}.
   Answer: [concise factual answer]
3. State any two important properties or rules related to {topic}.
   Answer: [concise factual answer]

## UNDERSTAND
(Use verbs: Explain, Describe, Summarize, Interpret, Classify, Paraphrase)
1. Explain how {topic} works in simple terms.
   Answer: [descriptive answer showing conceptual understanding]
2. Describe the relationship between {topic} and a related concept in {subject}.
   Answer: [descriptive answer]
3. Summarize the importance of {topic} in {subject}.
   Answer: [summary answer]

## APPLY
(Use verbs: Solve, Use, Implement, Demonstrate, Calculate, Execute)
1. Solve a simple problem using {topic} with a step-by-step example.
   Answer: [worked example with steps]
2. Demonstrate how {topic} is applied in a real-world scenario.
   Answer: [practical application answer]
3. Use {topic} to implement or calculate a small example relevant to {subject}.
   Answer: [step-by-step solution]

## ANALYZE
(Use verbs: Compare, Differentiate, Examine, Break down, Contrast, Investigate)
1. Compare {topic} with another related concept in {subject}. Highlight key differences.
   Answer: [comparison with differences table or points]
2. Examine the advantages and disadvantages of {topic}.
   Answer: [analysis of pros and cons]
3. Break down the internal working/structure of {topic} and explain each part.
   Answer: [detailed breakdown]

## EVALUATE
(Use verbs: Justify, Assess, Critique, Judge, Recommend, Defend)
1. Justify why {topic} is preferred over alternatives in specific situations.
   Answer: [reasoned justification with examples]
2. Assess the limitations and challenges of {topic} in real-world use.
   Answer: [critical evaluation]
3. Critique the efficiency or performance of {topic} and recommend improvements.
   Answer: [informed critique with suggestion]

## CREATE
(Use verbs: Design, Construct, Develop, Formulate, Propose, Build)
1. Design a system or algorithm using {topic} for a real-world application.
   Answer: [design steps and rationale]
2. Propose a new approach or improvement to {topic} based on its current limitations.
   Answer: [creative solution with explanation]
3. Develop a simple project or use case that uses {topic} as its core component.
   Answer: [project description with components]

Make all questions highly relevant to Anna University BE/BTech {subject} exam.
Generate actual detailed questions and answers, not placeholders.
"""

def get_important_questions_prompt(subject, topic, lang_pref="english", mode="detailed"):
    lang = tamil_language_instruction(subject, lang_pref)
    mode_inst = get_mode_instruction(mode)
    if is_tamil_subject(subject):
        part_b_c = f"""
**Part-B**
[INSTRUCTION: Generate 3 questions. Each answer MUST be detailed and clear. Cover: definition, historical context, core principles, variations, and cultural importance.]

Q1. Explain {topic} in detail with suitable examples.
Answer:
[WRITE A DETAILED ANSWER. Provide an introduction. Explain the main concept clearly. Give practical examples. State its historical or cultural importance.]

Q2. Describe the variations and key themes of {topic}.
Answer:
[WRITE A DETAILED ANSWER. Discuss the structure or variations. Include relevant literature or linguistic context.]

Q3. Discuss the significance of {topic} in detail.
Answer:
[WRITE A DETAILED ANSWER. Discuss its impact, cultural value, and usage in classical or modern contexts.]

**Part-C**
[INSTRUCTION: Generate 2 questions. Each answer MUST be an extensive essay. Cover: deep themes, historical evolution, and comprehensive analysis.]

Q1. Elaborate on {topic} covering its origin, textual evidence, cultural significance, and modern relevance.
Answer:
[WRITE AN EXTENSIVE ESSAY. Section 1: Introduction. Section 2: Core Analysis. Section 3: Detailed examples. Section 4: Modern relevance. Conclusion.]

Q2. Critically analyze {topic}. Discuss themes and context with prominent examples.
Answer:
[WRITE AN EXTENSIVE ESSAY. Section 1: Overview. Section 2: Critical thematic analysis. Section 3: Deep dive into examples. Conclusion.]
"""
    else:
        part_b_c = f"""
**Part-B**
[INSTRUCTION: Generate 3 questions. Each answer MUST be at least 20-25 lines long. Cover: definition, all types with full explanation, step-by-step working, labeled diagram description, formulas/algorithms, advantages, disadvantages, real-world applications, comparison with related concept.]

Q1. Explain {topic} in detail with neat diagram and suitable examples.
Answer:
[WRITE AT LEAST 20 LINES. Start with definition. Cover all types/categories with explanation. Describe the working step by step. Describe what the diagram shows. Mention at least 3 real-world applications. List advantages and disadvantages. Conclude with its importance.]

Q2. Describe the types of {topic} with working principle and examples.
Answer:
[WRITE AT LEAST 20 LINES. List and explain each type in detail. For each type: give definition, working mechanism, example. Include a comparison table. Describe real-world use cases for each type.]

Q3. Compare {topic} with related concepts. Discuss advantages and applications.
Answer:
[WRITE AT LEAST 18 LINES. Write a paragraph comparison. Include a comparison table with at least 5 parameters. Discuss when to use which. List advantages and disadvantages of each. Give practical examples.]

**Part-C**
[INSTRUCTION: Generate 2 questions. Each answer MUST be at least 30 lines long. Cover: deep theory, implementation details, multiple case studies, limitations, future scope.]

Q1. Elaborate on {topic} covering theory, implementation, real-world applications, and future scope.
Answer:
[WRITE AT LEAST 30 LINES. Section 1: Deep theoretical background. Section 2: How it is implemented/used in practice. Section 3: Minimum 3 detailed real-world case studies or applications with explanation. Section 4: Limitations and challenges. Section 5: Future scope and improvements. Conclusion.]

Q2. Critically analyze {topic}. Compare approaches, evaluate trade-offs, and justify with examples.
Answer:
[WRITE AT LEAST 30 LINES. Section 1: Overview of the concept and its importance. Section 2: Different approaches/techniques used. Section 3: Detailed comparison of approaches with a table. Section 4: Trade-off analysis (time, space, cost, complexity). Section 5: Justify the best approach with real examples. Section 6: Critical limitations and open problems. Conclusion.]
"""

    return f"""
You are an expert Anna University professor with 20 years of experience.
Generate HIGHLY {mode.upper()} Anna University exam questions with COMPREHENSIVE answers for:
{lang}
{mode_inst}
Subject: {subject}
Topic: {topic}

Use EXACTLY these section headings.
- IMPORTANT: Wrap every question in [QUESTION] tags (e.g. [QUESTION] Q1. What is...? [QUESTION]). 
- Do NOT use bolding or extra markdown inside the tags.

## IMPORTANT QUESTIONS

**Part-A**
[INSTRUCTION: Generate 5 questions here.]

Q1. [Write a define/state/list type question on {topic}]
Answer: [Precise answer with key terms]

Q2. [Write a difference/compare short question on {topic}]
Answer: [Precise answer]

Q3. [Write a what/why type question on {topic}]
Answer: [Precise answer]

Q4. [Write a short note type question on {topic}]
Answer: [Precise answer]

Q5. [Write an application/example question on {topic}]
Answer: [Precise answer]

{part_b_c}
"""