#include "avx512.hpp"
#include <algorithm>
#include <immintrin.h>
#include <vector>

std::vector<float> run_avx512_sim(int n, int steps, bool use_improved_formula) {
  std::vector<float> u_current(n, 0.0f);
  std::vector<float> u_next(n, 0.0f);

  u_current[n / 2] = 100.0f;

  __m512 v_half = _mm512_set1_ps(0.5f);
  __m512 v_center_coeff = _mm512_set1_ps(0.5f);
  __m512 v_neighbor_coeff = _mm512_set1_ps(0.25f);

  for (int t = 0; t < steps; ++t) {
    u_next[0] = 0.0f;
    u_next[n - 1] = 0.0f;

    int i = 1;

    // avx512 can hold up to 16 floats
    for (; i <= n - 17; i += 16) {
      if (use_improved_formula) {
        __m512 v_center = _mm512_loadu_ps(&u_current[i]);
        __m512 v_left = _mm512_loadu_ps(&u_current[i - 1]);
        __m512 v_right = _mm512_loadu_ps(&u_current[i + 1]);

        __m512 v_sum_neighbors = _mm512_add_ps(v_left, v_right);

        __m512 term_center = _mm512_mul_ps(v_center, v_center_coeff);
        __m512 term_neighbors =
            _mm512_mul_ps(v_sum_neighbors, v_neighbor_coeff);

        __m512 v_res = _mm512_add_ps(term_center, term_neighbors);
        _mm512_storeu_ps(&u_next[i], v_res);
      } else {
        __m512 v_left = _mm512_loadu_ps(&u_current[i - 1]);
        __m512 v_right = _mm512_loadu_ps(&u_current[i + 1]);

        __m512 v_sum = _mm512_add_ps(v_left, v_right);
        __m512 v_res = _mm512_mul_ps(v_sum, v_half);

        _mm512_storeu_ps(&u_next[i], v_res);
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