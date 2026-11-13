#include "avx2.hpp"
#include "avx512.hpp"
#include "naive.hpp"
#include "utils.hpp"
#include <chrono>
#include <functional>
#include <iostream>
#include <map>
#include <string>

enum class Algorithm { Naive, Unknown };

int main(int argc, char *argv[]) {
  std::string algo_name = "naive";
  int N = 10;
  int steps = 5;
  bool verbose = false;
  bool improved_formula = false;

  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if ((arg == "-a" || arg == "--algorithm") && i + 1 < argc) {
      algo_name = argv[i + 1];
      i++;
    } else if ((arg == "-n" || arg == "--size") && i + 1 < argc) {
      N = std::stoi(argv[i + 1]);
      i++;
    } else if ((arg == "-s" || arg == "--steps") && i + 1 < argc) {
      steps = std::stoi(argv[i + 1]);
      i++;
    } else if ((arg == "-v" || arg == "--verbose")) {
      verbose = true;
    } else if ((arg == "-i" || arg == "--improved-formula")) {
      improved_formula = true;
    }
  }

  if (N < 3) {
    std::cerr << "rod size n must be at lest 3" << std::endl;
    return 1;
  }

  std::map<std::string, std::function<std::vector<double>(int, int, bool)>>
      algo_map = {{"naive", run_naive_sim},
                  {"avx512", run_avx512_sim},
                  {"avx2", run_avx2_sim}};

  if (algo_map.find(algo_name) == algo_map.end()) {
    std::cerr << "unkown algorithm: " << algo_name << std::endl;
    std::cerr << "usage: " << argv[0]
              << " [-a algorithm] [-n size] [-s steps] [-v]" << std::endl;
    return 1;
  }

  if (verbose) {
    std::vector<double> init_state(N, 0.0);
    init_state[N / 2] = 100.0;
    print_state("Initial state (Algorithm - " + algo_name + ")", init_state);
  }

  auto start_time = std::chrono::high_resolution_clock::now();

  std::vector<double> final_state =
      algo_map[algo_name](N, steps, improved_formula);

  auto end_time = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double, std::milli> elapsed = end_time - start_time;

  if (verbose) {
    print_state("Final state (" + algo_name + ", N=" + std::to_string(N) +
                    ", steps=" + std::to_string(steps) + ")",
                final_state);
  }

  std::cout << "Execution time: " << elapsed.count() << " ms" << std::endl;

  return 0;
}