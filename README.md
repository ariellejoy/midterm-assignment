# Project Description 
This project is an advanced REPL (Read-Eval-Print Loop) calculator meant to satisfy the requirements of the midterm assignment. As part of the calculator, an end user can put in one of the available operations (EX: add, mulitply, modulus, absolute difference) and 2 numerical values to get the appropriate result in the terminal interactively. If the user inputs the wrong values or the calculator is unable to run the calculation, then a related error should show within the user interface. Users can also manage their calculation history. 

# Usage Guide 
The calculator supports multiple math operations, history management, undo/redo functionality, saving/loading calculation history, and logging. 

Please follow the below instructions under **Project Setup** to ensure that your system is prepped to run the application. 

Once the application has been started, a welcome message will appear, prompting the end user to interact with the terminal. To perform a calculation, enter the operation followed by 2 numerical values as such: <operation><num1><num2>

**Supported Operations include:**
| operation | function | example |
| --- | --- | --- |
| add | adds two numbers | add 1 1 |
| subtract | subtracts the second number from the first number | subtract 5 3 |
| multiply | multiplies two numbers | multiply 2 4 |
| divide | divides the first number by the second number | divide 10 2 |
| power | raises the first number to the power of the second number | power 2 3 |
| root | calculates the root of the two numbers | root 16 2 |
| modulus | returns the remainder after division | modulus 10 3 |
| int_divide | performs integer division | int_divide 10 3 |
| percentage | returns the percentage of two numbers by dividing the first number by the second number and multiplying by 100 | percentage 50 20 |
| abs_diff | calculates absolute difference | abs_diff 5 10 |

The user can also input one of the following commands for managing the app and it's history: 
- help = displays list of available operations and instructions
- history = displays calculation history 
- undo = undoes most recent calculation 
- redo = redoes most recent calculation 
- clear = clears calculation history
- save = saves history to CSV file 
- load = loads history from CSV file 
- exit = closes app

As the user interacts with the calculator, they may run into the following messages for common errors: 
- Invalid input 
- Division by zero
- Save/load failure
- Unsupported operaton 
- Unexpected exit 

Some color coding has also been added to the outputs to ensure the user is aware of their state. 
EXAMPLE: successful calculations should always be green
EXAMPLE: error messages should be red
There are other stylings applied to differentiate headings for things such as the help content and history, as well.

# Project Setup
## Installing Homebrew (MAC USERS ONLY)
> Skip this step if you're on Windows.

Homebrew is a package manager for macOS and should be used to easily install Git, Python, etc. for the project

**Installing Homebrew:**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
**Verifying Homebrew:**
```bash
brew --version
```

Note: If you see a version number, you're good to go.

## Installing and Configuring Git
#### Instaling Git
**FOR MAC (using Homebrew)**
```bash
brew install git
```
**FOR WINDOWS**
Download and install [Git for Windows](https://git-scm.com/download/win).  
Accept the default options during installation.

**Verify Git:**
```bash
git --version
```

## Generating SSH Keys and Connecting to GitHub
> Only do this once per machine. As a result, you may already have this set up on your machine from previous work.

1. Generate a new SSH key:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

(Press Enter at all prompts.)

2. Start the SSH agent:
```bash
eval "$(ssh-agent -s)"
```

3. Add the SSH private key to the agent:
```bash
ssh-add ~/.ssh/id_ed25519
```

4. Copy your SSH public key:
**FOR MAC**
```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```
**FOR WINDOWS**
```bash
cat ~/.ssh/id_ed25519.pub | clip
```

5. Add the key to your GitHub account:
   - Go to [GitHub SSH Settings](https://github.com/settings/keys)
   - Click **New SSH Key**, paste the key, save.

6. Test the connection:
```bash
ssh -T git@github.com
```

7. You should see a success message.


## Cloning the Repository

Now you can safely clone the calculator assignment:
```bash
git clone <repository-url>
cd <repository-directory>
```

## Ensuring that Python 3.10+ is installed
#### Install Python

**FOR MAC (Homebrew)**
```bash
brew install python
```
**FOR WINDOWS**

Download and install [Python for Windows](https://www.python.org/downloads/).  
Make sure you **check the box** `Add Python to PATH` during setup.

**Verify Python**
```bash
python3 --version
```
or
```bash
python --version
```

## Setting up your virtual environment
In order to set up your virtual environment, follow the below steps: 
1. Ensure that the project folder has been cloned to your local environment using SSH 
2. Open said project folder in VSCODE using:
```
code . 
```
3. Once in VSCode, open a new terminal to run the following command in order to create the virtual environment: 
FOR MAC (what I used)-
```
python3 -m venv .venv
```
FOR WINDOWS-
```
python -m venv .venv 
```
4. After it has been created, you can start your virtual environment by running the following: 
FOR MAC (what I used)- 
```
source venv/bin/activate
```
FOR WINDOWS-
``` 
venv\Scripts\activate.bat 
```
5. To know that the virtual environment has been started, you should see "(venv)" at the start of your terminal prompt line

## Installing packages for the project
To ensure that the required dependencies are installed, run the following command: 
```
pip install -r requirements.txt
```
## Running the Project
Since we are not using Docker, use the following command to run the REPL interface:
```bash
python main.py
```
# Configuration Setup 
Configuration setup included adding a env file in the project directory to store the environment variables required for the project's run. For this project, this included: 
- base directories
- history settings
and 
- calculation settings

This is included in the .gitignore to prevent them from being commited for version control.

# Testing Instructions 
In order to run tests, a user will need to ensure that you are running the project in a virtual environment and all requirements + dependencies have been added per the above instructions.

To run the unit tests, enter the following in the terminal: 
```
pytest
```
This command will run your test files, which will return a complete output with successful tests, as well as any errors/failures that come up. Traceback calls are also helpful to determine how to fix these errors and failed tests. 

A user can check test coverage through the pytest output! A table will be displayed that shows the overall coverage and what lines do not have any tests covering them. You can better view the code by opening the **index.html** file from the htmlcov folder in the browser. **For this project, the required test coverage is 90%**

# CI/CD Info
GitHub Actions (from now on refered to as GA) is the native CI/CD platform built within GitHub. GA's purpose is to automate workflows and streamline tests where the codebase is stored. GA is dictated by the **.yml** file that lives within the .github folder, which describes specific tasks that need to be executed as part of the workflows.

A user can also see how GA evolves as the code is updated overtime. 