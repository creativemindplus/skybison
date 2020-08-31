#!/usr/bin/env python3
import os
import subprocess
import sys
import unittest
from tempfile import TemporaryDirectory


class OptionsTest(unittest.TestCase):
    def test_I_option_sets_isolated_no_user_site_ignore_environment_flags(self):
        result = subprocess.run(
            [sys.executable, "-I", "-c", "import sys;print(sys.flags)"],
            check=True,
            capture_output=True,
        )
        self.assertIn(b"isolated=1", result.stdout)
        self.assertIn(b"ignore_environment=1", result.stdout)
        self.assertIn(b"no_user_site=1", result.stdout)

    def test_O_option_increments_optimize_flag(self):
        result = subprocess.run(
            [sys.executable, "-OO", "-OOO", "-c", "import sys;print(sys.flags)"],
            check=True,
            capture_output=True,
        )
        self.assertIn(b"optimize=5", result.stdout)

    def test_B_option_sets_dont_write_bytecode_flag(self):
        result = subprocess.run(
            [sys.executable, "-B", "-c", "import sys;print(sys.flags)"],
            check=True,
            capture_output=True,
        )
        self.assertIn(b"dont_write_bytecode=1", result.stdout)

    def test_PYTHONHASHSEED_sets_fixed_seed(self):
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = "0"
        code = "print(hash('abcdefghijkl'));import sys;print(sys.flags)"
        result0 = subprocess.run(
            [sys.executable, "-c", code], check=True, capture_output=True, env=env
        )
        result1 = subprocess.run(
            [sys.executable, "-c", code], check=True, capture_output=True, env=env
        )
        self.assertEqual(result0.stdout, result1.stdout)
        self.assertIn(b"hash_randomization=0", result0.stdout)

    def test_PYTHONHASHSEED_sets_random_seed(self):
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = "random"
        code = "print(hash('abcdefghijkl'));import sys;print(sys.flags)"
        result0 = subprocess.run(
            [sys.executable, "-c", code], check=True, capture_output=True, env=env
        )
        result1 = subprocess.run(
            [sys.executable, "-c", code], check=True, capture_output=True, env=env
        )
        self.assertNotEqual(result0.stdout, result1.stdout)
        self.assertIn(b"hash_randomization=1", result0.stdout)

    def test_PYTHONHASHSEED_unset_sets_random_seed(self):
        code = "print(hash('abcdefghijkl'));import sys;print(sys.flags)"
        result0 = subprocess.run(
            [sys.executable, "-c", code], check=True, capture_output=True
        )
        result1 = subprocess.run(
            [sys.executable, "-c", code], check=True, capture_output=True
        )
        self.assertNotEqual(result0.stdout, result1.stdout)
        self.assertIn(b"hash_randomization=1", result0.stdout)

    def test_PYTHONPATH_sets_sys_path(self):
        with TemporaryDirectory() as tempdir:
            path0 = os.path.abspath(os.path.join(tempdir, "foo"))
            path1 = os.path.abspath(os.path.join(tempdir, "bar"))
            env = dict(os.environ)
            env["PYTHONPATH"] = f"{path0}:{path1}"
            code = "import sys;print('sys.path: ' + str(sys.path))"
            result = subprocess.run(
                [sys.executable, "-c", code],
                check=True,
                capture_output=True,
                env=env,
                encoding="utf-8",
            )
            self.assertIn(f"sys.path: ['', '{path0}', '{path1}'", result.stdout)

    def test_PYTHONWARNINGS_adds_warnoptions(self):
        env = dict(os.environ)
        env["PYTHONWARNINGS"] = "foo,bar"
        code = "import sys;print('warnoptions: ' + str(sys.warnoptions))"
        result = subprocess.run(
            [sys.executable, "-W", "baz", "-W", "bam", "-c", code],
            check=True,
            capture_output=True,
            env=env,
        )
        self.assertIn(b"warnoptions: ['foo', 'bar', 'baz', 'bam']", result.stdout)

    def test_S_option_sets_no_site_flag(self):
        result = subprocess.run(
            [sys.executable, "-S", "-c", "import sys;print(sys.flags)"],
            check=True,
            capture_output=True,
        )
        self.assertIn(b"no_site=1", result.stdout)

    def test_E_option_sets_ignore_environment_flag(self):
        result = subprocess.run(
            [sys.executable, "-E", "-c", "import sys;print(sys.flags)"],
            check=True,
            capture_output=True,
        )
        self.assertIn(b"ignore_environment=1", result.stdout)

    def test_V_option_prints_version(self):
        result = subprocess.run(
            [sys.executable, "-V"], check=True, capture_output=True, encoding="utf-8"
        )
        version = sys.version_info
        self.assertIn(
            f"Python {version.major}.{version.minor}.{version.micro}", result.stdout
        )

    def test_W_option_adds_warnoptions(self):
        env = dict(os.environ)
        code = "import sys;print('warnoptions: ' + str(sys.warnoptions))"
        result = subprocess.run(
            [sys.executable, "-W", "foo", "-W", "ba,r", "-c", code],
            check=True,
            capture_output=True,
            env=env,
        )
        self.assertIn(b"warnoptions: ['foo', 'ba,r']", result.stdout)

    def test_c_option_runs_python_code(self):
        result = subprocess.run(
            [sys.executable, "-c", "print('test_c_op' + 'tion ok')"],
            check=True,
            capture_output=True,
        )
        self.assertIn(b"test_c_option ok", result.stdout)
        self.assertNotIn(b">>>", result.stderr)

    def test_t_option_noop(self):
        result = subprocess.run(
            [sys.executable, "-t", "-c", "0"], check=True, capture_output=True
        )
        self.assertIn(b"", result.stdout)

    def test_filename_option_executes_code(self):
        with TemporaryDirectory() as tempdir:
            tempfile = os.path.join(tempdir, "foo.py")
            tempfile = os.path.abspath(tempfile)
            with open(tempfile, "w") as fp:
                fp.write("print('test fi' + 'le executed')\n")
                fp.write("import sys\n")
                fp.write("print('argv: ' + str(sys.argv))\n")
            result = subprocess.run(
                [sys.executable, tempfile, "arg0", "arg1 with spaces"],
                check=True,
                capture_output=True,
                encoding="utf-8",
            )
            self.assertIn("test file executed", result.stdout)
            self.assertIn(
                f"argv: ['{tempfile}', 'arg0', 'arg1 with spaces']", result.stdout
            )

    def test_i_option_sets_inspect_interactive_flags(self):
        result = subprocess.run(
            [sys.executable, "-i", "-c", "import sys;print(sys.flags);sys.ps1='TTT:'"],
            check=True,
            capture_output=True,
            stdin=subprocess.DEVNULL,
        )
        self.assertIn(b"inspect=1", result.stdout)
        self.assertIn(b"interactive=1", result.stdout)
        self.assertIn(b"TTT:", result.stderr)

    def test_m_option_imports_module(self):
        result = subprocess.run(
            [sys.executable, "-m", "this"], check=True, capture_output=True
        )
        self.assertIn(b"The Zen of Python", result.stdout)
        self.assertNotIn(b">>>", result.stderr)

    def test_no_option_sets_default_flags(self):
        result = subprocess.run(
            [sys.executable, "-c", "import sys;print(sys.flags)"],
            check=True,
            capture_output=True,
        )
        self.assertIn(
            b"sys.flags(debug=0, inspect=0, interactive=0, optimize=0, dont_write_bytecode=0, no_user_site=0, no_site=0, ignore_environment=0, verbose=0, bytes_warning=0, quiet=0, hash_randomization=1, isolated=0, dev_mode=False, utf8_mode",
            result.stdout,
        )

    def test_s_option_sets_no_user_site_flag(self):
        result = subprocess.run(
            [sys.executable, "-s", "-c", "import sys;print(sys.flags)"],
            check=True,
            capture_output=True,
        )
        self.assertIn(b"no_user_site=1", result.stdout)

    def test_v_option_increments_verbose_flag(self):
        result = subprocess.run(
            [sys.executable, "-vvv", "-v", "-c", "import sys;print(sys.flags)"],
            check=True,
            capture_output=True,
        )
        self.assertIn(b"verbose=4", result.stdout)

    def test_version_option_prints_version(self):
        result = subprocess.run(
            [sys.executable, "--version"],
            check=True,
            capture_output=True,
            encoding="utf-8",
        )
        version = sys.version_info
        self.assertIn(
            f"Python {version.major}.{version.minor}.{version.micro}", result.stdout
        )

    def test_q_option_sets_quiet_flag(self):
        result = subprocess.run(
            [sys.executable, "-q", "-c", "import sys;print(sys.flags)"],
            check=True,
            capture_output=True,
        )
        self.assertIn(b"quiet=1", result.stdout)


if __name__ == "__main__":
    unittest.main()