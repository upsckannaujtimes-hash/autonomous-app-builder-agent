#!/usr/bin/env python3
"""
Autonomous App Builder Agent - Main Entry Point

Usage:
    python agent.py "Build a todo app with React and Firebase"
"""

import sys
import os
import time
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.planning_engine import PlanningEngine
from agent.code_generator import CodeGenerator
from agent.testing_agent import TestingAgent
from agent.deployment_agent import DeploymentAgent

console = Console()


class AutonomousAppBuilder:
    """
    Main orchestrator for autonomous app building
    """

    def __init__(self, output_dir: str = "./generated_apps"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Initialize agent components
        self.planner = PlanningEngine()
        self.code_gen = CodeGenerator()
        self.tester = TestingAgent()
        self.deployer = DeploymentAgent()

        console.print(
            Panel.fit(
                "[bold cyan]🤖 Autonomous App Builder Agent[/bold cyan]\n"
                "[dim]Give me one prompt, I'll build your app[/dim]",
                border_style="cyan",
            )
        )

    def build(self, user_prompt: str) -> dict:
        """
        Main build pipeline - fully autonomous

        Args:
            user_prompt: User's natural language request

        Returns:
            Build result with deployment URLs and stats
        """

        start_time = time.time()

        try:
            # Step 1: Planning
            console.print("\n[bold]📋 Step 1: Analyzing & Planning[/bold]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Analyzing your request...", total=None)
                plan = self.planner.analyze_prompt(user_prompt)
                progress.update(task, description="✓ Plan created")

            console.print(f"\n[green]✓[/green] Project: {plan['app_name']}")
            console.print(f"[green]✓[/green] Type: {plan['app_type']}")
            console.print(
                f"[green]✓[/green] Tech: {plan['tech_stack']['frontend']} + {plan['tech_stack']['backend']}"
            )
            console.print(f"[green]✓[/green] Features: {len(plan['features'])}")
            console.print(
                f"[green]✓[/green] Estimated time: {plan.get('estimated_time_minutes', 5)} minutes"
            )

            # Step 2: Code Generation
            console.print("\n[bold]💻 Step 2: Generating Code[/bold]")
            app_dir = self.output_dir / plan["app_name"]
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Writing code...", total=None)
                generated_files = self.code_gen.generate_app(plan, str(app_dir))
                progress.update(
                    task, description=f"✓ Generated {len(generated_files)} files"
                )

            console.print(
                f"\n[green]✓[/green] Created {len(generated_files)} files in {app_dir}"
            )

            # Step 3: Testing
            console.print("\n[bold]🧪 Step 3: Testing[/bold]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Running tests...", total=None)
                test_results = self.tester.generate_and_run_tests(plan, str(app_dir))
                progress.update(
                    task,
                    description=f"✓ {test_results['passed']}/{test_results['total']} tests passed",
                )

            if test_results["passed"] == test_results["total"]:
                console.print("[green]✓ All tests passing![/green]")
            else:
                console.print(
                    f"[yellow]⚠ {test_results['failed']} tests failed[/yellow]"
                )

            # Step 4: Deployment
            console.print("\n[bold]🚀 Step 4: Deploying[/bold]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Deploying to cloud...", total=None)
                deployment = self.deployer.deploy(plan, str(app_dir))
                progress.update(task, description="✓ Deployed successfully")

            # Final Summary
            elapsed_time = time.time() - start_time
            console.print(
                Panel.fit(
                    f"[bold green]🎉 App Successfully Built![/bold green]\n\n"
                    f"[cyan]📱 Live URL:[/cyan] {deployment['url']}\n"
                    f"[cyan]📁 Source Code:[/cyan] {deployment['github_url']}\n"
                    f"[cyan]⏱️ Total Time:[/cyan] {elapsed_time:.1f}s\n"
                    f"[cyan]📊 Files Created:[/cyan] {len(generated_files)}\n"
                    f"[cyan]✅ Tests Passed:[/cyan] {test_results['passed']}/{test_results['total']}",
                    border_style="green",
                    title="Success",
                )
            )

            return {
                "success": True,
                "plan": plan,
                "app_dir": str(app_dir),
                "deployment_url": deployment["url"],
                "github_url": deployment["github_url"],
                "elapsed_time": elapsed_time,
                "files_created": len(generated_files),
                "tests_passed": test_results["passed"],
            }

        except Exception as e:
            console.print(f"\n[bold red]❌ Error:[/bold red] {str(e)}")
            return {"success": False, "error": str(e)}


def main():
    """CLI Entry Point"""
    if len(sys.argv) < 2:
        console.print("[red]Usage:[/red] python agent.py \"Your app description\"")
        console.print("\n[yellow]Examples:[/yellow]")
        console.print(
            '  python agent.py "Build a todo app with React and Firebase auth"'
        )
        console.print('  python agent.py "Create a REST API for a bookstore"')
        console.print(
            '  python agent.py "Build an e-commerce site with Stripe integration"'
        )
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])

    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        console.print(
            "[red]Error:[/red] OPENAI_API_KEY not found in environment variables"
        )
        console.print("[yellow]Set it with:[/yellow] export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    agent = AutonomousAppBuilder()
    result = agent.build(user_prompt)

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
