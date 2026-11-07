#include "avx512.hpp"
#include <algorithm>
#include <immintrin.h>
#include <vector>

std::vector<double> run_avx512_sim(int n, int steps) {
  std::vector<double> u_current(n, 0.0);
  std::vector<double> u_next(n, 0.0);

  u_current[n / 2] = 100.0;

  __m512d v_half = _mm512_set1_pd(0.5);

  for (int t = 0; t < steps; ++t) {
    u_next[0] = 0.0;
    u_next[n - 1] = 0.0;

    int i = 1;

    // avx512 can hold up to 8 doubles
    for (; i <= n - 9; i += 8) {
      __m512d v_left = _mm512_loadu_pd(&u_current[i - 1]);
      __m512d v_right = _mm512_loadu_pd(&u_current[i + 1]);

      __m512d v_sum = _mm512_add_pd(v_left, v_right);
      __m512d v_res = _mm512_mul_pd(v_sum, v_half);

      _mm512_storeu_pd(&u_next[i], v_res);
    }

    for (; i < n - 1; ++i) {
      u_next[i] = 0.5 * (u_current[i - 1] + u_current[i + 1]);
    }

    std::swap(u_current, u_next);
  }

  return u_current;
}