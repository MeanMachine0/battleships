## Virtual Environment Setup
### On Windows:
1. Open a terminal at the 'battleships' directory.
2. Execute the following commands: 
- python -m venv .venv
- .venv\scripts\activate
- pip install -r requirements.txt

### On MacOS/Linux:
1. Open a terminal at the 'battleships' directory.
2. Execute the following commands:
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r requirements.txt

## Testing
1. Open a terminal at the 'battleships' directory.
2. To run my tests, execute the following command: "pytest test.py", where 'test.py' is replaced with the name of the test file, e.g. 'test_components.py'.