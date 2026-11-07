#include "naive.hpp"
#include <iostream>
#include <map>
#include <string>

enum class Algorithm { Naive, Unknown };

int main(int argc, char *argv[]) {
  std::string algo_name = "naive";

  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if ((arg == "-a" || arg == "--algorithm") && i + 1 < argc) {
      algo_name = argv[i + 1];
      i++;
    }
  }

  std::map<std::string, Algorithm> algo_map = {{"naive", Algorithm::Naive}};

  Algorithm selected_algo = Algorithm::Unknown;
  if (algo_map.find(algo_name) != algo_map.end()) {
    selected_algo = algo_map[algo_name];
  }

  switch (selected_algo) {
  case Algorithm::Naive:
    run_naive_sim();
    break;
  default:
    std::cerr << "Unknown algorithm: " << algo_name << std::endl;
    return 1;
  }

  return 0;
}