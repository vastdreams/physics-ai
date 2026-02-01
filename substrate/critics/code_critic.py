# PATH: substrate/critics/code_critic.py
# PURPOSE:
#   - Analyzes code for bugs, inefficiencies, and improvements
#   - Focuses on implementation, not physics
#   - Proposes code changes for evolution
#
# ROLE IN ARCHITECTURE:
#   - Second-line critic in the audit stack
#   - Focuses on code quality and correctness
#
# MAIN EXPORTS:
#   - CodeCritic: Main critic class
#
# NON-RESPONSIBILITIES:
#   - Does NOT analyze physics logic (that's LogicCritic)
#   - Does NOT apply changes (that's evolution)
#
# NOTES FOR FUTURE AI:
#   - Use AST analysis for structural issues
#   - Use LLM for semantic issues
#   - Propose concrete patches, not vague suggestions

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import json
import ast
import uuid
import os
import re

from substrate.critics.local_llm import LocalLLMBackend, LLMResponse
from substrate.memory.reasoning_trace import ReasoningTrace, CriticAnnotation


@dataclass
class CodeIssue:
    """An issue found in code."""
    
    issue_type: str  # "bug", "inefficiency", "style", "duplication", etc.
    severity: str    # "info", "warning", "error", "critical"
    message: str
    
    # Location
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    
    # The problematic code
    code_snippet: str = ""
    
    # Evidence and confidence
    evidence: str = ""
    confidence: float = 1.0
    
    # Suggested fix
    suggestion: Optional[str] = None
    suggested_code: Optional[str] = None
    
    def to_annotation(self, critic_id: str) -> CriticAnnotation:
        """Convert to CriticAnnotation."""
        return CriticAnnotation(
            critic_id=critic_id,
            critic_type="code",
            step_ids=[],
            issue_type=self.issue_type,
            severity=self.severity,
            message=f"{self.file_path}:{self.line_number}: {self.message}" if self.file_path else self.message,
            suggestion=self.suggestion,
            suggested_fix={"code": self.suggested_code} if self.suggested_code else None,
            confidence=self.confidence,
        )


@dataclass
class CodePatch:
    """A proposed code change."""
    
    file_path: str
    
    # What to change
    old_code: str
    new_code: str
    
    # Location (optional, for context)
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    
    # Rationale
    reason: str = ""
    issue_type: str = ""
    
    # Assessment
    confidence: float = 1.0
    risk: str = "low"  # "low", "medium", "high"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "old_code": self.old_code,
            "new_code": self.new_code,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "reason": self.reason,
            "issue_type": self.issue_type,
            "confidence": self.confidence,
            "risk": self.risk,
        }


class CodeCritic:
    """
    Critic that analyzes code for bugs and improvements.
    
    Uses:
    - AST analysis for structural issues
    - LLM analysis for semantic issues
    - Pattern matching for common anti-patterns
    """
    
    def __init__(
        self,
        llm_backend: LocalLLMBackend,
        codebase_root: str = ".",
        critic_id: Optional[str] = None
    ):
        self.llm = llm_backend
        self.codebase_root = codebase_root
        self.critic_id = critic_id or f"code_critic_{uuid.uuid4().hex[:8]}"
        self._analysis_count = 0
    
    def analyze_file(
        self,
        file_path: str,
        check_types: Optional[Set[str]] = None
    ) -> List[CodeIssue]:
        """
        Analyze a single file for code issues.
        
        Args:
            file_path: Path to the file
            check_types: Which checks to run
            
        Returns:
            List of CodeIssues found
        """
        self._analysis_count += 1
        issues = []
        
        check_types = check_types or {
            "syntax", "complexity", "style", "bugs", "performance", "llm"
        }
        
        # Read file
        try:
            full_path = os.path.join(self.codebase_root, file_path)
            with open(full_path) as f:
                code = f.read()
        except Exception as e:
            issues.append(CodeIssue(
                issue_type="file_error",
                severity="error",
                message=f"Could not read file: {e}",
                file_path=file_path,
            ))
            return issues
        
        # Programmatic checks
        if "syntax" in check_types:
            issues.extend(self._check_syntax(code, file_path))
        
        if "complexity" in check_types:
            issues.extend(self._check_complexity(code, file_path))
        
        if "style" in check_types:
            issues.extend(self._check_style(code, file_path))
        
        if "bugs" in check_types:
            issues.extend(self._check_common_bugs(code, file_path))
        
        if "performance" in check_types:
            issues.extend(self._check_performance(code, file_path))
        
        # LLM analysis
        if "llm" in check_types:
            issues.extend(self._llm_analysis(code, file_path))
        
        return issues
    
    def analyze_function(
        self,
        code: str,
        function_name: str,
        context: Optional[str] = None
    ) -> Tuple[List[CodeIssue], List[CodePatch]]:
        """
        Analyze a specific function for issues and suggest patches.
        
        Args:
            code: The function code
            function_name: Name of the function
            context: Additional context (what the function should do)
            
        Returns:
            Tuple of (issues, patches)
        """
        issues = []
        patches = []
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            issues.append(CodeIssue(
                issue_type="syntax_error",
                severity="error",
                message=f"Syntax error: {e}",
                function_name=function_name,
                code_snippet=code[:200],
            ))
            return issues, patches
        
        # Check function-specific issues
        issues.extend(self._check_function_complexity(tree, code, function_name))
        issues.extend(self._check_function_bugs(tree, code, function_name))
        
        # LLM analysis for improvements
        llm_result = self._llm_function_analysis(code, function_name, context)
        issues.extend(llm_result[0])
        patches.extend(llm_result[1])
        
        return issues, patches
    
    def propose_patches(
        self,
        issues: List[CodeIssue],
        file_path: str,
        code: str
    ) -> List[CodePatch]:
        """
        Generate patches to fix issues.
        
        Args:
            issues: Issues to fix
            file_path: Path to the file
            code: Current code
            
        Returns:
            List of proposed patches
        """
        if not issues:
            return []
        
        # Build prompt
        issues_desc = "\n".join([
            f"- [{i.severity}] {i.issue_type}: {i.message}"
            + (f"\n  Code: {i.code_snippet[:100]}" if i.code_snippet else "")
            for i in issues
        ])
        
        prompt = f"""Given these issues in Python code:

{issues_desc}

Original code:
```python
{code[:2000]}  # Truncated for brevity
```

Generate patches to fix these issues. For each patch, provide:
1. The exact old code to replace
2. The new code
3. Brief explanation

Respond with JSON:
{{
    "patches": [
        {{
            "old_code": "exact code to replace",
            "new_code": "replacement code",
            "reason": "why this fixes the issue",
            "issue_type": "which issue this fixes"
        }}
    ]
}}"""

        response = self.llm.generate(
            prompt,
            system_prompt="You are an expert Python developer fixing code issues. Provide exact, minimal patches.",
        )
        
        patches = []
        try:
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            data = json.loads(text)
            
            for p in data.get("patches", []):
                if p.get("old_code") and p.get("new_code"):
                    patches.append(CodePatch(
                        file_path=file_path,
                        old_code=p["old_code"],
                        new_code=p["new_code"],
                        reason=p.get("reason", ""),
                        issue_type=p.get("issue_type", ""),
                        confidence=0.7,  # LLM-generated patches get lower confidence
                    ))
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        
        return patches
    
    def _check_syntax(self, code: str, file_path: str) -> List[CodeIssue]:
        """Check for syntax errors."""
        issues = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(CodeIssue(
                issue_type="syntax_error",
                severity="error",
                message=str(e),
                file_path=file_path,
                line_number=e.lineno,
                confidence=1.0,
            ))
        
        return issues
    
    def _check_complexity(self, code: str, file_path: str) -> List[CodeIssue]:
        """Check for overly complex code."""
        issues = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count complexity indicators
                complexity = self._compute_cyclomatic(node)
                
                if complexity > 15:
                    issues.append(CodeIssue(
                        issue_type="high_complexity",
                        severity="warning",
                        message=f"Function {node.name} has high cyclomatic complexity ({complexity})",
                        file_path=file_path,
                        line_number=node.lineno,
                        function_name=node.name,
                        suggestion="Consider breaking into smaller functions",
                    ))
                
                # Check nesting depth
                max_depth = self._compute_max_depth(node)
                if max_depth > 5:
                    issues.append(CodeIssue(
                        issue_type="deep_nesting",
                        severity="warning",
                        message=f"Function {node.name} has deep nesting ({max_depth} levels)",
                        file_path=file_path,
                        line_number=node.lineno,
                        function_name=node.name,
                        suggestion="Consider early returns or extracting nested logic",
                    ))
        
        return issues
    
    def _compute_cyclomatic(self, node: ast.AST) -> int:
        """Compute cyclomatic complexity of a function."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _compute_max_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Compute maximum nesting depth."""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                child_depth = self._compute_max_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._compute_max_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _check_style(self, code: str, file_path: str) -> List[CodeIssue]:
        """Check for style issues."""
        issues = []
        lines = code.split("\n")
        
        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 120:
                issues.append(CodeIssue(
                    issue_type="line_too_long",
                    severity="info",
                    message=f"Line exceeds 120 characters ({len(line)})",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line[:80] + "...",
                ))
            
            # Trailing whitespace
            if line.rstrip() != line and line.strip():
                issues.append(CodeIssue(
                    issue_type="trailing_whitespace",
                    severity="info",
                    message="Line has trailing whitespace",
                    file_path=file_path,
                    line_number=i,
                ))
        
        return issues
    
    def _check_common_bugs(self, code: str, file_path: str) -> List[CodeIssue]:
        """Check for common bug patterns."""
        issues = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues
        
        for node in ast.walk(tree):
            # Mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults + node.args.kw_defaults:
                    if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(CodeIssue(
                            issue_type="mutable_default",
                            severity="warning",
                            message=f"Function {node.name} has mutable default argument",
                            file_path=file_path,
                            line_number=node.lineno,
                            function_name=node.name,
                            suggestion="Use None as default and initialize in function body",
                            confidence=1.0,
                        ))
            
            # Bare except
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(CodeIssue(
                    issue_type="bare_except",
                    severity="warning",
                    message="Bare except clause catches all exceptions including SystemExit",
                    file_path=file_path,
                    line_number=node.lineno,
                    suggestion="Catch specific exceptions or at least Exception",
                    confidence=1.0,
                ))
            
            # Comparison to None using ==
            if isinstance(node, ast.Compare):
                for op, comp in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(comp, ast.Constant) and comp.value is None:
                        issues.append(CodeIssue(
                            issue_type="none_comparison",
                            severity="info",
                            message="Use 'is None' or 'is not None' for None comparisons",
                            file_path=file_path,
                            line_number=node.lineno,
                            confidence=1.0,
                        ))
        
        return issues
    
    def _check_performance(self, code: str, file_path: str) -> List[CodeIssue]:
        """Check for performance issues."""
        issues = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues
        
        for node in ast.walk(tree):
            # String concatenation in loop
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            issues.append(CodeIssue(
                                issue_type="string_concat_loop",
                                severity="info",
                                message="Possible string concatenation in loop - consider using list.join()",
                                file_path=file_path,
                                line_number=child.lineno,
                                confidence=0.6,
                            ))
        
        return issues
    
    def _check_function_complexity(
        self,
        tree: ast.AST,
        code: str,
        function_name: str
    ) -> List[CodeIssue]:
        """Check complexity of a specific function."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                complexity = self._compute_cyclomatic(node)
                if complexity > 10:
                    issues.append(CodeIssue(
                        issue_type="function_too_complex",
                        severity="warning",
                        message=f"Function has cyclomatic complexity of {complexity}",
                        function_name=function_name,
                        suggestion="Break into smaller, focused functions",
                    ))
                
                # Count lines
                lines = code.split("\n")
                if len(lines) > 50:
                    issues.append(CodeIssue(
                        issue_type="function_too_long",
                        severity="info",
                        message=f"Function has {len(lines)} lines",
                        function_name=function_name,
                        suggestion="Consider extracting helper functions",
                    ))
        
        return issues
    
    def _check_function_bugs(
        self,
        tree: ast.AST,
        code: str,
        function_name: str
    ) -> List[CodeIssue]:
        """Check for bugs in a specific function."""
        issues = []
        
        # Check for unused variables
        assigned_names = set()
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    assigned_names.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
        
        unused = assigned_names - used_names - {"_", "__"}
        for name in unused:
            if not name.startswith("_"):
                issues.append(CodeIssue(
                    issue_type="unused_variable",
                    severity="info",
                    message=f"Variable '{name}' is assigned but never used",
                    function_name=function_name,
                    confidence=0.9,
                ))
        
        return issues
    
    def _llm_analysis(self, code: str, file_path: str) -> List[CodeIssue]:
        """Use LLM to analyze code."""
        issues = []
        
        # Truncate very long files
        if len(code) > 5000:
            code = code[:5000] + "\n# ... (truncated)"
        
        prompt = f"""Analyze this Python code for bugs, inefficiencies, or improvements.

File: {file_path}

```python
{code}
```

Focus on:
1. Logic errors or bugs
2. Performance issues
3. Security concerns
4. Maintainability problems

Respond with JSON:
{{
    "issues": [
        {{
            "type": "bug|performance|security|maintainability",
            "severity": "info|warning|error",
            "message": "description",
            "line": line_number_or_null,
            "suggestion": "how to fix"
        }}
    ]
}}

If no significant issues, return {{"issues": []}}"""

        response = self.llm.generate(
            prompt,
            system_prompt="You are an expert Python code reviewer. Be precise and actionable.",
        )
        
        try:
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            data = json.loads(text)
            
            for issue in data.get("issues", []):
                issues.append(CodeIssue(
                    issue_type=issue.get("type", "llm_detected"),
                    severity=issue.get("severity", "warning"),
                    message=issue.get("message", ""),
                    file_path=file_path,
                    line_number=issue.get("line"),
                    suggestion=issue.get("suggestion"),
                    confidence=0.6,  # LLM issues get lower confidence
                ))
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        
        return issues
    
    def _llm_function_analysis(
        self,
        code: str,
        function_name: str,
        context: Optional[str]
    ) -> Tuple[List[CodeIssue], List[CodePatch]]:
        """Use LLM to analyze a function and suggest improvements."""
        issues = []
        patches = []
        
        prompt = f"""Analyze and improve this Python function:

```python
{code}
```

{f"Context: {context}" if context else ""}

Provide:
1. Any bugs or issues found
2. Suggested improvements with exact code changes

Respond with JSON:
{{
    "issues": [
        {{"type": "string", "severity": "string", "message": "string"}}
    ],
    "improvements": [
        {{
            "old_code": "exact code to replace",
            "new_code": "improved code",
            "reason": "why this is better"
        }}
    ]
}}"""

        response = self.llm.generate(
            prompt,
            system_prompt="You are an expert Python developer. Provide exact, minimal changes.",
        )
        
        try:
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            data = json.loads(text)
            
            for issue in data.get("issues", []):
                issues.append(CodeIssue(
                    issue_type=issue.get("type", "llm_detected"),
                    severity=issue.get("severity", "warning"),
                    message=issue.get("message", ""),
                    function_name=function_name,
                    confidence=0.6,
                ))
            
            for imp in data.get("improvements", []):
                if imp.get("old_code") and imp.get("new_code"):
                    patches.append(CodePatch(
                        file_path="",  # Unknown at this point
                        old_code=imp["old_code"],
                        new_code=imp["new_code"],
                        reason=imp.get("reason", ""),
                        confidence=0.6,
                    ))
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        
        return issues, patches
    
    def statistics(self) -> Dict[str, Any]:
        """Get critic statistics."""
        return {
            "critic_id": self.critic_id,
            "analysis_count": self._analysis_count,
            "llm_stats": self.llm.statistics(),
        }

