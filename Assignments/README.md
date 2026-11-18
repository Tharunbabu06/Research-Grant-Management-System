# Assignments: fourteen supplied labs

These standard-library scripts and their original notebooks are preserved. No notebook output was fabricated or re-executed for this update. Scripts are the executable source; existing evidence is historical. Fresh `python Course-Project/tools/verify_labs.py` executes every script in an isolated temporary directory and applies its notebook terminal acceptance cell to captured output. These are trace assertions, not independent end-to-end application tests.

| Lab | Purpose / demonstrated behavior | Script | Notebook | Supporting historical evidence | Fresh assertions |
| --- | --- | --- | --- | --- | --- |
| 1 | Planning and revision | [Script](scripts/lab01_agent_vs_chatbot.py) | [Notebook](LAB_1_Worklet13_Agent_vs_Chatbot.ipynb) | [Trace](../Course-Project/evidence/lab1_artifacts/lab1_console_trace.txt) | 10/10 |
| 2 | Typed tools and financial validation | [Script](scripts/lab02_tool_using_agent.py) | [Notebook](LAB_2_Worklet13_Tool_Using_Agent.ipynb) | [Trace](../Course-Project/evidence/lab2_artifacts/lab2_console_trace.txt) | 10/10 |
| 3 | Reusable schema-typed skills | [Script](scripts/lab03_skill_creation.py) | [Notebook](LAB_3_Worklet13_Skill_Creation.ipynb) | [Trace](../Course-Project/evidence/lab3_artifacts/lab3_console_trace.txt) | 11/11 |
| 4 | Memory and scoped retrieval | [Script](scripts/lab04_memory_and_retrieval.py) | [Notebook](LAB_4_Worklet13_Memory_and_Retrieval.ipynb) | [Trace](../Course-Project/evidence/lab4_artifacts/lab4_console_trace.txt) | 8/8 |
| 5 | Governed connector | [Script](scripts/lab05_mcp_connector.py) | [Notebook](LAB_5_Worklet13_MCP_Connector.ipynb) | [Trace](../Course-Project/evidence/lab5_artifacts/lab5_console_trace.txt) | 10/10 |
| 6 | Runtime, audit and checkpoints | [Script](scripts/lab06_runtime.py) | [Notebook](LAB_6_Worklet13_Runtime.ipynb) | [Trace](../Course-Project/evidence/lab6_artifacts/lab6_console_trace.txt) | 10/10 |
| 7 | Executable state graph | [Script](scripts/lab07_agentic_node_graph.py) | [Notebook](LAB_7_Worklet13_Node_Graph.ipynb) | [Trace](../Course-Project/evidence/lab7_artifacts/lab7_console_trace.txt) | 10/10 |
| 8 | Parallel work and merge | [Script](scripts/lab08_parallel_swarm.py) | [Notebook](LAB_8_Worklet13_Parallel_Swarm.ipynb) | [Trace](../Course-Project/evidence/lab8_artifacts/lab8_console_trace.txt) | 10/10 |
| 9 | Source grounding and evidence | [Script](scripts/lab09_deep_research.py) | [Notebook](LAB_9_Worklet13_Deep_Research_Grounding.ipynb) | [Trace](../Course-Project/evidence/lab9_artifacts/lab9_console_trace.txt) | 10/10 |
| 10 | Diagnosis and bounded repair | [Script](scripts/lab10_ops_resilience.py) | [Notebook](LAB_10_Worklet13_Ops_Resilience.ipynb) | [Trace](../Course-Project/evidence/lab10_artifacts/lab10_console_trace.txt) | 11/11 |
| 11 | Acceptance-driven generation | [Script](scripts/lab11_sdlc_factory.py) | [Notebook](LAB_11_Worklet13_SDLC_Factory.ipynb) | [Trace](../Course-Project/evidence/lab11_artifacts/lab11_console_trace.txt) | 9/9 |
| 12 | Governance and versions | [Script](scripts/lab12_safety_governance.py) | [Notebook](LAB_12_Worklet13_Safety_and_Governance.ipynb) | [Trace](../Course-Project/evidence/lab12_artifacts/lab12_console_trace.txt) | 11/11 |
| 13 | Funding-profile specialists | [Script](scripts/lab13_discipline_specialists.py) | [Notebook](LAB_13_Worklet13_Domain_Specialists.ipynb) | [Trace](../Course-Project/evidence/lab13_artifacts/lab13_console_trace.txt) | 8/8 |
| 14 | Integrated capstone | [Script](scripts/lab14_capstone.py) | [Notebook](LAB_14_Worklet13_Capstone.ipynb) | [Trace](../Course-Project/evidence/lab14_artifacts/lab14_console_trace.txt) | 12/12 |

## Run and interpret

From repository root: `python Course-Project/tools/verify_labs.py` (Python 3.10+). Result: 140/140 trace assertions across 14 labs. Do not add these to backend or Python-app test totals. The Windows runner restores its working directory before temporary-directory cleanup.

Individual example: `python Assignments/scripts/lab01_agent_vs_chatbot.py`. Use a disposable current directory when a script emits artifacts. Optional notebook regeneration requires root requirements.txt and intentionally rewrites notebooks/evidence; it was not used here.

Lab 5 implements scoped MCP-style connector concepts, not a verified wire-protocol server. Lab 6 demonstrates runtime budgets/checkpoints, not an installed OpenClaw service. Lab 9 resolves evidence structure, not scientific truth. Lab 14 uses practice data, not a real funding submission.

[Earlier independent assignment programs](LEGACY_LABS.md) and their support/tests are retained in addition to this supplied set.
