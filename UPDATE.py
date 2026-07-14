import subprocess
import os
import sys
from pathlib import Path

def git_pull(repo_path=None, branch=None, verbose=False):
    """
    Execute git pull with optional branch specification.
    
    Args:
        repo_path: Path to git repository (default: current directory)
        branch: Specific branch to pull (default: current branch)
        verbose: Print detailed output
    
    Returns:
        dict: Result with status, output, and error details
    """
    result = {
        'success': False,
        'stdout': '',
        'stderr': '',
        'returncode': -1,
        'message': ''
    }
    
    try:
        # Determine working directory
        cwd = repo_path if repo_path else os.getcwd()
        
        # Validate directory exists
        if not os.path.exists(cwd):
            result['message'] = f"Directory not found: {cwd}"
            return result
        
        # Check if it's a git repository
        git_dir = os.path.join(cwd, '.git')
        if not os.path.exists(git_dir):
            result['message'] = f"Not a git repository: {cwd}"
            return result
        
        # Build git pull command
        cmd = ['git', 'pull']
        if branch:
            cmd.extend(['origin', branch])
        
        # Execute git pull
        process = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Store results
        result['stdout'] = process.stdout
        result['stderr'] = process.stderr
        result['returncode'] = process.returncode
        
        # Check success
        if process.returncode == 0:
            result['success'] = True
            result['message'] = "Git pull completed successfully"
            print("✅ Updated Successfully Now Run your Scripts")
        else:
            result['message'] = f"Git pull failed with code: {process.returncode}"
            
    except FileNotFoundError:
        result['message'] = "Git is not installed or not in PATH"
    except Exception as e:
        result['message'] = f"Error: {str(e)}"
    
    return result

def main():
    """Example usage with argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Git pull script')
    parser.add_argument('--path', '-p', 
                       help='Path to git repository (default: current directory)')
    parser.add_argument('--branch', '-b',
                       help='Branch to pull (default: current branch)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress output')
    
    args = parser.parse_args()
    
    # Execute git pull
    result = git_pull(
        repo_path=args.path,
        branch=args.branch,
        verbose=not args.quiet
    )
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)

if __name__ == "__main__":
    main()
