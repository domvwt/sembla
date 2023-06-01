# Sembla

Sembla is a software development framework designed to guide users through every step of the development process, from project scoping to code completion and testing. Sembla leverages OpenAI's ChatGPT technology to assist in generating various software development artifacts, such as project scopes, technical plans, code stubs, and tests.

## Table of Contents

- [Sembla](#sembla)
    - [Table of Contents](#table-of-contents)
    - [Features](#features)
    - [Requirements](#requirements)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Contributing](#contributing)
    - [License](#license)

## Features

- Project scoping: Define the scope and objectives of your project.
- Technical planning: Generate a technical plan based on the project scope.
- Code generation: Create code stubs and complete code.
- Testing: Develop unit tests for your code.
- Project configuration: Configure your project based on technical plans and code stubs.

## Requirements

- Python 3.8.1 or higher
- OpenAI API key

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/domvwt/sembla
   ```

2. Install the required packages:

   ```
   poetry install
   ```

3. Set up the OpenAI API key as an environment variable:

   ```
   export OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. Run Sembla:

   ```
   python -m sembla
   ```

2. Follow the prompts to define your project scope, generate technical plans, code stubs, and unit tests.

3. Save your generated files to the appropriate directory structure.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and submit a pull request.

## License

This project is currently closed source.
