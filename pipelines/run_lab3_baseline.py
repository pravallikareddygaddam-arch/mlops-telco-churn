import subprocess
import sys


def run_script(script_path):
    print(f"\nRunning {script_path}...")
    subprocess.run(
        [sys.executable, script_path],
        check=True
    )


def main():
    print("=" * 50)
    print("LAB 3 - BASELINE MLOPS PIPELINE")
    print("=" * 50)

    # Step 1: Preprocessing
    run_script("src/preprocess.py")

    # Step 2: Model Training
    run_script("src/train.py")

    # Step 3: Model Evaluation
    run_script("src/evaluate.py")

    print("\n" + "=" * 50)
    print("LAB 3 BASELINE PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 50)


if __name__ == "__main__":
    main()