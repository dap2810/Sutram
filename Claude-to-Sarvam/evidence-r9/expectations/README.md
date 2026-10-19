How the R9 goldens were computed (not from the compiler):

- `r9_guard_cells.out` / `r9_guard_cells2.out`: the values in these two `.expect` files were written
  by hand from each function's contract (Python one-liners for 321 - 123, 12 * 34, the 8 LE bytes of
  -2^63), then compared with the compiled run: they agree.
- `r9_alloc_failure.out`: 0 for each failed allocation (the documented contract), then 1, 1, 9.
- `r9_aadhar_alone.out`: 255 in base 16 is `ff`: 2 digits, 15 and 15.
- `tests/expect/236_guna_once.out`: f() is called once per guna (calls = 1, then 2 after the nested
  guna); the case values follow from the program text.
