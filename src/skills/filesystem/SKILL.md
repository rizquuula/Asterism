---
name: filesystem
description: Manages file operations and directory navigation. Use when users need to list files and directories, read file contents, write or modify files, create directories, or perform file system operations. Supports file encoding handling, permissions management, and backup operations.
---

# Filesystem

## Overview
The filesystem skill specializes in file operations and directory management. It provides powerful tools for navigating, reading, writing, and managing files within a project structure.

## Usage
This skill excels at:

1. **File Navigation**
   - Listing files and directories with various filtering options
   - Recursive directory traversal
   - File pattern matching and filtering

2. **File Operations**
   - Reading the contents of files with proper encoding handling
   - Writing new files or modifying existing ones
   - Creating directories as needed
   - Managing file permissions and access rights

3. **Data Management**
   - Creating backup copies when modifying important files
   - Using appropriate file paths (relative to project root)
   - Organizing information for other team members
   - Finding specific files efficiently

## Examples

### Basic File Operations
```python
# List files in a directory
list_files(directory_path)

# Read a file's contents
read_file(file_path)

# Write to a file
write_file(file_path, content)
```

### Directory Management
```python
# Create a new directory
create_directory(path)

# List files recursively
list_files(directory_path, recursive=True)
```

### File System Navigation
```python
# Find files matching a pattern
find_files(pattern, directory)

# Get file information
get_file_info(file_path)
```

## References
- See references/file-operations.md for detailed file operation guidelines
- See references/encoding-handling.md for file encoding best practices
- See references/permissions-guide.md for file permission management
