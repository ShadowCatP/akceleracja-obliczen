#include "utils.hpp"
#include <iomanip>
#include <iostream>

void print_state(const std::string &label, const std::vector<float> &state) {
  std::ios_base::fmtflags original_flags = std::cout.flags();
  std::streamsize original_precision = std::cout.precision();

  const int field_width = 6;
  std::cout << label << ":\n";
  std::cout << std::setw(8) << "";
  for (float val : state) {
    std::cout << std::fixed << std::setprecision(1) << std::setw(field_width)
              << val << " ";
  }
  std::cout << std::endl << std::endl;

  std::cout.flags(original_flags);
  std::cout.precision(original_precision);
}