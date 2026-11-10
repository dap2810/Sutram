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
| `javac` | javac 21.0.12.1 |
| `java` | openjdk version "21.0.12.1" 2026-08-18 |
| `zig` | **not found** |
| `python3` | Python 3.13.17 |
| `node` | v22.23.4 |
| `perl` | This is perl 5, version 38, subversion 2 (v5.38.2) built for x86_64-linux-gnu-thread-multi |
| `ruby` | ruby 3.3.6 (2024-11-05 revision 75015d4c1f) [x86_64-linux] |
| `nasm` | NASM version 2.16.01 |
| Sutram v315 (main) | Sutram 1.0 (v315) - sampurna sutra |
| Sutram v323 (staged tip) | Sutram 1.0 (v323) - sampurna sutra |

## Run time - wall time of the whole process, best of 5, milliseconds

| | empty | A | A2 | B | C0 | C | D0 | D | C: 10,000,000 additions, (C - C0) / 20 | D: 10,000,000 additions, (D - D0) / 20 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sutram v315 (main) | 0.4 | 8.1 | 20.2 | 10.8 | 48.6 | 844.8 | 1.0 | 291.5 | 39.81 | 14.53 |
| Sutram v323 (staged tip) | 0.5 | 12.0 | 22.1 | 9.4 | 46.2 | 820.9 | 0.9 | 276.7 | 38.73 | 13.79 |
| C, gcc (no flag) | 1.5 | 23.1 | 8.9 | 9.1 | 42.8 | 839.2 | 1.8 | 473.7 | 39.82 | 23.59 |
| C, gcc -O2 | 1.3 | 1.2 | 7.8 | 5.3 | 38.1 | 290.2 | 1.7 | 66.8 | 12.61 | 3.26 |
| C, gcc -O3 -march=native | 1.3 | 1.1 | 7.7 | 4.5 | 36.9 | 184.3 | 1.5 | 18.3 | 7.37 | 0.84 |
| C, clang (no flag) | 1.3 | 8.0 | 9.9 | 10.0 | 41.5 | 484.4 | 1.7 | 156.6 | 22.14 | 7.75 |
| C, clang -O2 | 1.4 | 1.4 | 8.7 | 5.8 | 39.6 | 213.8 | 1.7 | 23.6 | 8.71 | 1.09 |
| C++, g++ (no flag) |  |  |  | 20.5 | 74.7 | 1040.7 | 3.4 | 843.8 | 48.30 | 42.02 |
| C++, g++ -O2 |  |  |  | 11.6 | 53.2 | 318.6 | 2.2 | 65.7 | 13.27 | 3.17 |
| Rust, rustc (debug) | 1.5 | 39.2 | 38.4 | 15.9 | 124.9 | 1089.0 | 2.9 | 490.9 | 48.21 | 24.40 |
| Rust, rustc -C opt-level=3 (what --release sets) | 1.5 | 1.6 | 8.7 | 6.0 | 37.8 | 204.7 | 1.8 | 23.8 | 8.35 | 1.10 |
| Zig, zig build-exe -O ReleaseFast |  |  |  |  |  |  |  |  | | | *`zig` not found - not measured*
| Go, go build | 1.6 | 8.1 | 11.4 | 47.4 | 46.5 | 312.0 | 1.9 | 67.8 | 13.27 | 3.29 |
| Java, javac + java | 40.2 | 49.8 | 57.0 | 130.3 | 101.4 | 366.8 | 39.9 | 116.9 | 13.27 | 3.85 |
| JavaScript, node | 25.4 | 42.4 | 471.8 | 95.7 | 84.0 | 474.5 | 34.5 | 167.6 | 19.52 | 6.65 |
| Python, python3 | 12.9 | 661.6 | 1574.0 | 89.4 | 594.1 | 2316.2 | 18.9 | 971.0 | 86.11 | 47.61 |

- **Sutram v315 (main), scenario C with a `kosh` (every index checked) instead of raw `nirmmita` memory:** fill 53.0 ms, all 763.1 ms, 10,000,000 additions 35.51 ms.
- **Sutram v315 (main), scenario D with a `kosh` (every index checked) instead of raw `nirmmita` memory:** fill 0.7 ms, all 385.1 ms, 10,000,000 additions 19.22 ms.
- **Sutram v323 (staged tip), scenario C with a `kosh` (every index checked) instead of raw `nirmmita` memory:** fill 48.3 ms, all 692.5 ms, 10,000,000 additions 32.21 ms.
- **Sutram v323 (staged tip), scenario D with a `kosh` (every index checked) instead of raw `nirmmita` memory:** fill 0.7 ms, all 385.5 ms, 10,000,000 additions 19.24 ms.


## Compile time - wall time of the compiler, best of 5, milliseconds

"small" is scenario A's source (under 15 lines). "big" is one generated program in each language: 128 functions of six lines and a main that calls each once (1156 lines in Sutram), written by `gen_big.py`.

| | small | big | what the time covers |
|---|---:|---:|---|
| Sutram v315 (main) | 1.1 | 5.7 | source to executable, one process (no assembler, no linker) |
| Sutram v323 (staged tip) | 1.2 | 4.7 | source to executable, one process (no assembler, no linker) |
| C, gcc (no flag) | 34.5 | 82.4 | preprocess, compile, assemble, link |
| C, gcc -O2 | 37.2 | 51.2 | preprocess, compile, assemble, link |
| C, gcc -O3 -march=native | 40.2 | 53.8 | preprocess, compile, assemble, link |
| C, clang (no flag) | 64.6 | 76.6 | preprocess, compile, assemble, link |
| C, clang -O2 | 65.9 | 99.3 | preprocess, compile, assemble, link |
| Rust, rustc (debug) | 110.0 | 140.4 | compile and link |
| Rust, rustc -C opt-level=3 (what --release sets) | 117.0 | 136.5 | compile and link |
| Go, go build | 164.7 | 195.4 | `go build` of the one package (the standard library already built) |
| Java, javac + java | 504.6 | 745.2 | source to `.class` (no native code is made here; the JVM compiles when it runs) |

