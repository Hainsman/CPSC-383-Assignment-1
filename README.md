# A* Pathfinding Agent in AEGIS Simulation

## Overview
This project implements an **autonomous AI agent** that navigates a dynamic, grid-based disaster rescue simulation (AEGIS) using the **A\* search algorithm**.  
The agent’s objective is to safely and efficiently locate and rescue a survivor while minimizing energy consumption and avoiding hazardous terrain.

This work was completed as part of **CPSC 383: Explorations in Artificial Intelligence and Machine Learning** at the **University of Calgary**.

---

## Key Features
- **A\* Search Algorithm** with cost-aware path optimization
- **Admissible Octile Distance Heuristic** for 8-directional movement
- Handles **dynamic and partially observable environments**
- Avoids:
  - Killer cells (instant death)
  - Traps and high-cost terrain
  - Energy-depleting paths
- Supports **deterministic tie-breaking** for consistent path selection
- Automatically **replans paths** as new movement costs are revealed

---

## Technologies Used
- **Language:** Python 3  
- **Algorithms:** A\* Search, Heuristic Search  
- **Data Structures:** Priority Queue (`heapq`), Dictionaries  
- **Environment:** AEGIS Simulation Framework  

---

## How the Agent Works

### Heuristic Function
The agent uses **octile distance**, which is admissible for 8-connected grids and balances diagonal and straight movement efficiently.

### Neighbor Expansion
For each possible move, the agent:
- Checks map boundaries
- Avoids killer cells and traps
- Evaluates movement and destination costs
- Applies deterministic direction ordering for tie-breaking

### A* Search
The algorithm prioritizes nodes using:
```
f(n) = g(n) + h(n)
```
where:
- `g(n)` is the cumulative energy cost
- `h(n)` is the octile heuristic estimate

### Dynamic Replanning
In environments where move costs are hidden initially, the agent:
- Assumes optimistic default costs
- Reveals costs as it moves
- Recomputes the optimal path when new information becomes available

### Decision Loop
Each simulation round, the agent:
- Saves the survivor if on the target tile
- Locates the survivor if unseen
- Plans a safe path using A*
- Executes the next safest, lowest-cost move

---

## File Structure
```
.
├── main.py        # A* agent implementation
└── README.md      # Project documentation
```

---

## Running the Project
This project is designed to run **inside the AEGIS simulation environment**.

1. Install and configure AEGIS: https://aegis-game.github.io/docs/
2. Place `main.py` into the appropriate agent directory
3. Launch the AEGIS simulation
4. Run the simulation with the agent enabled

---

## Academic Context
- **Course:** CPSC 383 – Explorations in Artificial Intelligence and Machine Learning  
- **Topics:** Symbolic AI, Search Algorithms, Autonomous Agents, Pathfinding under Uncertainty  

This implementation follows course constraints and does not rely on external pathfinding libraries.

---

## Skills Demonstrated
- AI search and planning
- Heuristic design and evaluation
- Algorithmic optimization
- Decision-making under uncertainty
- Clean, well-documented Python code

---

## Author
**Hyunmin Kim**  
University of Calgary – B.Sc. Computer Science  

GitHub: https://github.com/Hainsman  
LinkedIn: https://linkedin.com/in/
