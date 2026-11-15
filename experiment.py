import csv
import ctypes
import platform
import re
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT / "build"
TIME_PATTERN = re.compile(r"Execution time:\s*([0-9.eE+-]+)\s*ms")
PF_AVX512F_INSTRUCTIONS_AVAILABLE = 41


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
        algorithms.append("cuda")
        print("[INFO] CUDA-capable NVIDIA GPU detected.")
    else:
        print("[WARNING] CUDA-capable NVIDIA GPU not detected. Skipping CUDA.")

    return algorithms


def run_simulation(executable: Path, algorithm: str, size: int, steps: int) -> str:
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
    return match.group(1)


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
                print(
                    f"Testing - Algorithm: {algorithm} | "
                    f"N: {size} | Steps: {step_count}"
                )
                elapsed = run_simulation(executable, algorithm, size, step_count)
                writer.writerow([algorithm, size, step_count, elapsed])


def main() -> None:
    executable = build_project()
    algorithms = detect_algorithms()
    experiment_dir = PROJECT_ROOT / "experiment"
    experiment_dir.mkdir(exist_ok=True)

    print("=== Running Experiment 1: Size Scaling ===")
    run_experiment(
        executable,
        algorithms,
        experiment_dir / "experiment1_size_scaling.csv",
        [100000, 1000000, 10000000, 100000000],
        [1000] * 4,
    )

    print("=== Running Experiment 2: Step Count Scaling ===")
    run_experiment(
        executable,
        algorithms,
        experiment_dir / "experiment2_steps_scaling.csv",
        [100000] * 4,
        [10000, 50000, 1000000, 5000000],
    )

    print("=== Experiments Complete! ===")
    print("Results saved to:")
    print(" - experiment/experiment1_size_scaling.csv")
    print(" - experiment/experiment2_steps_scaling.csv")


if __name__ == "__main__":
    main()
