# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "matplotlib>=3.11.2",
#     "pandas>=3.1.1",
# ]
# ///
import argparse
import csv
import ctypes
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Final

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT / "build"
TIME_PATTERN = re.compile(r"Execution time:\s*([0-9.eE+-]+)\s*ms")
EXPERIMENT_RUNS: Final[int] = 3
CUDA_THREADS_PER_BLOCK: Final[int] = 256
CUDA_FLOAT_BYTES: Final[int] = 4
PF_AVX512F_INSTRUCTIONS_AVAILABLE = 41
ALGORITHM_LABELS: Final[dict[str, str]] = {
    "naive": "Naiwny",
    "avx2": "AVX2",
    "avx512": "AVX-512",
    "cuda": "CUDA (Globalny)",
    "cuda-global": "CUDA (Globalny)",
    "cuda-shared": "CUDA (Współdzielony)",
}

EXPERIMENT_DIR: Final[Path] = PROJECT_ROOT / "experiment"
EXPERIMENT_1_PATH: Final[Path] = EXPERIMENT_DIR / "experiment1_size_scaling.csv"
EXPERIMENT_2_PATH: Final[Path] = EXPERIMENT_DIR / "experiment2_steps_scaling.csv"
EXPERIMENT_3_PATH: Final[Path] = EXPERIMENT_DIR / "experiment3_cuda_comparison.csv"
EXPERIMENT_4_PLOT_PATH: Final[Path] = EXPERIMENT_DIR / "experiment4_cuda_speedup.png"


def supports_avx512() -> bool:
    if platform.system() == "Windows":
        try:
            return bool(
                ctypes.windll.kernel32.IsProcessorFeaturePresent(
                    PF_AVX512F_INSTRUCTIONS_AVAILABLE
                )
            )
        except AttributeError:
            return False

    try:
        cpu_info = Path("/proc/cpuinfo").read_text().lower()
    except OSError:
        return False
    return "avx512f" in cpu_info


def build_project() -> Path:
    print("Building project in Release mode...")
    subprocess.run(
        ["cmake", "--build", str(BUILD_DIR), "--config", "Release"],
        cwd=PROJECT_ROOT,
        check=True,
    )

    candidates = [
        BUILD_DIR / "Release" / "main.exe",
        BUILD_DIR / "main.exe",
        BUILD_DIR / "main",
    ]
    for executable in candidates:
        if executable.is_file():
            return executable

    raise FileNotFoundError("Could not find compiled executable.")


def detect_algorithms() -> list[str]:
    algorithms = ["naive", "avx2"]

    if supports_avx512():
        algorithms.append("avx512")
        print("[INFO] AVX-512 instruction set detected on this CPU.")
    else:
        print("[WARNING] AVX-512 not detected on this CPU. Skipping AVX-512.")

    nvidia_smi = shutil.which("nvidia-smi")
    has_cuda = (
        nvidia_smi is not None
        and subprocess.run(
            [nvidia_smi, "-L"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )

    if has_cuda:
        algorithms.extend(["cuda-global", "cuda-shared"])
        print("[INFO] CUDA-capable NVIDIA GPU detected.")
    else:
        print("[WARNING] CUDA-capable NVIDIA GPU not detected. Skipping CUDA.")

    return algorithms


def run_simulation(executable: Path, algorithm: str, size: int, steps: int) -> float:
    result = subprocess.run(
        [str(executable), "-a", algorithm, "-n", str(size), "-s", str(steps)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    match = TIME_PATTERN.search(result.stdout)
    if match is None:
        raise RuntimeError(
            f"Could not parse execution time from output: {result.stdout!r}"
        )
    return float(match.group(1))


def run_experiment(
    executable: Path,
    algorithms: list[str],
    output_path: Path,
    sizes: list[int],
    steps: list[int],
) -> None:
    with output_path.open("w", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["Algorithm", "N", "Steps", "Time_ms"])

        for size, step_count in zip(sizes, steps):
            for algorithm in algorithms:
                elapsed_times = []
                for run_number in range(1, EXPERIMENT_RUNS + 1):
                    print(
                        f"Algorithm: {algorithm} | N: {size} | Steps: {step_count} "
                        f"| Run: {run_number}/{EXPERIMENT_RUNS}"
                    )
                    elapsed_times.append(
                        run_simulation(executable, algorithm, size, step_count)
                    )

                average_time = sum(elapsed_times) / EXPERIMENT_RUNS
                writer.writerow([algorithm, size, step_count, average_time])


def cuda_bytes_per_step(algorithm: str, size: int) -> int:
    blocks = (size + CUDA_THREADS_PER_BLOCK - 1) // CUDA_THREADS_PER_BLOCK

    if algorithm == "cuda-global":
        float_operations = 2 * (size - 2) + size
    elif algorithm == "cuda-shared":
        halo_reads = 2 * blocks - 2
        float_operations = size + halo_reads + size
    else:
        raise ValueError(f"Unsupported CUDA algorithm: {algorithm}")

    return float_operations * CUDA_FLOAT_BYTES


def run_bandwidth_experiment(
    executable: Path,
    output_path: Path,
    sizes: list[int],
    steps: list[int],
) -> None:
    algorithms = ["cuda-global", "cuda-shared"]

    with output_path.open("w", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(
            [
                "Algorithm",
                "N",
                "Steps",
                "Time_ms",
                "Bandwidth_GB_s",
                "Memory_Traffic_GB",
            ]
        )

        for size, step_count in zip(sizes, steps):
            for algorithm in algorithms:
                elapsed_times = []
                for run_number in range(1, EXPERIMENT_RUNS + 1):
                    print(
                        f"Algorithm: {algorithm} | N: {size} | Steps: {step_count} "
                        f"| Run: {run_number}/{EXPERIMENT_RUNS}"
                    )
                    elapsed_times.append(
                        run_simulation(executable, algorithm, size, step_count)
                    )

                average_time = sum(elapsed_times) / EXPERIMENT_RUNS
                total_bytes = cuda_bytes_per_step(algorithm, size) * step_count
                bandwidth_gb_s = total_bytes / (average_time / 1000) / 1e9
                writer.writerow(
                    [
                        algorithm,
                        size,
                        step_count,
                        average_time,
                        bandwidth_gb_s,
                        total_bytes / 1e9,
                    ]
                )


def generate_plots(experiment_dir: Path) -> None:

    if EXPERIMENT_1_PATH.exists():
        df1 = pd.read_csv(EXPERIMENT_1_PATH)

        plt.figure(figsize=(8, 5))
        for alg, group in df1.groupby("Algorithm"):
            plt.plot(
                group["N"] / 1000,
                group["Time_ms"] / 1000,
                marker="o",
                linewidth=2,
                label=ALGORITHM_LABELS.get(str(alg), str(alg)),
            )

        plt.xlabel("Rozmiar pręta (tysiące elementów, skala logarytmiczna)")
        plt.ylabel("Czas wykonania (s, skala logarytmiczna)")
        plt.title("Eksperyment 1: Skalowanie rozmiaru problemu (100 000 kroków)")
        plt.grid(True, which="both", linestyle="--", alpha=0.6)
        plt.legend()
        plt.tight_layout()

        plot1_path = experiment_dir / "experiment1_size_scaling.png"
        plt.savefig(plot1_path, dpi=300)
        plt.close()
        print(f"Saved plot: {plot1_path}")

    if EXPERIMENT_2_PATH.exists():
        df2 = pd.read_csv(EXPERIMENT_2_PATH)

        plt.figure(figsize=(8, 5))
        for alg, group in df2.groupby("Algorithm"):
            plt.plot(
                group["Steps"] / 1000,
                group["Time_ms"] / 1000,
                marker="o",
                linewidth=2,
                label=ALGORITHM_LABELS.get(str(alg), str(alg)),
            )

        plt.xlabel("Liczba kroków (tysiące)")
        plt.ylabel("Czas wykonania (s)")
        plt.title("Eksperyment 2: Skalowanie liczby kroków (N = 100 000)")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        plt.tight_layout()

        plot2_path = experiment_dir / "experiment2_steps_scaling.png"
        plt.savefig(plot2_path, dpi=300)
        plt.close()
        print(f"Saved plot: {plot2_path}")

    if EXPERIMENT_3_PATH.exists():
        df3 = pd.read_csv(EXPERIMENT_3_PATH)
        required_algorithms = {"cuda-global", "cuda-shared"}
        if not required_algorithms.issubset(set(df3["Algorithm"].unique())):
            print(
                f"Skipping plot: {EXPERIMENT_3_PATH} does not contain both CUDA "
                "implementations."
            )
            return

        if "Memory_Traffic_GB" not in df3.columns:
            df3["Memory_Traffic_GB"] = df3["Bandwidth_GB_s"] * df3["Time_ms"] / 1000

        plt.figure(figsize=(8, 5))
        for alg, group in df3.groupby("Algorithm"):
            plt.plot(
                group["Steps"],
                group["Memory_Traffic_GB"],
                marker="o",
                linewidth=2,
                label=ALGORITHM_LABELS.get(str(alg), str(alg)),
            )

        plt.xscale("log")
        plt.yscale("log")
        plt.xlabel("Liczba kroków")
        plt.ylabel("Ruch globalnej pamięci (GB)")
        plt.title("Eksperyment 3: Zużycie globalnej pamięci (N = 1 000 000)")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        plt.tight_layout()

        plot3_path = experiment_dir / "experiment3_cuda_comparison.png"
        plt.savefig(plot3_path, dpi=300)
        plt.close()
        print(f"Saved plot: {plot3_path}")

        speedup_data = df3.pivot_table(
            index="Steps",
            columns="Algorithm",
            values="Time_ms",
            aggfunc="mean",
        ).sort_index()
        speedup = speedup_data["cuda-global"] / speedup_data["cuda-shared"]

        plt.figure(figsize=(8, 5))
        plt.plot(
            speedup.index,
            speedup,
            marker="o",
            linewidth=2,
            label="Globalny / Współdzielony",
        )
        plt.axhline(
            1.0,
            color="gray",
            linestyle="--",
            linewidth=1,
            label="Brak przyspieszenia",
        )
        plt.xscale("log")
        plt.xlabel("Liczba kroków")
        plt.ylabel("Speedup (Globalny / Współdzielony)")
        plt.title("Eksperyment 4: Przyspieszenie Shared Memory (N = 1 000 000)")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        plt.tight_layout()
        plt.savefig(EXPERIMENT_4_PLOT_PATH, dpi=300)
        plt.close()
        print(f"Saved plot: {EXPERIMENT_4_PLOT_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run heat simulation experiments and generate performance plots."
    )
    parser.add_argument(
        "-p",
        "--plot-only",
        action="store_true",
        help="Skip running benchmarks and only regenerate plots from existing CSV files.",
    )
    parser.add_argument(
        "-e",
        "--experiment",
        choices=("1", "2", "3", "4", "all"),
        default="all",
        help="Experiment to run (default: all)",
    )
    args = parser.parse_args()

    EXPERIMENT_DIR.mkdir(exist_ok=True)

    if not args.plot_only and args.experiment != "4":
        executable = build_project()
        algorithms = detect_algorithms()

        if args.experiment in ("1", "all"):
            print("=== Running Experiment 1: Size Scaling ===")
            run_experiment(
                executable,
                algorithms,
                EXPERIMENT_1_PATH,
                [100000, 500000, 1000000, 5000000],
                [100000] * 4,
            )

        if args.experiment in ("2", "all"):
            print("=== Running Experiment 2: Step Count Scaling ===")
            run_experiment(
                executable,
                algorithms,
                EXPERIMENT_2_PATH,
                [100000] * 4,
                [100000, 500000, 1000000, 5000000],
            )

        if args.experiment in ("3", "all"):
            print("=== Running Experiment 3: Memory Bandwidth ===")
            run_bandwidth_experiment(
                executable,
                EXPERIMENT_3_PATH,
                [1000000] * 4,
                [1000000, 10000000, 100000000, 1000000000],
            )

        print("=== Experiments Complete! ===")
        print("Results saved to:")
        print(f" - {EXPERIMENT_1_PATH}")
        print(f" - {EXPERIMENT_2_PATH}")
        print(f" - {EXPERIMENT_3_PATH}")
        print(f" - {EXPERIMENT_4_PLOT_PATH}")

    generate_plots(EXPERIMENT_DIR)


if __name__ == "__main__":
    main()
