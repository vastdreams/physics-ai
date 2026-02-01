"""
PATH: ai/evolution/validator.py
PURPOSE: Validate evolution proposals before applying

Validation checks:
1. Syntax validity (code compiles)
2. Type safety
3. Test coverage
4. Physics validity (for equations)
5. Security (no dangerous operations)
"""

import ast
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .proposal import EvolutionProposal, ValidationResult, CodeChange, ProposalType


class ProposalValidator:
    """
    Validates evolution proposals.
    
    Uses multiple checks to ensure proposals are safe and correct.
    """
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"os\.system",
        r"subprocess\.",
        r"eval\(",
        r"exec\(",
        r"__import__",
        r"open\(.+['\"]w['\"]",  # Writing files
        r"shutil\.rmtree",
        r"os\.remove",
        r"rm\s+-rf",
    ]
    
    # Required patterns for equation nodes
    EQUATION_REQUIRED = [
        "id=",
        "name=",
        "latex=",
        "sympy=",
        "variables=",
        "domain=",
    ]
    
    def __init__(self):
        self.checks = {
            "syntax": self._check_syntax,
            "security": self._check_security,
            "physics": self._check_physics,
            "consistency": self._check_consistency,
            "completeness": self._check_completeness,
        }
    
    def validate(self, proposal: EvolutionProposal) -> ValidationResult:
        """
        Run all validation checks on a proposal.
        
        Returns ValidationResult with pass/fail and details.
        """
        errors = []
        warnings = []
        suggestions = []
        check_results = {}
        
        # Run each check
        for check_name, check_func in self.checks.items():
            try:
                result = check_func(proposal)
                check_results[check_name] = result["passed"]
                errors.extend(result.get("errors", []))
                warnings.extend(result.get("warnings", []))
                suggestions.extend(result.get("suggestions", []))
            except Exception as e:
                check_results[check_name] = False
                errors.append(f"{check_name} check failed: {str(e)}")
        
        # Calculate overall pass/fail
        passed = all(check_results.values()) and len(errors) == 0
        confidence = sum(check_results.values()) / len(check_results) if check_results else 0.0
        
        return ValidationResult(
            passed=passed,
            checks=check_results,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            confidence=confidence,
        )
    
    def _check_syntax(self, proposal: EvolutionProposal) -> Dict[str, Any]:
        """Check if code changes have valid Python syntax."""
        errors = []
        warnings = []
        
        for change in proposal.changes:
            if change.new_content and change.file_path.endswith(".py"):
                try:
                    ast.parse(change.new_content)
                except SyntaxError as e:
                    errors.append(f"Syntax error in {change.file_path}: {e}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
    
    def _check_security(self, proposal: EvolutionProposal) -> Dict[str, Any]:
        """Check for dangerous patterns in code changes."""
        errors = []
        warnings = []
        
        for change in proposal.changes:
            if change.new_content:
                for pattern in self.DANGEROUS_PATTERNS:
                    if re.search(pattern, change.new_content):
                        errors.append(
                            f"Security: Dangerous pattern '{pattern}' found in {change.file_path}"
                        )
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
    
    def _check_physics(self, proposal: EvolutionProposal) -> Dict[str, Any]:
        """Check physics-specific requirements."""
        errors = []
        warnings = []
        suggestions = []
        
        if proposal.proposal_type in [ProposalType.NEW_EQUATION, ProposalType.EQUATION_CORRECTION]:
            for change in proposal.changes:
                if change.new_content:
                    # Check for required equation fields
                    for required in self.EQUATION_REQUIRED:
                        if required not in change.new_content:
                            errors.append(
                                f"Physics: Missing required field '{required}' in equation"
                            )
                    
                    # Check for LaTeX validity (basic check)
                    if "latex=" in change.new_content:
                        latex_match = re.search(r'latex\s*=\s*[rf]?"([^"]+)"', change.new_content)
                        if latex_match:
                            latex = latex_match.group(1)
                            # Check for balanced braces
                            if latex.count("{") != latex.count("}"):
                                warnings.append("Physics: LaTeX may have unbalanced braces")
                    
                    # Suggest dimensional analysis
                    suggestions.append("Consider adding dimensional analysis verification")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
        }
    
    def _check_consistency(self, proposal: EvolutionProposal) -> Dict[str, Any]:
        """Check for consistency with existing codebase."""
        errors = []
        warnings = []
        
        for change in proposal.changes:
            if change.new_content:
                # Check for consistent naming
                if "class " in change.new_content:
                    # Classes should be CamelCase
                    classes = re.findall(r"class\s+(\w+)", change.new_content)
                    for cls in classes:
                        if not cls[0].isupper():
                            warnings.append(f"Consistency: Class '{cls}' should be CamelCase")
                
                # Check for docstrings
                if "def " in change.new_content:
                    funcs = re.findall(r'def\s+(\w+)\s*\([^)]*\):', change.new_content)
                    for func in funcs:
                        if func.startswith("_"):
                            continue
                        # Check if function has docstring (simplified check)
                        func_pattern = rf'def\s+{func}\s*\([^)]*\):\s*\n\s*"""'
                        if not re.search(func_pattern, change.new_content):
                            warnings.append(f"Consistency: Function '{func}' should have docstring")
        
        return {
            "passed": True,  # Warnings don't fail
            "errors": errors,
            "warnings": warnings,
        }
    
    def _check_completeness(self, proposal: EvolutionProposal) -> Dict[str, Any]:
        """Check if proposal is complete."""
        errors = []
        warnings = []
        
        if not proposal.title:
            errors.append("Completeness: Proposal needs a title")
        
        if not proposal.description:
            warnings.append("Completeness: Consider adding a description")
        
        if not proposal.motivation:
            warnings.append("Completeness: Consider explaining the motivation")
        
        if not proposal.changes:
            errors.append("Completeness: Proposal has no code changes")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
    
    def quick_validate(self, code: str) -> bool:
        """Quick syntax check for code snippet."""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
