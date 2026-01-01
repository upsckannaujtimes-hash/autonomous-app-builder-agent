"""
Planning Engine - Analyzes prompts and creates execution plans
"""

import json
from typing import Dict, List, Any
from openai import OpenAI
import os


class PlanningEngine:
    """
    Autonomous planning engine that breaks down user prompts into actionable tasks
    """

    def __init__(self, model: str = "gpt-4-turbo"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def analyze_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Analyze user prompt and create comprehensive project plan

        Args:
            user_prompt: Natural language description of desired application

        Returns:
            Dictionary containing:
            - app_type: Type of application (web, api, mobile, etc.)
            - tech_stack: Recommended technologies
            - features: List of features to implement
            - tasks: Ordered list of implementation tasks
            - estimated_time: Estimated generation time
        """

        system_prompt = """You are an expert software architect. Analyze the user's request and create a detailed implementation plan.

Your response MUST be valid JSON with this structure:
{
  "app_type": "web_app|api|mobile_app|chrome_extension|cli_tool",
  "app_name": "suggested-app-name",
  "description": "Brief description",
  "tech_stack": {
    "frontend": "react|vue|svelte|next|none",
    "backend": "node|python|go|none",
    "database": "postgresql|mongodb|firebase|none",
    "styling": "tailwindcss|mui|chakra",
    "auth": "firebase|supabase|jwt|none"
  },
  "features": [
    "Feature 1",
    "Feature 2"
  ],
  "tasks": [
    {
      "id": 1,
      "name": "Task name",
      "description": "What to do",
      "files_to_create": ["file1.js", "file2.jsx"],
      "dependencies": []
    }
  ],
  "estimated_time_minutes": 5
}

Be specific and comprehensive."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        plan = json.loads(response.choices[0].message.content)
        return plan

    def decompose_tasks(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Further decompose tasks into granular subtasks
        """
        tasks = plan.get("tasks", [])
        decomposed = []

        for task in tasks:
            # Add file-level subtasks
            for file in task.get("files_to_create", []):
                decomposed.append(
                    {
                        "task_id": task["id"],
                        "type": "file_creation",
                        "target": file,
                        "description": f"Generate {file}",
                        "depends_on": task.get("dependencies", []),
                    }
                )

        return decomposed

    def validate_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Validate that plan is feasible and complete
        """
        required_fields = ["app_type", "tech_stack", "features", "tasks"]
        return all(field in plan for field in required_fields)
