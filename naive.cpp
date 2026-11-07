#include "naive.hpp"
#include <iomanip>
#include <iostream>
#include <vector>

void run_naive_sim() {
  const int N = 10;
  const int steps = 5;
  const int field_width = 6;

  std::vector<double> u_current(N, 0.0);
  std::vector<double> u_next(N, 0.0);

  u_current[N / 2] = 100.0; // initial heat source in the middle of the rod

  std::cout << "Initial state (Algorithm - naive):\n";
  std::cout << std::setw(8) << "";
  for (double val : u_current) {
    std::cout << std::fixed << std::setprecision(1) << std::setw(field_width)
              << val << " ";
  }

  std::cout << std::endl << std::endl;

  for (int t = 0; t < steps; ++t) {
    u_next[0] = 0.0;
    u_next[N - 1] = 0.0;

    for (int i = 1; i < N - 1; ++i) {
      u_next[i] = 0.5 * (u_current[i - 1] + u_current[i + 1]);
    }

    std::swap(u_current, u_next);

    std::cout << "Step " << t + 1 << ": ";
    for (double val : u_current) {
      std::cout << std::fixed << std::setprecision(1) << std::setw(field_width)
                << val << " ";
    }
    std::cout << std::endl;
  }
};
