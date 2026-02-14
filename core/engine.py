# core/
"""
PATH: core/engine.py
PURPOSE: Central neurosymbolic engine that integrates neural and symbolic reasoning.

FLOW:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Input     │───▶│   Neural     │───▶│  Symbolic   │───▶│  Integration │
│ Validation  │    │  Processing  │    │  Processing │    │   & Output   │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘

First Principle Analysis:
- Neural: Pattern recognition via embeddings and similarity
- Symbolic: Logical inference via rule application and constraint satisfaction
- Integration: Weighted combination based on confidence scores

Mathematical Foundation:
- Neural: f_neural(x) = softmax(W·embed(x) + b)
- Symbolic: f_symbolic(x) = apply_rules(parse(x))
- Integration: f(x) = α·f_neural(x) + (1-α)·f_symbolic(x)

DEPENDENCIES:
- numpy: Numerical operations for neural processing
- sympy: Symbolic mathematics
- validators: Input/output validation
- loggers: System logging
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from abc import ABC, abstractmethod
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

# Import validators and loggers
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validators.data_validator import DataValidator
from loggers.system_logger import SystemLogger

# Try to import sympy for symbolic processing
try:
    import sympy as sp
    from sympy import Symbol, sympify, simplify, solve, diff, integrate
    from sympy.parsing.sympy_parser import parse_expr
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


class ProcessingMode(Enum):
    """Processing mode for the engine."""
    NEURAL_ONLY = "neural"
    SYMBOLIC_ONLY = "symbolic"
    HYBRID = "hybrid"
    AUTO = "auto"


@dataclass
class ProcessingResult:
    """Result from neural or symbolic processing."""
    output: Any
    confidence: float
    method: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'output': self.output,
            'confidence': self.confidence,
            'method': self.method,
            'metadata': self.metadata
        }


class NeuralComponent:
    """
    Neural processing component using embedding-based similarity and pattern matching.
    
    This is a lightweight neural component that doesn't require heavy ML frameworks.
    For production, integrate with PyTorch/TensorFlow.
    """
    
    def __init__(self, embedding_dim: int = 128):
        """
        Initialize neural component.
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedding_dim = embedding_dim
        self.logger = SystemLogger()
        
        # Simple pattern memory (in production: use vector database)
        self.pattern_memory: Dict[str, np.ndarray] = {}
        self.pattern_outputs: Dict[str, Any] = {}
        
        # Initialize random projection matrix for simple embeddings
        np.random.seed(42)
        self.projection_matrix = np.random.randn(1000, embedding_dim) / np.sqrt(embedding_dim)
        
        self.logger.log("NeuralComponent initialized", level="INFO")
    
    def embed(self, data: Any) -> np.ndarray:
        """
        Create embedding for input data.
        
        Uses a simple hash-based embedding approach.
        In production, use pre-trained embeddings (BERT, etc.)
        
        Args:
            data: Input data to embed
            
        Returns:
            Embedding vector
        """
        # Convert data to string representation
        data_str = json.dumps(data, sort_keys=True, default=str)
        
        # Create feature vector from character n-grams
        features = np.zeros(1000)
        for i in range(len(data_str) - 2):
            ngram = data_str[i:i+3]
            idx = hash(ngram) % 1000
            features[idx] += 1
        
        # Normalize
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        
        # Project to embedding dimension
        embedding = features @ self.projection_matrix
        
        return embedding
    
    def similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between embeddings.
        
        Args:
            emb1: First embedding
            emb2: Second embedding
            
        Returns:
            Similarity score [0, 1]
        """
        dot = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot / (norm1 * norm2)
        # Convert from [-1, 1] to [0, 1]
        return (similarity + 1) / 2
    
    def learn_pattern(self, pattern_id: str, input_data: Any, output_data: Any) -> None:
        """
        Learn a pattern by storing its embedding and output.
        
        Args:
            pattern_id: Unique identifier for the pattern
            input_data: Input data for the pattern
            output_data: Expected output for the pattern
        """
        embedding = self.embed(input_data)
        self.pattern_memory[pattern_id] = embedding
        self.pattern_outputs[pattern_id] = output_data
        
        self.logger.log(f"Learned pattern: {pattern_id}", level="DEBUG")
    
    def process(self, input_data: Any) -> ProcessingResult:
        """
        Process input through neural pattern matching.
        
        Args:
            input_data: Input data to process
            
        Returns:
            ProcessingResult with matched patterns and confidence
        """
        input_embedding = self.embed(input_data)
        
        # Find most similar patterns
        similarities = []
        for pattern_id, pattern_emb in self.pattern_memory.items():
            sim = self.similarity(input_embedding, pattern_emb)
            similarities.append((pattern_id, sim))
        
        if not similarities:
            # No patterns learned yet
            return ProcessingResult(
                output={'type': 'no_match', 'data': input_data},
                confidence=0.1,
                method='neural_no_patterns',
                metadata={'embedding_dim': self.embedding_dim}
            )
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        best_match = similarities[0]
        
        if best_match[1] > 0.7:  # Good match threshold
            return ProcessingResult(
                output=self.pattern_outputs.get(best_match[0], input_data),
                confidence=best_match[1],
                method='neural_pattern_match',
                metadata={
                    'matched_pattern': best_match[0],
                    'similarity': best_match[1],
                    'top_matches': similarities[:3]
                }
            )
        else:
            # Low confidence match - interpolate or extrapolate
            return ProcessingResult(
                output={
                    'type': 'weak_match',
                    'data': input_data,
                    'nearest_pattern': best_match[0],
                    'similarity': best_match[1]
                },
                confidence=best_match[1],
                method='neural_weak_match',
                metadata={
                    'matched_pattern': best_match[0],
                    'similarity': best_match[1]
                }
            )


class SymbolicComponent:
    """
    Symbolic processing component using rule-based inference and symbolic math.
    
    Integrates with SymPy for mathematical operations.
    """
    
    def __init__(self):
        """Initialize symbolic component."""
        self.logger = SystemLogger()
        
        # Rule base for logical inference
        self.rules: List[Dict[str, Any]] = []
        
        # Known facts/axioms
        self.facts: Dict[str, Any] = {}
        
        # Symbol definitions
        self.symbols: Dict[str, Any] = {}
        
        self.logger.log("SymbolicComponent initialized", level="INFO")
    
    def add_rule(self, name: str, condition: str, action: str, priority: int = 0) -> None:
        """
        Add a rule to the rule base.
        
        Args:
            name: Rule name
            condition: Condition expression (Python expression string)
            action: Action expression (what to produce if condition is true)
            priority: Rule priority (higher = more important)
        """
        self.rules.append({
            'name': name,
            'condition': condition,
            'action': action,
            'priority': priority
        })
        self.rules.sort(key=lambda r: r['priority'], reverse=True)
        self.logger.log(f"Added rule: {name}", level="DEBUG")
    
    def add_fact(self, name: str, value: Any) -> None:
        """
        Add a fact to the knowledge base.
        
        Args:
            name: Fact name
            value: Fact value
        """
        self.facts[name] = value
        self.logger.log(f"Added fact: {name} = {value}", level="DEBUG")
    
    def define_symbol(self, name: str) -> Any:
        """
        Define a symbolic variable.
        
        Args:
            name: Symbol name
            
        Returns:
            SymPy symbol
        """
        if SYMPY_AVAILABLE:
            self.symbols[name] = Symbol(name)
            return self.symbols[name]
        else:
            self.symbols[name] = name
            return name
    
    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition string against a context.
        
        Args:
            condition: Condition expression
            context: Variable context
            
        Returns:
            True if condition is satisfied
        """
        try:
            # Create safe evaluation context
            safe_context = {
                'True': True,
                'False': False,
                'None': None,
                **self.facts,
                **context
            }
            
            # Evaluate condition
            result = eval(condition, {"__builtins__": {}}, safe_context)
            return bool(result)
        except Exception as e:
            self.logger.log(f"Error evaluating condition '{condition}': {e}", level="WARNING")
            return False
    
    def apply_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply all matching rules to the context.
        
        Args:
            context: Current context/state
            
        Returns:
            List of rule applications
        """
        applications = []
        
        for rule in self.rules:
            if self.evaluate_condition(rule['condition'], context):
                try:
                    # Evaluate action
                    safe_context = {
                        'True': True,
                        'False': False,
                        'None': None,
                        **self.facts,
                        **context
                    }
                    result = eval(rule['action'], {"__builtins__": {}}, safe_context)
                    applications.append({
                        'rule': rule['name'],
                        'result': result,
                        'priority': rule['priority']
                    })
                except Exception as e:
                    self.logger.log(f"Error executing rule '{rule['name']}': {e}", level="WARNING")
        
        return applications
    
    def symbolic_math(self, expression: str, operation: str = 'simplify', 
                      variable: Optional[str] = None, value: Optional[float] = None) -> Any:
        """
        Perform symbolic math operations.
        
        Args:
            expression: Mathematical expression string
            operation: Operation to perform (simplify, differentiate, integrate, solve, substitute)
            variable: Variable for calculus operations
            value: Value for substitution
            
        Returns:
            Result of symbolic operation
        """
        if not SYMPY_AVAILABLE:
            self.logger.log("SymPy not available for symbolic math", level="WARNING")
            return {'error': 'SymPy not available', 'expression': expression}
        
        try:
            # Parse expression
            expr = parse_expr(expression)
            
            if operation == 'simplify':
                result = simplify(expr)
            elif operation == 'differentiate' and variable:
                var = Symbol(variable)
                result = diff(expr, var)
            elif operation == 'integrate' and variable:
                var = Symbol(variable)
                result = integrate(expr, var)
            elif operation == 'solve' and variable:
                var = Symbol(variable)
                result = solve(expr, var)
            elif operation == 'substitute' and variable and value is not None:
                var = Symbol(variable)
                result = expr.subs(var, value)
            else:
                result = expr
            
            return str(result)
            
        except Exception as e:
            self.logger.log(f"Error in symbolic math: {e}", level="WARNING")
            return {'error': str(e), 'expression': expression}
    
    def process(self, input_data: Any) -> ProcessingResult:
        """
        Process input through symbolic reasoning.
        
        Args:
            input_data: Input data to process
            
        Returns:
            ProcessingResult with symbolic analysis
        """
        result = {
            'type': 'symbolic_analysis',
            'input': input_data,
            'rules_applied': [],
            'symbolic_result': None
        }
        confidence = 0.5
        
        # If input is a dict, use it as context
        if isinstance(input_data, dict):
            context = input_data
            
            # Apply rules
            rule_results = self.apply_rules(context)
            result['rules_applied'] = rule_results
            
            if rule_results:
                confidence = 0.7 + 0.1 * min(len(rule_results), 3)
            
            # Check for mathematical expression
            if 'expression' in context:
                expr = context['expression']
                operation = context.get('operation', 'simplify')
                variable = context.get('variable')
                value = context.get('value')
                
                result['symbolic_result'] = self.symbolic_math(
                    expr, operation, variable, value
                )
                confidence = max(confidence, 0.8)
        
        elif isinstance(input_data, str):
            # Try to parse as mathematical expression
            result['symbolic_result'] = self.symbolic_math(input_data)
            if not isinstance(result['symbolic_result'], dict):
                confidence = 0.8
        
        return ProcessingResult(
            output=result,
            confidence=confidence,
            method='symbolic_reasoning',
            metadata={
                'rules_count': len(self.rules),
                'facts_count': len(self.facts),
                'sympy_available': SYMPY_AVAILABLE
            }
        )


class NeurosymboticEngine:
    """
    Central neurosymbolic reasoning engine.
    
    Integrates neural network learning with symbolic reasoning
    to create a hybrid AI system capable of both pattern recognition
    and logical deduction.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the neurosymbolic engine.
        
        Args:
            config: Configuration dictionary for engine parameters
        """
        self.config = config or {}
        self.validator = DataValidator()
        self.logger = SystemLogger()
        
        # Neural component
        embedding_dim = self.config.get('embedding_dim', 128)
        self.neural_component = NeuralComponent(embedding_dim=embedding_dim)
        
        # Symbolic component
        self.symbolic_component = SymbolicComponent()
        
        # Processing mode
        self.mode = ProcessingMode(self.config.get('mode', 'hybrid'))
        
        # Integration weight (0 = pure symbolic, 1 = pure neural)
        self.alpha = self.config.get('alpha', 0.5)
        
        # Knowledge base
        self.knowledge_base = {}
        
        # Processing history for learning
        self.processing_history: List[Dict[str, Any]] = []
        
        # Initialize with some default rules
        self._initialize_default_rules()
        
        self.logger.log("NeurosymboticEngine initialized", level="INFO")
        
        # Validate initialization
        if config and not self.validator.validate_dict(config):
            self.logger.log("Invalid configuration provided", level="WARNING")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default symbolic rules."""
        # Physics rules
        self.symbolic_component.add_rule(
            'kinetic_energy',
            "'mass' in context and 'velocity' in context",
            "0.5 * context['mass'] * context['velocity'] ** 2",
            priority=1
        )
        
        self.symbolic_component.add_rule(
            'momentum',
            "'mass' in context and 'velocity' in context",
            "context['mass'] * context['velocity']",
            priority=1
        )
        
        self.symbolic_component.add_rule(
            'force',
            "'mass' in context and 'acceleration' in context",
            "context['mass'] * context['acceleration']",
            priority=1
        )
        
        # Add default facts
        self.symbolic_component.add_fact('speed_of_light', 299792458)  # m/s
        self.symbolic_component.add_fact('planck_constant', 6.62607015e-34)  # J·s
        self.symbolic_component.add_fact('gravitational_constant', 6.67430e-11)  # m³/(kg·s²)
    
    def process(self, input_data: Any) -> Any:
        """
        Process input through the neurosymbolic engine.
        
        Mathematical approach:
        - Neural: f_neural(x) -> pattern_representation
        - Symbolic: f_symbolic(pattern) -> logical_inference
        - Integration: f_integrated = α·f_neural + (1-α)·f_symbolic
        
        Args:
            input_data: Input to process
            
        Returns:
            Processed output
        """
        # Validate input
        if not self.validator.validate_input(input_data):
            self.logger.log("Invalid input data", level="ERROR")
            raise ValueError("Invalid input data")
        
        self.logger.log(f"Processing input: {type(input_data)}", level="DEBUG")
        
        try:
            # Determine processing mode
            mode = self._determine_mode(input_data)
            
            # Neural processing
            neural_result = self._neural_process(input_data)
            
            # Symbolic processing
            symbolic_result = self._symbolic_process(input_data)
            
            # Integration
            result = self._integrate_results(neural_result, symbolic_result, mode)
            
            # Validate output
            if not self.validator.validate_output(result):
                self.logger.log("Invalid output generated", level="ERROR")
                raise ValueError("Invalid output generated")
            
            # Store in processing history
            self.processing_history.append({
                'input': input_data,
                'neural_result': neural_result.to_dict(),
                'symbolic_result': symbolic_result.to_dict(),
                'output': result,
                'mode': mode.value
            })
            
            self.logger.log("Processing completed successfully", level="INFO")
            return result
            
        except Exception as e:
            self.logger.log(f"Error in processing: {str(e)}", level="ERROR")
            raise
    
    def _determine_mode(self, input_data: Any) -> ProcessingMode:
        """
        Determine the best processing mode for input.
        
        Args:
            input_data: Input data
            
        Returns:
            Appropriate processing mode
        """
        if self.mode != ProcessingMode.AUTO:
            return self.mode
        
        # Auto-detect best mode based on input type
        if isinstance(input_data, str):
            # Check if it looks like a mathematical expression
            math_indicators = ['+', '-', '*', '/', '**', 'sin', 'cos', 'exp', 'log', '=']
            if any(ind in input_data for ind in math_indicators):
                return ProcessingMode.SYMBOLIC_ONLY
        
        if isinstance(input_data, dict):
            # Check if it has known variable names
            physics_vars = {'mass', 'velocity', 'acceleration', 'force', 'energy', 'time', 'position'}
            if physics_vars & set(input_data.keys()):
                return ProcessingMode.HYBRID
        
        return ProcessingMode.HYBRID
    
    def _neural_process(self, input_data: Any) -> ProcessingResult:
        """
        Neural network processing component.
        
        Args:
            input_data: Input to process neurally
            
        Returns:
            ProcessingResult from neural component
        """
        self.logger.log("Neural processing", level="DEBUG")
        return self.neural_component.process(input_data)
    
    def _symbolic_process(self, input_data: Any) -> ProcessingResult:
        """
        Symbolic reasoning component.
        
        Args:
            input_data: Input to process symbolically
            
        Returns:
            ProcessingResult from symbolic component
        """
        self.logger.log("Symbolic processing", level="DEBUG")
        return self.symbolic_component.process(input_data)
    
    def _integrate_results(self, neural_result: ProcessingResult, 
                          symbolic_result: ProcessingResult,
                          mode: ProcessingMode) -> Dict[str, Any]:
        """
        Integrate neural and symbolic results.
        
        Mathematical integration:
        - Weighted combination based on confidence scores
        - Conflict resolution when results disagree
        
        Args:
            neural_result: Result from neural processing
            symbolic_result: Result from symbolic processing
            mode: Processing mode used
            
        Returns:
            Integrated result dictionary
        """
        if mode == ProcessingMode.NEURAL_ONLY:
            return {
                'result': neural_result.output,
                'confidence': neural_result.confidence,
                'method': 'neural',
                'metadata': neural_result.metadata
            }
        
        if mode == ProcessingMode.SYMBOLIC_ONLY:
            return {
                'result': symbolic_result.output,
                'confidence': symbolic_result.confidence,
                'method': 'symbolic',
                'metadata': symbolic_result.metadata
            }
        
        # Hybrid mode - integrate based on confidence
        total_confidence = neural_result.confidence + symbolic_result.confidence
        if total_confidence == 0:
            neural_weight = 0.5
            symbolic_weight = 0.5
        else:
            neural_weight = neural_result.confidence / total_confidence
            symbolic_weight = symbolic_result.confidence / total_confidence
        
        # Adjust weights by alpha parameter
        neural_weight = neural_weight * self.alpha + (1 - self.alpha) * 0.5
        symbolic_weight = 1 - neural_weight
        
        # Combined confidence
        combined_confidence = (
            neural_weight * neural_result.confidence +
            symbolic_weight * symbolic_result.confidence
        )
        
        integrated = {
            'neural': neural_result.to_dict(),
            'symbolic': symbolic_result.to_dict(),
            'weights': {
                'neural': neural_weight,
                'symbolic': symbolic_weight
            },
            'confidence': combined_confidence,
            'method': 'hybrid',
            'primary_result': (
                symbolic_result.output if symbolic_result.confidence > neural_result.confidence
                else neural_result.output
            )
        }
        
        self.logger.log("Results integrated", level="DEBUG")
        return integrated
    
    def learn(self, input_data: Any, expected_output: Any, pattern_id: Optional[str] = None) -> None:
        """
        Learn from a training example.
        
        Args:
            input_data: Input data
            expected_output: Expected output
            pattern_id: Optional pattern identifier
        """
        # Generate pattern ID if not provided
        if pattern_id is None:
            data_hash = hashlib.md5(json.dumps(input_data, sort_keys=True, default=str).encode()).hexdigest()[:8]
            pattern_id = f"pattern_{data_hash}"
        
        # Learn in neural component
        self.neural_component.learn_pattern(pattern_id, input_data, expected_output)
        
        self.logger.log(f"Learned pattern: {pattern_id}", level="INFO")
    
    def add_rule(self, name: str, condition: str, action: str, priority: int = 0) -> None:
        """
        Add a symbolic rule.
        
        Args:
            name: Rule name
            condition: Condition expression
            action: Action expression
            priority: Rule priority
        """
        self.symbolic_component.add_rule(name, condition, action, priority)
    
    def add_fact(self, name: str, value: Any) -> None:
        """
        Add a fact to the knowledge base.
        
        Args:
            name: Fact name
            value: Fact value
        """
        self.symbolic_component.add_fact(name, value)
        self.knowledge_base[name] = value
    
    def evolve(self, feedback: Dict[str, Any]) -> None:
        """
        Evolve the engine based on feedback.
        
        This method allows the engine to modify itself based on
        performance feedback, enabling self-improvement.
        
        Args:
            feedback: Performance feedback dictionary
        """
        if not self.validator.validate_dict(feedback):
            self.logger.log("Invalid feedback provided", level="WARNING")
            return
        
        self.logger.log("Engine evolution triggered", level="INFO")
        
        # Adjust alpha based on feedback
        if 'neural_accuracy' in feedback and 'symbolic_accuracy' in feedback:
            neural_acc = feedback['neural_accuracy']
            symbolic_acc = feedback['symbolic_accuracy']
            
            # Shift alpha towards better performing component
            if neural_acc > symbolic_acc:
                self.alpha = min(1.0, self.alpha + 0.05)
            elif symbolic_acc > neural_acc:
                self.alpha = max(0.0, self.alpha - 0.05)
            
            self.logger.log(f"Adjusted alpha to {self.alpha}", level="INFO")
        
        # Learn from correct examples in feedback
        if 'correct_examples' in feedback:
            for example in feedback['correct_examples']:
                if 'input' in example and 'output' in example:
                    self.learn(example['input'], example['output'])
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get engine statistics.
        
        Returns:
            Dictionary with engine statistics
        """
        return {
            'mode': self.mode.value,
            'alpha': self.alpha,
            'neural_patterns': len(self.neural_component.pattern_memory),
            'symbolic_rules': len(self.symbolic_component.rules),
            'facts': len(self.symbolic_component.facts),
            'processing_history_size': len(self.processing_history),
            'sympy_available': SYMPY_AVAILABLE
        }


class ReasoningEngine(ABC):
    """
    Abstract base class for reasoning engines.
    
    Provides interface for different reasoning approaches.
    """
    
    @abstractmethod
    def reason(self, premises: List[Any]) -> Any:
        """
        Perform reasoning on given premises.
        
        Args:
            premises: List of premises to reason from
            
        Returns:
            Reasoning result
        """
        pass
