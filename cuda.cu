#include "cuda.hpp"
#include <algorithm>
#include <cuda_runtime.h>
#include <iostream>
#include <vector>

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
  if (tid == 0 && i > 0) {
    s_data[0] = d_current[i - 1];
  }
  if (tid == blockDim.x - 1 && i < n - 1) {
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

std::vector<float> run_cuda_sim(int n, int steps, bool use_physical_formula) {
  std::vector<float> h_current(n, 0.0f);
  h_current[n / 2] = 100.0f;

  float *d_current = nullptr;
  float *d_next = nullptr;
  size_t bytes = n * sizeof(float);

  cudaMalloc(&d_current, bytes);
  cudaMalloc(&d_next, bytes);
  cudaMemcpy(d_current, h_current.data(), bytes, cudaMemcpyHostToDevice);

  int threadsPerBlock = 256;
  int blocksPerGrid = (n + threadsPerBlock - 1) / threadsPerBlock;

  for (int t = 0; t < steps; ++t) {
    heat_kernel_global<<<blocksPerGrid, threadsPerBlock>>>(
        d_current, d_next, n, use_physical_formula);
    std::swap(d_current, d_next);
  }

  cudaMemcpy(h_current.data(), d_current, bytes, cudaMemcpyDeviceToHost);
  cudaFree(d_current);
  cudaFree(d_next);

  return h_current;
}