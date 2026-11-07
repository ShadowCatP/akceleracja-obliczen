#include "avx2.hpp"
#include <immintrin.h>
#include <vector>

std::vector<double> run_avx2_sim(int n, int steps) {
  std::vector<double> u_current(n, 0.0);
  std::vector<double> u_next(n, 0.0);

  u_current[n / 2] = 100.0;

  __m256d v_half = _mm256_set1_pd(0.5);

  for (int t = 0; t < steps; ++t) {
    u_next[0] = 0.0;
    u_next[n - 1] = 0.0;

    int i = 1;

    // avx2 can hold 4 doubles at a time
    for (; i < n - 5; i += 4) {
      __m256d v_left = _mm256_loadu_pd(&u_current[i - 1]);
      __m256d v_right = _mm256_loadu_pd(&u_current[i + 1]);

      __m256d v_sum = _mm256_add_pd(v_left, v_right);
      __m256d v_res = _mm256_mul_pd(v_sum, v_half);

      _mm256_storeu_pd(&u_next[i], v_res);
    }

    for (; i < n - 1; ++i) {
      u_next[i] = 0.5 * (u_current[i - 1] + u_current[i + 1]);
    }

    std::swap(u_current, u_next);
  }

  return u_current;
}