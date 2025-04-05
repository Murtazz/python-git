# Python Git Implementation (WYAG)

This repository contains a minimal implementation of a Git-like version control system written in Python. The project is inspired by the "Write Yourself a Git" (WYAG) tutorial and serves as a learning tool to understand the internals of Git.

## Features

- **Initialize a Repository**: Create a new Git repository.
- **Read Objects**: Display the content of Git objects (blobs, commits, tags, trees).
- **Hash Objects**: Compute the SHA-1 hash of a file and optionally store it as a blob in the repository.
- **Commit Log**: Display the history of a given commit (partially implemented).

## Project Structure

```
.gitignore
[`git_commands.py`](git_commands.py )
[`GitObject.py`](GitObject.py )
[`GitRepository.py`](GitRepository.py )
[`libwyag.py`](libwyag.py )
wyag
.vscode/
    settings.json
```

### Key Files

- **[wyag](wyag)**: Entry point for the application. Runs the `main` function from `libwyag.py`.
- **[libwyag.py](libwyag.py)**: Main script that defines the command-line interface and dispatches commands.
- **[GitRepository.py](GitRepository.py)**: Contains the `GitRepository` class and utility functions for managing repositories.
- **[GitObject.py](GitObject.py)**: Defines Git object types (e.g., blobs, commits) and functions for reading, writing, and hashing objects.
- **[git_commands.py](git_commands.py)**: Implements commands like `init`, `cat-file`, `hash-object`, and `log`.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/python-git.git
   cd python-git
   ```

2. Make the `wyag` script executable:
   ```sh
   chmod +x wyag
   ```

3. Run the script:
   ```sh
   ./wyag <command> [options]
   ```

## Usage

### Initialize a Repository
```sh
./wyag init <directory>
```
Creates a new Git repository in the specified directory.

### Display Object Content
```sh
./wyag cat-file <type> <object>
```
Displays the content of a Git object (e.g., blob, commit, tag, tree).

### Hash a File
```sh
./wyag hash-object [-t <type>] [-w] <file>
```
Computes the SHA-1 hash of a file and optionally writes it as a blob to the repository.

### Display Commit Log
```sh
./wyag log <commit>
```
Displays the history of a given commit (in Graphviz format).

## Development

### Adding New Commands
To add a new command:
1. Define the command in `libwyag.py` by adding a new subparser.
2. Implement the command logic in `git_commands.py`.

### Testing
You can test the functionality by running the commands in a terminal. Ensure that `.gitignore` excludes unnecessary files like `__pycache__` and `.vscode/settings.json`.

## License

This project is for educational purposes and does not include a license. Feel free to use it as a learning resource.

## Acknowledgments

- Inspired by the "Write Yourself a Git" (WYAG) tutorial.