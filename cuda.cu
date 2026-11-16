#include "cuda.hpp"
#include <algorithm>
#include <cuda_runtime.h>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void run_cuda(cudaError_t result) {
  if (result != cudaSuccess) {
    throw std::runtime_error(cudaGetErrorString(result));
  }
}

} // namespace

__global__ void heat_kernel_global(const float *d_current, float *d_next, int n,
                                   bool use_improved_formula) {
  int i = blockDim.x * blockIdx.x + threadIdx.x;

  if (i > 0 && i < n - 1) {
    if (use_improved_formula) {
      d_next[i] =
          0.5 * d_current[i] + 0.25 * (d_current[i - 1] + d_current[i + 1]);
    } else {
      d_next[i] = 0.5 * (d_current[i - 1] + d_current[i + 1]);
    }
  } else if (i == 0 || i == n - 1) {
    d_next[i] = 0.0;
  }
}

__global__ void heat_kernel_shared(const float *d_current, float *d_next, int n,
                                   bool use_improved_formula) {
  extern __shared__ float s_data[];

  int tid = threadIdx.x;
  int i = blockDim.x * blockIdx.x + tid;

  if (i < n) {
    s_data[tid + 1] = d_current[i];
  }
  if (tid == 0) {
    s_data[0] = i > 0 ? d_current[i - 1] : 0.0f;
  }
  if ((tid == blockDim.x - 1 || i == n - 2) && i < n - 1) {
    s_data[tid + 2] = d_current[i + 1];
  }

  __syncthreads();

  if (i > 0 && i < n - 1) {
    float center = s_data[tid + 1];
    float left = s_data[tid];
    float right = s_data[tid + 2];

    if (use_improved_formula) {
      d_next[i] = 0.5 * center + 0.25 * (left + right);
    } else {
      d_next[i] = 0.5 * (left + right);
    }
  } else if (i == 0 || i == n - 1) {
    d_next[i] = 0.0;
  }
}

std::vector<float> run_cuda_sim_impl(int n, int steps,
                                     bool use_improved_formula,
                                     bool use_shared_memory);

std::vector<float> run_cuda_global_sim(int n, int steps,
                                       bool use_improved_formula) {
  return run_cuda_sim_impl(n, steps, use_improved_formula, false);
}

std::vector<float> run_cuda_shared_sim(int n, int steps,
                                       bool use_improved_formula) {
  return run_cuda_sim_impl(n, steps, use_improved_formula, true);
}

std::vector<float> run_cuda_sim_impl(int n, int steps,
                                     bool use_improved_formula,
                                     bool use_shared_memory) {
  std::vector<float> h_current(n, 0.0f);
  h_current[n / 2] = 100.0f;

  float *d_current = nullptr;
  float *d_next = nullptr;
  size_t bytes = n * sizeof(float);

  run_cuda(cudaMalloc(&d_current, bytes));
  run_cuda(cudaMalloc(&d_next, bytes));
  run_cuda(
      cudaMemcpy(d_current, h_current.data(), bytes, cudaMemcpyHostToDevice));

  int threadsPerBlock = 256;
  int blocksPerGrid = (n + threadsPerBlock - 1) / threadsPerBlock;

  cudaEvent_t start_event;
  cudaEvent_t stop_event;
  run_cuda(cudaEventCreate(&start_event));
  run_cuda(cudaEventCreate(&stop_event));
  run_cuda(cudaEventRecord(start_event));

  for (int t = 0; t < steps; ++t) {
    if (use_shared_memory) {
      heat_kernel_shared<<<blocksPerGrid, threadsPerBlock,
                           (threadsPerBlock + 2) * sizeof(float)>>>(
          d_current, d_next, n, use_improved_formula);
    } else {
      heat_kernel_global<<<blocksPerGrid, threadsPerBlock>>>(
          d_current, d_next, n, use_improved_formula);
    }
    run_cuda(cudaGetLastError());
    std::swap(d_current, d_next);
  }

  run_cuda(cudaEventRecord(stop_event));
  run_cuda(cudaEventSynchronize(stop_event));

  float gpu_elapsed_ms = 0.0f;
  run_cuda(cudaEventElapsedTime(&gpu_elapsed_ms, start_event, stop_event));
  std::cout << "GPU kernel execution time: " << gpu_elapsed_ms << " ms"
            << std::endl;
  cudaEventDestroy(start_event);
  cudaEventDestroy(stop_event);

  run_cuda(
      cudaMemcpy(h_current.data(), d_current, bytes, cudaMemcpyDeviceToHost));
  run_cuda(cudaFree(d_current));
  run_cuda(cudaFree(d_next));

  return h_current;
}