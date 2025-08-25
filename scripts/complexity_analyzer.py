#!/usr/bin/env python3
"""
Complexity Analysis Tool

Analyzes Python functions for complexity metrics and identifies candidates
for refactoring. Uses AST parsing to calculate cyclomatic complexity.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import sys


class ComplexityAnalyzer:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        
    def analyze_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            # Control flow statements increase complexity
            if isinstance(node, (
                ast.If, ast.For, ast.While, ast.Try,
                ast.ExceptHandler, ast.With, ast.AsyncWith,
                ast.comprehension  # List/dict/set comprehensions
            )):
                complexity += 1
            # Boolean operators in conditions
            elif isinstance(node, (ast.BoolOp,)):
                if isinstance(node.op, (ast.And, ast.Or)):
                    complexity += len(node.values) - 1
        
        return complexity
    
    def analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze all functions in a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self.analyze_function_complexity(node)
                    line_count = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'complexity': complexity,
                        'line_count': line_count,
                        'file': str(file_path),
                        'args_count': len(node.args.args)
                    })
            
            return functions
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return []
    
    def scan_project(self) -> List[Dict[str, Any]]:
        """Scan entire project for function complexity."""
        all_functions = []
        
        for py_file in self.root_dir.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            functions = self.analyze_file(py_file)
            all_functions.extend(functions)
        
        return all_functions
    
    def identify_refactor_candidates(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify functions that are candidates for refactoring."""
        candidates = []
        
        for func in functions:
            score = 0
            reasons = []
            
            # High cyclomatic complexity
            if func['complexity'] > 10:
                score += 3
                reasons.append(f"High complexity ({func['complexity']})")
            elif func['complexity'] > 7:
                score += 2
                reasons.append(f"Medium complexity ({func['complexity']})")
            
            # Long functions
            if func['line_count'] > 50:
                score += 2
                reasons.append(f"Long function ({func['line_count']} lines)")
            elif func['line_count'] > 30:
                score += 1
                reasons.append(f"Medium length ({func['line_count']} lines)")
            
            # Many parameters
            if func['args_count'] > 5:
                score += 1
                reasons.append(f"Many parameters ({func['args_count']})")
            
            if score >= 2:  # Threshold for refactoring
                candidates.append({
                    **func,
                    'refactor_score': score,
                    'reasons': reasons
                })
        
        return sorted(candidates, key=lambda x: x['refactor_score'], reverse=True)


def main():
    analyzer = ComplexityAnalyzer()
    
    print("🔧 Function Complexity Analysis")
    print("=" * 50)
    
    # Analyze all functions
    all_functions = analyzer.scan_project()
    print(f"Analyzed {len(all_functions)} functions")
    
    # Find refactor candidates
    candidates = analyzer.identify_refactor_candidates(all_functions)
    
    if candidates:
        print(f"\n📊 Top {min(10, len(candidates))} Refactor Candidates:")
        print("-" * 50)
        
        for i, func in enumerate(candidates[:10], 1):
            print(f"{i}. {func['name']} ({Path(func['file']).name}:{func['line']})")
            print(f"   Score: {func['refactor_score']}, Complexity: {func['complexity']}")
            print(f"   Reasons: {', '.join(func['reasons'])}")
            print()
    
    # Statistics
    complexities = [f['complexity'] for f in all_functions]
    avg_complexity = sum(complexities) / len(complexities) if complexities else 0
    max_complexity = max(complexities) if complexities else 0
    
    print(f"📈 Statistics:")
    print(f"   Average complexity: {avg_complexity:.1f}")
    print(f"   Maximum complexity: {max_complexity}")
    print(f"   Functions with complexity > 10: {len([f for f in all_functions if f['complexity'] > 10])}")
    print(f"   Functions with complexity > 7: {len([f for f in all_functions if f['complexity'] > 7])}")
    
    return candidates


if __name__ == "__main__":
    main()