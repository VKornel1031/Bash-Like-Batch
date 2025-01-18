# -----------------------------------------------------------------------------
# Bash-like-Batch Interpreter
# Copyright (c) 2025 VKornel1031 Reserved.
# This code is licensed under GNU 3.0 General Public License.
# -----------------------------------------------------------------------------

import os
import sys
import time
import shutil
import subprocess
import platform

# Store variables like 'set VAR=value'
variables = {}

# Store labels (e.g., ':main')
labels = {}

def parse_variables(command):
    """Replace Batch-style %VAR% with Python-compatible variable substitution."""
    for var, value in variables.items():
        command = command.replace(f"%{var}%", value)
    return command

def set_variable(command):
    """Handle 'set' command to assign variables."""
    global variables
    _, assignment = command.split("set ", 1)
    var_name, var_value = assignment.split("=", 1)
    variables[var_name.strip()] = var_value.strip()

def echo(command):
    """Handle 'echo' command."""
    message = command.replace("echo ", "").strip()
    print(message)

def cls(command):
    """Handle 'cls' command (clear the screen)."""
    os.system("cls" if os.name == "nt" else "clear")

def timeout(command):
    """Handle 'timeout' command. Simulate delay."""
    _, timeout_value = command.split("timeout ", 1)
    timeout_value = timeout_value.strip().split(" ")[0]
    time.sleep(int(timeout_value))

def dir(command):
    """Handle 'dir' command (list files in the current directory)."""
    options = command.split("dir ", 1)[1].strip()
    if "/s" in options:
        path = options.replace("/s", "").strip()
        for root, dirs, files in os.walk(path):
            for file in files:
                print(os.path.join(root, file))
    else:
        path = options if options else "."
        files = os.listdir(path)
        for file in files:
            print(file)

def del_file(command):
    """Handle 'del' command (delete file)."""
    _, file_name = command.split("del ", 1)
    file_name = file_name.strip()
    if os.path.exists(file_name):
        os.remove(file_name)
        print(f"Deleted: {file_name}")
    else:
        print(f"File not found: {file_name}")

def copy(command):
    """Handle 'copy' command (copy file)."""
    _, params = command.split("copy ", 1)
    src, dst = params.split(" ", 1)
    shutil.copy(src.strip(), dst.strip())
    print(f"Copied {src} to {dst}")

def mkdir(command):
    """Handle 'mkdir' command (make directory)."""
    _, dir_name = command.split("mkdir ", 1)
    dir_name = dir_name.strip()
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print(f"Directory created: {dir_name}")
    else:
        print(f"Directory already exists: {dir_name}")

def move(command):
    """Handle 'move' command (move file)."""
    _, params = command.split("move ", 1)
    src, dst = params.split(" ", 1)
    shutil.move(src.strip(), dst.strip())
    print(f"Moved {src} to {dst}")

def for_loop(command):
    """Handle 'for' loop command."""
    command = command.strip()
    _, loop_params, in_values, do_command = command.split(" ", 3)
    variable, values = loop_params.split(" in ", 1)
    values = values.strip().split(" ")
    for value in values:
        variables[variable] = value
        execute_command(do_command.strip())

# -----------------------------------------------------------------------------
# Bash-like-Batch Interpreter
# Copyright (c) 2025 VKornel1031 Reserved.
# This code is licensed under GNU 3.0 General Public License.
# -----------------------------------------------------------------------------


def if_statement(command):
    """Handle 'if' condition."""
    command = command.strip()
    condition, then_command = command.split(" then ", 1)
    if eval(condition):
        execute_command(then_command.strip())

def goto(command):
    """Handle 'goto' command (jump to a label)."""
    label_name = command.split("goto ", 1)[1].strip()
    if label_name in labels:
        return labels[label_name]  # Return the line number for the label
    else:
        print(f"Label '{label_name}' not found.")
        return None
    
def pause(command):
    """Handle 'pause' command (wait for user input)."""
    input("Press any key to continue...")

def call(command):
    """Handle 'call' command (call another script)."""
    _, script_name = command.split("call ", 1)
    script_name = script_name.strip()
    run_script(script_name)

def shift(command):
    """Handle 'shift' command (shifting command-line arguments)."""
    # Simulate shifting by removing the first argument
    if len(sys.argv) > 1:
        sys.argv.pop(1)
        print("Shifted arguments.")
    else:
        print("No arguments to shift.")

def ren(command):
    """Handle 'ren' command (rename a file)."""
    _, params = command.split("ren ", 1)
    old_name, new_name = params.split(" ", 1)
    os.rename(old_name.strip(), new_name.strip())
    print(f"Renamed {old_name.strip()} to {new_name.strip()}")

def execute_command(command, current_line):
    """Execute the command (parse and handle Batch commands)."""
    command = parse_variables(command)

    # Handle the command based on its first word (Batch command)
    if command.startswith("set "):
        set_variable(command)
    elif command.startswith("echo "):
        echo(command)
    elif command.startswith("cls"):
        cls(command)
    elif command.startswith("timeout"):
        timeout(command)
    elif command.startswith("dir"):
        dir(command)
    elif command.startswith("del"):
        del_file(command)
    elif command.startswith("copy"):
        copy(command)
    elif command.startswith("mkdir"):
        mkdir(command)
    elif command.startswith("move"):
        move(command)
    elif command.startswith("for"):
        for_loop(command)
    elif command.startswith("if"):
        if_statement(command)
    elif command.startswith("goto"):
        return goto(command)
    elif command.startswith("call"):
        call(command)
    elif command.startswith("shift"):
        shift(command)
    elif command.startswith("ren"):
        ren(command)

    elif command.startswith("pause"):
        pause(command)
    
    else:
        print(f"Unknown command: {command}")

    return current_line + 1

def run_script(file_path):
    """Run a .blb script file."""
    with open(file_path, "r") as script:
        lines = script.readlines()
    
    # Store labels with their line numbers
    global labels
    labels = {line[1:].strip(): idx for idx, line in enumerate(lines) if line.startswith(":")}
    
    current_line = 0
    while current_line < len(lines):
        line = lines[current_line].strip()
        
        # Skip empty lines or comments
        if not line or line.startswith("::") or line.startswith("rem"):
            current_line += 1
            continue
        
        # Execute the command and handle potential jumps (goto)
        next_line = execute_command(line, current_line)
        
        # If it's a goto, jump to the label
        if next_line is not None:
            current_line = next_line
        else:
            current_line += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <script.blb>")
        sys.exit(1)

    script_file = sys.argv[1]
    if not os.path.isfile(script_file):
        print(f"File not found: {script_file}")
        sys.exit(1)

    run_script(script_file)
# -----------------------------------------------------------------------------
# Bash-like-Batch Interpreter
# Copyright (c) 2025 VKornel1031 Reserved.
# This code is licensed under GNU 3.0 General Public License.
# -----------------------------------------------------------------------------
