## What this machine has

| tool | |
|---|---|
| `gcc` | gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0 |
| `cc` | cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0 |
| `clang` | Ubuntu clang version 18.1.3 (1ubuntu1) |
| `g++` | g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0 |
| `rustc` | rustc 1.97.0 (2d8144b78 2026-07-07) |
| `cargo` | cargo 1.97.0 (c980f4866 2026-06-30) |
| `go` | go version go1.24.7 linux/amd64 |
| `javac` | javac 21.0.12 (patch 1) |
| `java` | openjdk version "21.0.12 (patch 1)" 2026-08-18 |
| `zig` | **not found** |
| `python3` | Python 3.13.17 |
| `node` | v22.23.4 |
| `perl` |  |
| `ruby` | ruby 3.3.6 (2024-11-05 revision 75015d4c1f) [x86_64-linux] |
| `nasm` | NASM version 2.16.01 |
| Sutram v315 (main) | Sutram 1.0 (v315) - sampurna sutra |
| Sutram v323 (staged tip) | Sutram 1.0 (v323) - sampurna sutra |

## Run time - wall time of the whole process, best of 5, milliseconds

| | empty | A | A2 | B | C0 | C | D0 | D | C: 10,000,000 additions, (C - C0) / 20 | D: 10,000,000 additions, (D - D0) / 20 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sutram v315 (main) | 0.4 | 7.7 | 20.2 | 8.2 | 46.1 | 846.6 | 1.1 | 283.9 | 40.03 | 14.14 |
| Sutram v323 (staged tip) | 0.5 | 7.9 | 20.0 | 9.0 | 45.2 | 836.4 | 0.9 | 278.4 | 39.56 | 13.87 |
| C, gcc (no flag) | 1.2 | 25.3 | 10.4 | 8.3 | 41.7 | 787.8 | 1.6 | 471.5 | 37.30 | 23.50 |
| C, gcc -O2 | 1.2 | 1.3 | 7.9 | 5.1 | 38.0 | 282.1 | 1.5 | 66.1 | 12.21 | 3.23 |
| C, gcc -O3 -march=native | 1.3 | 1.3 | 7.8 | 5.0 | 36.2 | 187.4 | 1.6 | 17.5 | 7.56 | 0.80 |
| C, clang (no flag) | 1.3 | 8.0 | 9.6 | 7.2 | 40.1 | 505.2 | 1.6 | 156.3 | 23.25 | 7.74 |
| C, clang -O2 | 1.3 | 1.3 | 8.1 | 5.7 | 37.8 | 221.1 | 1.6 | 23.9 | 9.17 | 1.12 |
| C++, g++ (no flag) |  |  |  | 21.4 | 77.9 | 1164.1 | 2.8 | 829.8 | 54.31 | 41.35 |
| C++, g++ -O2 |  |  |  | 11.5 | 57.2 | 301.7 | 2.4 | 66.3 | 12.23 | 3.20 |
| Rust, rustc (debug) | 1.5 | 39.0 | 38.8 | 16.4 | 124.0 | 1036.3 | 2.7 | 461.7 | 45.61 | 22.95 |
| Rust, rustc -C opt-level=3 (what --release sets) | 1.7 | 1.5 | 8.7 | 6.0 | 36.0 | 218.7 | 1.7 | 23.4 | 9.13 | 1.09 |
| Zig, zig build-exe -O ReleaseFast |  |  |  |  |  |  |  |  | | | *`zig` not found - not measured*
| Go, go build | 1.6 | 7.9 | 11.2 | 53.8 | 37.7 | 233.2 | 1.8 | 66.0 | 9.78 | 3.21 |
| Java, javac + java | 38.3 | 47.3 | 50.2 | 112.5 | 95.7 | 363.6 | 43.3 | 116.4 | 13.39 | 3.65 |
| JavaScript, node | 23.9 | 40.2 | 437.6 | 93.0 | 76.1 | 489.8 | 31.9 | 167.7 | 20.68 | 6.79 |
| Python, python3 | 13.5 | 660.9 | 1635.5 | 87.5 | 589.0 | 2273.1 | 18.4 | 964.8 | 84.21 | 47.32 |

- **Sutram v315 (main), scenario C with a `kosh` (every index checked) instead of raw `nirmmita` memory:** fill 49.1 ms, all 770.5 ms, 10,000,000 additions 36.07 ms.
- **Sutram v315 (main), scenario D with a `kosh` (every index checked) instead of raw `nirmmita` memory:** fill 0.8 ms, all 391.8 ms, 10,000,000 additions 19.55 ms.
- **Sutram v323 (staged tip), scenario C with a `kosh` (every index checked) instead of raw `nirmmita` memory:** fill 48.7 ms, all 682.8 ms, 10,000,000 additions 31.71 ms.
- **Sutram v323 (staged tip), scenario D with a `kosh` (every index checked) instead of raw `nirmmita` memory:** fill 0.8 ms, all 391.3 ms, 10,000,000 additions 19.52 ms.


## Compile time - wall time of the compiler, best of 5, milliseconds

"small" is scenario A's source (under 15 lines). "big" is one generated program in each language: 128 functions of six lines and a main that calls each once (1156 lines in Sutram), written by `gen_big.py`.

| | small | big | what the time covers |
|---|---:|---:|---|
| Sutram v315 (main) | 1.1 | 4.0 | source to executable, one process (no assembler, no linker) |
| Sutram v323 (staged tip) | 0.9 | 4.1 | source to executable, one process (no assembler, no linker) |
| C, gcc (no flag) | 34.1 | 83.3 | preprocess, compile, assemble, link |
| C, gcc -O2 | 37.9 | 51.7 | preprocess, compile, assemble, link |
| C, gcc -O3 -march=native | 41.7 | 53.8 | preprocess, compile, assemble, link |
| C, clang (no flag) | 62.7 | 79.6 | preprocess, compile, assemble, link |
| C, clang -O2 | 65.8 | 98.6 | preprocess, compile, assemble, link |
| Rust, rustc (debug) | 105.6 | 143.9 | compile and link |
| Rust, rustc -C opt-level=3 (what --release sets) | 112.4 | 135.5 | compile and link |
| Go, go build | 164.1 | 198.1 | `go build` of the one package (the standard library already built) |
| Java, javac + java | 498.0 | 700.8 | source to `.class` (no native code is made here; the JVM compiles when it runs) |

