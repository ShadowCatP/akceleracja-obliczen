#include "avx2.hpp"
#include <immintrin.h>
#include <vector>

std::vector<float> run_avx2_sim(int n, int steps, bool use_improved_formula) {
  std::vector<float> u_current(n, 0.0f);
  std::vector<float> u_next(n, 0.0f);

  u_current[n / 2] = 100.0f;

  __m256 v_half = _mm256_set1_ps(0.5f);
  __m256 v_center_coeff = _mm256_set1_ps(0.5f);
  __m256 v_neighbor_coeff = _mm256_set1_ps(0.25f);

  for (int t = 0; t < steps; ++t) {
    u_next[0] = 0.0f;
    u_next[n - 1] = 0.0f;

    int i = 1;

    // avx2 can hold 8 floats at a time
    for (; i <= n - 9; i += 8) {
      if (use_improved_formula) {
        __m256 v_center = _mm256_loadu_ps(&u_current[i]);
        __m256 v_left = _mm256_loadu_ps(&u_current[i - 1]);
        __m256 v_right = _mm256_loadu_ps(&u_current[i + 1]);

        __m256 v_sum_neighbors = _mm256_add_ps(v_left, v_right);

        __m256 term_center = _mm256_mul_ps(v_center, v_center_coeff);
        __m256 term_neighbors =
            _mm256_mul_ps(v_sum_neighbors, v_neighbor_coeff);

        __m256 v_res = _mm256_add_ps(term_center, term_neighbors);
        _mm256_storeu_ps(&u_next[i], v_res);
      } else {
        __m256 v_left = _mm256_loadu_ps(&u_current[i - 1]);
        __m256 v_right = _mm256_loadu_ps(&u_current[i + 1]);

        __m256 v_sum = _mm256_add_ps(v_left, v_right);
        __m256 v_res = _mm256_mul_ps(v_sum, v_half);

        _mm256_storeu_ps(&u_next[i], v_res);
      }
    }

    for (; i < n - 1; ++i) {
      if (use_improved_formula) {
        u_next[i] =
            0.5f * u_current[i] + 0.25f * (u_current[i - 1] + u_current[i + 1]);
      } else {
        u_next[i] = 0.5f * (u_current[i - 1] + u_current[i + 1]);
      }
    }

    std::swap(u_current, u_next);
  }

  return u_current;
}