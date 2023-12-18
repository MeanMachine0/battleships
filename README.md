# Self-Assessment - Extra Features
## AI Attacking Algorithm
- Probabilistic.
- Median: 42 attacks.
- Standard Deviation: ~10.2 attacks.
- Tested against 100,000 random boards.
- See in main.py within the 'AI' Class.

## AI Ship Placement
- Based on the attacking algorithm, see 'analysis.ipynb' for more information.
- Algorithm is located in 'main.py' within the AI class as a function, called 'set_board'.

## Testing
- 'test_main.py'
- 'test_components.py'
- My tests were made using pytest. To run them, execute:
"pytest test_filename.py" (where 'filename' is replaced by the name of the file you want to test).

# Executing the Project
- Install Python 3.11.4 and set it as your interpreter in your IDE.
- When executing any commands mentioned, do so at the 'battleships' directory (project root directory).
## Virtual Environment Setup
### Windows
Execute: 
- python -m venv .venv
- .venv\scripts\activate
- pip install -r requirements.txt

### MacOS/Linux
Execute:
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r requirements.txt

### For All, Afterwards
Select the virtual environment's Python installation as your IDE's interpreter.

## Running and Using the Application
### CLI
#### Simple Game
- Execute: "python components.py"
- Type the coordinates you would like to attack using a letter followed by a number, like so: 'A1' or 'a1'.
- Press enter to execute your attack.
- Execute attacks until you have sunk all of the opponents' ships.

#### Game Against an Opponent
- To set your own board configuration, edit the file called "placement.json", adhering to the example shown in the file.
- Execute: "python mp_game_engine.py" (where 'python' is replaced by your respective environment variable).
- Type the coordinates you would like to attack using a letter followed by a number, like so: 'A1' or 'a1'.
- Press enter to execute your attack.
- See your updated board after every attack, showing your ships marked by an 'X' and empty spots marked as '-'.
- Execute attacks until the game is over.

### Web Interface
- Execute: "python main.py" (where 'python' is replaced by your respective environment variable).
- Go to http://127.0.0.1:5000/ in a browser.
- Rotate your ships using the 'R' key and place all five of them using M1/LMB.
- Push the 'Send Game' button using M1/LMB.
- Attack (using M1/LMB) on the left hand board against the AI opponent until the game is over.
- Refresh the page to restart the game.

# Boring Stuff
- Author: Marcus Carter
- License: this project is licensed under the MIT license. See the file called 'LICENSE.txt' in the battleships directory for more information.
- Dependencies: see the file called "requirements.txt".