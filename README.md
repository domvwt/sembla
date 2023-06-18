# Sembla

Sembla is a functional framework for developing AI agent systems.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and submit a pull request.

## Flowchart

```mermaid
graph TB
  InitialState(Initial State) --> PerceiveAndAct
  subgraph "Agent System"
    PerceiveAndAct(Perception Action Cycle) --> Evaluate
    Evaluate{Goal Met?} -- No --> PerceiveAndAct
  end
    Evaluate -- Yes --> FinalState(Final State)
```

## License

This project is currently closed source.
