"""
Prompt templates for the Software Architecture Workbench.
Single-shot design: one LLM call returns the complete analysis as JSON.
"""

SYSTEM_ARCHITECT = """You are a principal software architect. 
Analyze user requirements and respond ONLY with a single valid JSON object — no markdown, no prose, no explanation outside the JSON.
Your output must be pure JSON that can be passed directly to json.loads()."""


def prompt_full_analysis(requirements: str) -> str:
    return f"""Analyze these system requirements and return a single JSON object with exactly these keys:

{{
  "functional_requirements": ["req1", "req2", ...],
  "non_functional_requirements": ["perf", "scalability", ...],
  "domain": "e-commerce | healthcare | fintech | education | ...",
  "stakeholders": ["end-users", "admins", ...],
  "quality_attributes": ["availability", "scalability", "security", ...],
  "recommended_style": "Microservices | SOA | Layered | Event-Driven | Serverless | Monolith",
  "architecture_rationale": "Why this style fits the requirements in 2-3 sentences",
  "scalability_tactics": ["Horizontal scaling", "Caching", "Data partitioning", ...],
  "availability_tactics": ["Active redundancy", "Health checks", "ACID transactions", ...],
  "security_tactics": ["OAuth2", "Rate limiting", "Encryption at rest", ...],
  "components": [
    {{"name": "API Gateway", "role": "Entry point, routing, auth", "technology": "Nginx / Kong"}},
    {{"name": "User Service", "role": "User management", "technology": "Node.js / FastAPI"}},
    ...
  ],
  "mermaid_diagram": "graph TD\\n  Client-->APIGateway\\n  APIGateway-->UserService\\n  ...",
  "deployment_recommendation": "Kubernetes on AWS EKS with auto-scaling",
  "tech_stack": {{
    "frontend": "React / Next.js",
    "backend": "FastAPI / Node.js",
    "database": "PostgreSQL + Redis",
    "messaging": "Kafka / RabbitMQ",
    "devops": "Docker, Kubernetes, GitHub Actions"
  }},
  "risk_assessment": ["Single point of failure at API Gateway", "Data consistency challenges", ...]
}}

Keep mermaid_diagram as a valid Mermaid flowchart (graph TD) using escaped newlines (\\n).
Use at least 6 components in the architecture.

REQUIREMENTS:
{requirements}"""
