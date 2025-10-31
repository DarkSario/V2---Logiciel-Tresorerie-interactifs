#!/usr/bin/env python3
"""
Project Audit Script for V2 - Logiciel Tresorerie Interactifs

This script performs a comprehensive audit of the codebase to detect:
- Sensitive files (databases, logs, environment files)
- Large files (>5 MB by default)
- Circular imports
- Orphan modules (rarely imported)
- TODO/FIXME/XXX comments
- Missing or unused dependencies
- Missing tests

The script generates a PROJECT_AUDIT.md report with findings and recommendations.

Usage:
    python scripts/project_audit.py [--output OUTPUT] [--max-size-MB SIZE]

Examples:
    python scripts/project_audit.py
    python scripts/project_audit.py --output PROJECT_AUDIT.md --max-size-MB 5
"""

import os
import sys
import ast
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
import re


class ProjectAuditor:
    """Audits a Python project for various issues and generates a report."""
    
    def __init__(self, root_dir: str, max_size_mb: float = 5.0):
        """
        Initialize the auditor.
        
        Args:
            root_dir: Root directory of the project
            max_size_mb: Maximum file size in MB before flagging as large
        """
        self.root_dir = Path(root_dir).resolve()
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        
        # Results storage
        self.sensitive_files = {
            'databases': [],
            'logs': [],
            'env_files': [],
        }
        self.large_files = []
        self.import_graph = defaultdict(set)  # module -> set of imported modules
        self.circular_imports = []
        self.orphan_modules = []
        self.todos = []
        self.python_files = []
        self.modules_without_docstring = []
        self.modules_without_main = []
        self.parse_errors = []
        
        # Dependencies analysis
        self.requirements = set()
        self.imported_packages = set()
        
    def scan_files(self):
        """Scan the repository for files to analyze."""
        print("🔍 Scanning repository files...")
        
        for root, dirs, files in os.walk(self.root_dir):
            # Skip hidden directories and virtual environments
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__', 'node_modules']]
            
            rel_root = Path(root).relative_to(self.root_dir)
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.root_dir)
                
                # Check file size
                try:
                    file_size = file_path.stat().st_size
                    if file_size > self.max_size_bytes:
                        self.large_files.append({
                            'path': str(rel_path),
                            'size_mb': file_size / (1024 * 1024)
                        })
                except OSError:
                    pass
                
                # Categorize sensitive files
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    self.sensitive_files['databases'].append(str(rel_path))
                elif file.endswith('.log'):
                    self.sensitive_files['logs'].append(str(rel_path))
                elif file in ['.env', 'env', '.env.local', '.env.production'] or file.startswith('env.'):
                    self.sensitive_files['env_files'].append(str(rel_path))
                
                # Track Python files for analysis
                if file.endswith('.py'):
                    self.python_files.append(file_path)
    
    def analyze_python_files(self):
        """Analyze Python files for imports, TODOs, and other issues."""
        print("🐍 Analyzing Python files...")
        
        for py_file in self.python_files:
            rel_path = py_file.relative_to(self.root_dir)
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Parse AST
                try:
                    tree = ast.parse(content, filename=str(py_file))
                    self._analyze_ast(tree, py_file, rel_path)
                except SyntaxError as e:
                    self.parse_errors.append({
                        'file': str(rel_path),
                        'error': str(e)
                    })
                
                # Search for TODO/FIXME/XXX comments
                self._find_todos(content, rel_path)
                
            except Exception as e:
                self.parse_errors.append({
                    'file': str(rel_path),
                    'error': f"Failed to read file: {str(e)}"
                })
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path, rel_path: Path):
        """Analyze the AST of a Python file."""
        module_name = self._get_module_name(rel_path)
        
        # Check for module docstring
        has_docstring = (isinstance(tree.body, list) and 
                        len(tree.body) > 0 and 
                        isinstance(tree.body[0], ast.Expr) and 
                        isinstance(tree.body[0].value, (ast.Str, ast.Constant)))
        
        if not has_docstring:
            self.modules_without_docstring.append(str(rel_path))
        
        # Check for main function or if __name__ == "__main__"
        has_main = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in ['main', '__main__']:
                has_main = True
                break
            if isinstance(node, ast.If):
                # Check for if __name__ == "__main__"
                if isinstance(node.test, ast.Compare):
                    if hasattr(node.test.left, 'id') and node.test.left.id == '__name__':
                        has_main = True
                        break
        
        if not has_main and str(rel_path) not in ['__init__.py', 'setup.py', 'conftest.py']:
            self.modules_without_main.append(str(rel_path))
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_module = alias.name.split('.')[0]
                    self.import_graph[module_name].add(imported_module)
                    self.imported_packages.add(imported_module)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_module = node.module.split('.')[0]
                    self.import_graph[module_name].add(imported_module)
                    self.imported_packages.add(imported_module)
    
    def _get_module_name(self, rel_path: Path) -> str:
        """Convert a file path to a module name."""
        parts = list(rel_path.parts)
        if parts[-1] == '__init__.py':
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1][:-3]  # Remove .py extension
        return '.'.join(parts) if parts else 'root'
    
    def _find_todos(self, content: str, rel_path: Path):
        """Find TODO/FIXME/XXX comments in the content."""
        lines = content.split('\n')
        patterns = [r'#\s*(TODO|FIXME|XXX)', r'"""\s*(TODO|FIXME|XXX)', r"'''\s*(TODO|FIXME|XXX)"]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.todos.append({
                        'file': str(rel_path),
                        'line': line_num,
                        'text': line.strip()
                    })
                    break
    
    def detect_circular_imports(self):
        """Detect circular imports in the import graph."""
        print("🔄 Detecting circular imports...")
        
        visited = set()
        rec_stack = set()
        
        def has_cycle(node, path):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.import_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, path + [neighbor]):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor) if neighbor in path else 0
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in self.circular_imports:
                        self.circular_imports.append(cycle)
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in list(self.import_graph.keys()):
            if node not in visited:
                has_cycle(node, [node])
    
    def identify_orphan_modules(self):
        """Identify modules that are rarely or never imported."""
        print("🔍 Identifying orphan modules...")
        
        # Count how many times each module is imported
        import_count = defaultdict(int)
        
        for module, imports in self.import_graph.items():
            for imported in imports:
                # Only count internal modules (not external packages)
                if '.' in imported or imported in [self._get_module_name(Path(pf).relative_to(self.root_dir)) for pf in self.python_files]:
                    import_count[imported] += 1
        
        # Find modules with 0-1 imports (potential orphans)
        all_modules = [self._get_module_name(Path(pf).relative_to(self.root_dir)) for pf in self.python_files]
        
        for module in all_modules:
            if import_count[module] <= 1 and module not in ['main', 'root', '__main__']:
                # Exclude common entry points and test files
                if not module.startswith('test_') and 'test' not in module:
                    self.orphan_modules.append({
                        'module': module,
                        'import_count': import_count[module]
                    })
    
    def analyze_dependencies(self):
        """Analyze dependencies from requirements.txt."""
        print("📦 Analyzing dependencies...")
        
        req_file = self.root_dir / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before ==, >=, etc.)
                            pkg_name = re.split(r'[=><!\[]', line)[0].strip()
                            # Normalize package names (e.g., python-docx -> docx)
                            self.requirements.add(pkg_name.lower().replace('-', '_'))
                            self.requirements.add(pkg_name.lower().replace('_', '-'))
                            self.requirements.add(pkg_name.lower())
            except Exception as e:
                print(f"Warning: Could not read requirements.txt: {e}")
    
    def count_tests(self) -> Dict[str, int]:
        """Count test files and test functions."""
        print("🧪 Counting tests...")
        
        test_dir = self.root_dir / 'tests'
        test_count = {'files': 0, 'functions': 0}
        
        if not test_dir.exists():
            return test_count
        
        for py_file in test_dir.rglob('*.py'):
            if py_file.name.startswith('test_') or py_file.name.endswith('_test.py'):
                test_count['files'] += 1
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                                test_count['functions'] += 1
                except:
                    pass
        
        return test_count
    
    def generate_report(self, output_file: str):
        """Generate the audit report in Markdown format."""
        print(f"📝 Generating report: {output_file}")
        
        report = []
        report.append("# PROJECT AUDIT REPORT")
        report.append("")
        report.append("*Generated automatically by `scripts/project_audit.py`*")
        report.append("")
        report.append("---")
        report.append("")
        
        # Executive Summary
        report.append("## 📊 Executive Summary")
        report.append("")
        
        total_issues = (
            len(self.sensitive_files['databases']) +
            len(self.sensitive_files['logs']) +
            len(self.sensitive_files['env_files']) +
            len(self.large_files) +
            len(self.circular_imports) +
            len(self.orphan_modules) +
            len(self.todos)
        )
        
        report.append(f"- **Total Python files analyzed**: {len(self.python_files)}")
        report.append(f"- **Total issues detected**: {total_issues}")
        report.append(f"- **Sensitive files found**: {len(self.sensitive_files['databases']) + len(self.sensitive_files['logs']) + len(self.sensitive_files['env_files'])}")
        report.append(f"- **Large files (>{self.max_size_bytes / (1024*1024):.0f} MB)**: {len(self.large_files)}")
        report.append(f"- **Circular imports detected**: {len(self.circular_imports)}")
        report.append(f"- **Potential orphan modules**: {len(self.orphan_modules)}")
        report.append(f"- **TODO/FIXME/XXX comments**: {len(self.todos)}")
        report.append("")
        
        # Sensitive Files
        report.append("## 🔒 Security & Sensitive Files")
        report.append("")
        
        if self.sensitive_files['databases']:
            report.append("### Database Files")
            report.append("")
            report.append("⚠️ **Warning**: Database files should NOT be committed to the repository!")
            report.append("")
            for db_file in self.sensitive_files['databases']:
                report.append(f"- `{db_file}`")
            report.append("")
        
        if self.sensitive_files['logs']:
            report.append("### Log Files")
            report.append("")
            report.append("⚠️ **Warning**: Log files should NOT be committed to the repository!")
            report.append("")
            for log_file in self.sensitive_files['logs']:
                report.append(f"- `{log_file}`")
            report.append("")
        
        if self.sensitive_files['env_files']:
            report.append("### Environment Files")
            report.append("")
            report.append("⚠️ **Warning**: Environment files may contain sensitive information!")
            report.append("")
            for env_file in self.sensitive_files['env_files']:
                report.append(f"- `{env_file}`")
            report.append("")
        
        # Large Files
        if self.large_files:
            report.append("## 📦 Large Files")
            report.append("")
            report.append(f"Files larger than {self.max_size_bytes / (1024*1024):.0f} MB:")
            report.append("")
            for lf in sorted(self.large_files, key=lambda x: x['size_mb'], reverse=True):
                report.append(f"- `{lf['path']}` - **{lf['size_mb']:.2f} MB**")
            report.append("")
        
        # Circular Imports
        if self.circular_imports:
            report.append("## 🔄 Circular Import Issues")
            report.append("")
            report.append("⚠️ **Warning**: Circular imports can cause import errors and make code harder to maintain!")
            report.append("")
            for i, cycle in enumerate(self.circular_imports, 1):
                report.append(f"### Cycle {i}")
                report.append("")
                report.append(" → ".join(cycle))
                report.append("")
        
        # Orphan Modules
        if self.orphan_modules:
            report.append("## 🔍 Potential Orphan Modules")
            report.append("")
            report.append("Modules that are rarely or never imported by other modules:")
            report.append("")
            for orphan in sorted(self.orphan_modules, key=lambda x: x['import_count']):
                report.append(f"- `{orphan['module']}` (imported {orphan['import_count']} time(s))")
            report.append("")
        
        # Parse Errors
        if self.parse_errors:
            report.append("## ⚠️ Parse Errors")
            report.append("")
            report.append("Files that could not be parsed:")
            report.append("")
            for error in self.parse_errors:
                report.append(f"- `{error['file']}`: {error['error']}")
            report.append("")
        
        # Modules without docstrings
        if self.modules_without_docstring:
            report.append("## 📝 Code Quality: Missing Module Docstrings")
            report.append("")
            report.append(f"Found {len(self.modules_without_docstring)} Python file(s) without module-level docstrings:")
            report.append("")
            for module in sorted(self.modules_without_docstring)[:10]:
                report.append(f"- `{module}`")
            if len(self.modules_without_docstring) > 10:
                report.append(f"- ... and {len(self.modules_without_docstring) - 10} more")
            report.append("")
        
        # Dependencies Analysis
        report.append("## 📦 Dependencies Analysis")
        report.append("")
        
        # Compare requirements with imports
        missing_in_requirements = []
        unused_in_requirements = []
        
        # Standard library modules to exclude
        stdlib_modules = {
            'os', 'sys', 're', 'json', 'csv', 'datetime', 'time', 'math', 'random',
            'collections', 'itertools', 'functools', 'pathlib', 'argparse', 'logging',
            'unittest', 'sqlite3', 'ast', 'io', 'typing', 'tkinter', 'threading',
            'subprocess', 'shutil', 'zipfile', 'tempfile', 'copy', 'pickle', 'hashlib'
        }
        
        for pkg in self.imported_packages:
            if pkg not in stdlib_modules and pkg not in self.requirements:
                # Check if it's an internal module
                if not any(pkg in str(pf) for pf in self.python_files):
                    missing_in_requirements.append(pkg)
        
        for req in self.requirements:
            found = False
            for pkg in self.imported_packages:
                if req in pkg or pkg in req or req.replace('_', '-') == pkg.replace('_', '-'):
                    found = True
                    break
            if not found:
                unused_in_requirements.append(req)
        
        if missing_in_requirements:
            report.append("### Potentially Missing from requirements.txt")
            report.append("")
            for pkg in sorted(set(missing_in_requirements)):
                report.append(f"- `{pkg}`")
            report.append("")
        
        if unused_in_requirements:
            report.append("### Potentially Unused in requirements.txt")
            report.append("")
            report.append("⚠️ Note: This is a heuristic check and may have false positives")
            report.append("")
            for pkg in sorted(set(unused_in_requirements)):
                report.append(f"- `{pkg}`")
            report.append("")
        
        # Test Coverage
        report.append("## 🧪 Test Coverage")
        report.append("")
        
        test_stats = self.count_tests()
        report.append(f"- **Test files**: {test_stats['files']}")
        report.append(f"- **Test functions**: {test_stats['functions']}")
        report.append("")
        
        if test_stats['files'] == 0:
            report.append("⚠️ **Warning**: No test files found! Consider adding tests to ensure code quality.")
            report.append("")
        elif test_stats['functions'] < 10:
            report.append("⚠️ **Warning**: Low test coverage. Consider adding more tests.")
            report.append("")
        
        # TODOs
        if self.todos:
            report.append("## 📝 TODO/FIXME/XXX Comments")
            report.append("")
            report.append(f"Found {len(self.todos)} TODO/FIXME/XXX comment(s):")
            report.append("")
            
            # Show first 20 TODOs
            for todo in self.todos[:20]:
                report.append(f"- `{todo['file']}:{todo['line']}` - {todo['text']}")
            
            if len(self.todos) > 20:
                report.append(f"- ... and {len(self.todos) - 20} more")
            report.append("")
        
        # Recommendations
        report.append("## 💡 Recommendations")
        report.append("")
        
        # High Priority
        report.append("### 🔴 High Priority")
        report.append("")
        
        if self.sensitive_files['databases']:
            report.append("1. **Remove database files from repository**")
            report.append("   ```bash")
            report.append("   # Remove from git tracking")
            for db_file in self.sensitive_files['databases']:
                report.append(f"   git rm --cached {db_file}")
            report.append("")
            report.append("   # Add to .gitignore")
            report.append("   echo '*.db' >> .gitignore")
            report.append("   echo '*.sqlite' >> .gitignore")
            report.append("   echo '*.sqlite3' >> .gitignore")
            report.append("   ```")
            report.append("")
        
        if self.sensitive_files['logs']:
            report.append("2. **Remove log files from repository**")
            report.append("   ```bash")
            report.append("   # Remove from git tracking")
            for log_file in self.sensitive_files['logs']:
                report.append(f"   git rm --cached {log_file}")
            report.append("")
            report.append("   # Add to .gitignore")
            report.append("   echo '*.log' >> .gitignore")
            report.append("   echo 'logs/' >> .gitignore")
            report.append("   ```")
            report.append("")
        
        if self.sensitive_files['env_files']:
            report.append("3. **Secure environment files**")
            report.append("   - Review environment files for sensitive information")
            report.append("   - Ensure `.env` files are in `.gitignore`")
            report.append("   - Use `env.example` as a template without sensitive data")
            report.append("")
        
        # Medium Priority
        report.append("### 🟡 Medium Priority")
        report.append("")
        
        if self.circular_imports:
            report.append("1. **Refactor circular imports**")
            report.append("   - Review the circular import cycles listed above")
            report.append("   - Consider restructuring code to remove circular dependencies")
            report.append("   - Use dependency injection or move shared code to a common module")
            report.append("")
        
        if self.large_files:
            report.append("2. **Handle large files**")
            report.append("   - Consider using Git LFS for large binary files")
            report.append("   - Move large data files outside the repository")
            report.append("   ```bash")
            report.append("   # Install and use Git LFS")
            report.append("   git lfs install")
            report.append("   git lfs track '*.db'")
            report.append("   ```")
            report.append("")
        
        if test_stats['files'] < 5:
            report.append("3. **Improve test coverage**")
            report.append("   - Add unit tests for critical modules")
            report.append("   - Aim for at least 70% code coverage")
            report.append("   - Use pytest and coverage tools")
            report.append("   ```bash")
            report.append("   pip install pytest pytest-cov")
            report.append("   pytest --cov=. --cov-report=html")
            report.append("   ```")
            report.append("")
        
        # Low Priority
        report.append("### 🟢 Low Priority")
        report.append("")
        
        if self.orphan_modules:
            report.append("1. **Review orphan modules**")
            report.append("   - Check if orphan modules are actually unused")
            report.append("   - Remove unused code or document why it's kept")
            report.append("")
        
        if self.todos:
            report.append("2. **Address TODO/FIXME comments**")
            report.append("   - Create issues for important TODOs")
            report.append("   - Remove or complete outdated TODOs")
            report.append("")
        
        if self.modules_without_docstring:
            report.append("3. **Add module docstrings**")
            report.append("   - Document the purpose of each module")
            report.append("   - Follow PEP 257 docstring conventions")
            report.append("")
        
        # How to Run
        report.append("## 🚀 How to Run This Audit Locally")
        report.append("")
        report.append("### Prerequisites")
        report.append("")
        report.append("- Python 3.8 or higher")
        report.append("")
        report.append("### Steps")
        report.append("")
        report.append("```bash")
        report.append("# Clone the repository")
        report.append("git clone <repository-url>")
        report.append("cd V2---Logiciel-Tresorerie-interactifs")
        report.append("")
        report.append("# Create and activate virtual environment (optional but recommended)")
        report.append("python -m venv venv")
        report.append("")
        report.append("# On Windows:")
        report.append(".\\venv\\Scripts\\Activate.ps1")
        report.append("# On Linux/Mac:")
        report.append("source venv/bin/activate")
        report.append("")
        report.append("# Install dependencies")
        report.append("pip install -r requirements.txt")
        report.append("")
        report.append("# Run the audit")
        report.append("python scripts/project_audit.py --output PROJECT_AUDIT.md")
        report.append("")
        report.append("# With custom max file size (default is 5 MB)")
        report.append("python scripts/project_audit.py --max-size-MB 10")
        report.append("```")
        report.append("")
        
        report.append("---")
        report.append("")
        report.append(f"*Report generated from: `{self.root_dir}`*")
        report.append("")
        
        # Write report to file
        output_path = self.root_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"✅ Report generated: {output_path}")
    
    def print_summary(self):
        """Print a summary to console."""
        print("\n" + "="*60)
        print("PROJECT AUDIT SUMMARY")
        print("="*60)
        print(f"Total Python files: {len(self.python_files)}")
        print(f"Sensitive files: {len(self.sensitive_files['databases']) + len(self.sensitive_files['logs']) + len(self.sensitive_files['env_files'])}")
        print(f"  - Databases: {len(self.sensitive_files['databases'])}")
        print(f"  - Logs: {len(self.sensitive_files['logs'])}")
        print(f"  - Environment: {len(self.sensitive_files['env_files'])}")
        print(f"Large files: {len(self.large_files)}")
        print(f"Circular imports: {len(self.circular_imports)}")
        print(f"Orphan modules: {len(self.orphan_modules)}")
        print(f"TODO/FIXME/XXX: {len(self.todos)}")
        print(f"Parse errors: {len(self.parse_errors)}")
        print("="*60)
        print()
    
    def run_audit(self, output_file: str):
        """Run the complete audit process."""
        print("\n🔍 Starting project audit...")
        print(f"📁 Root directory: {self.root_dir}")
        print(f"📏 Max file size: {self.max_size_bytes / (1024*1024):.1f} MB")
        print()
        
        self.scan_files()
        self.analyze_python_files()
        self.detect_circular_imports()
        self.identify_orphan_modules()
        self.analyze_dependencies()
        
        self.generate_report(output_file)
        self.print_summary()
        
        print(f"✅ Audit complete! Report saved to: {output_file}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Audit a Python project for potential issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/project_audit.py
  python scripts/project_audit.py --output PROJECT_AUDIT.md --max-size-MB 10

The script will analyze the project and generate a detailed report.
        """
    )
    
    parser.add_argument(
        '--output',
        default='PROJECT_AUDIT.md',
        help='Output file for the audit report (default: PROJECT_AUDIT.md)'
    )
    
    parser.add_argument(
        '--max-size-MB',
        type=float,
        default=5.0,
        help='Maximum file size in MB before flagging as large (default: 5.0)'
    )
    
    args = parser.parse_args()
    
    # Get the root directory (parent of scripts/)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    try:
        auditor = ProjectAuditor(root_dir, args.max_size_MB)
        auditor.run_audit(args.output)
        return 0
    except Exception as e:
        print(f"❌ Error during audit: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
