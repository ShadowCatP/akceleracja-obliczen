#include "naive.hpp"
#include <iomanip>
#include <iostream>
#include <vector>

std::vector<double> run_naive_sim(int n, int steps) {
  std::vector<double> u_current(n, 0.0);
  std::vector<double> u_next(n, 0.0);

  u_current[n / 2] = 100.0; // initial heat source in the middle of the rod

  for (int t = 0; t < steps; ++t) {
    u_next[0] = 0.0;
    u_next[n - 1] = 0.0;

    for (int i = 1; i < n - 1; ++i) {
      u_next[i] = 0.5 * (u_current[i - 1] + u_current[i + 1]);
    }

    std::swap(u_current, u_next);
  }

  return u_current;
};
