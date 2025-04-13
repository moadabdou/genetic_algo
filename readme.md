
# Genetic Text Evolution

This project is a minimal genetic algorithm that evolves random character sequences into a target string. It's written in pure Python with zero dependencies.

### 🧬 How It Works

The algorithm simulates evolution:

- **Initialization**: It starts with a population of random strings.
- **Selection**: The fittest individuals (those closest to the target) are chosen.
- **Crossover**: Pairs of parents are combined to produce offspring.
- **Mutation**: Offspring undergo slight mutations to introduce variation.
- **Repeat**: Over many generations, the population evolves toward the target.

The fitness score is based on how close each character is to the corresponding one in the target string, using a precomputed reference map.

### 🔡 Character Set

It supports a wide character space:

```
 abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!
```

(Space included at the beginning for natural text evolution.)

### ▶️ How to Run

Clone the repo and run the script:

```bash
python app.py
```

You'll see output like this:

```
0  310/620:   S5tzZ3Jv9zzWgP1!
...
1999  618/620:  Genetic Algorithm
```

Each line shows the generation number, current fitness vs. perfect fitness, and the best candidate string at that generation.

### 💡 Example Target

```python
eval("Genetic Algorithm", 100)
```

Want it to evolve something else? Just change the target string in the `eval()` function.

---

### 🛠️ Notes

- Population size and mutation behavior can be easily tweaked.
- Uses `random.normalvariate()` for smoother mutation control.
- Keeps the top 2 individuals each generation to retain strong genes (elitism).

---

### 🧪 Test

![alt](./assets/Screenshot%202025-04-09%20195638.png)

### 🎥 Watch  the algoritm generates the word "genome" in action 

<video src="./assets/genome_word_gen.mp4" width="320" height="240" controls></video>