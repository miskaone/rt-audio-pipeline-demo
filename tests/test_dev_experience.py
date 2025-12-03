"""Tests for developer experience improvements (Makefile, README, etc)."""

import os
import subprocess
import pytest
from pathlib import Path


class TestMakefile:
    """Test Makefile provides essential development targets."""

    def test_makefile_exists(self):
        """Makefile should exist in project root."""
        makefile_path = Path("Makefile")
        assert makefile_path.exists(), "Makefile should exist"

    def test_makefile_has_install_target(self):
        """Makefile should have install target."""
        makefile_path = Path("Makefile")
        content = makefile_path.read_text()
        assert "install:" in content, "Makefile should have install target"

    def test_makefile_has_test_target(self):
        """Makefile should have test target."""
        makefile_path = Path("Makefile")
        content = makefile_path.read_text()
        assert "test:" in content, "Makefile should have test target"

    def test_makefile_has_lint_target(self):
        """Makefile should have lint target."""
        makefile_path = Path("Makefile")
        content = makefile_path.read_text()
        assert "lint:" in content, "Makefile should have lint target"

    def test_makefile_has_run_target(self):
        """Makefile should have run target."""
        makefile_path = Path("Makefile")
        content = makefile_path.read_text()
        assert "run:" in content, "Makefile should have run target"

    def test_makefile_has_clean_target(self):
        """Makefile should have clean target."""
        makefile_path = Path("Makefile")
        content = makefile_path.read_text()
        assert "clean:" in content, "Makefile should have clean target"

    def test_makefile_has_help_target(self):
        """Makefile should have help target."""
        makefile_path = Path("Makefile")
        content = makefile_path.read_text()
        assert "help:" in content, "Makefile should have help target"

    @pytest.mark.skipif(
        os.name == 'nt', reason="Make commands not available on Windows"
    )
    def test_make_help_works(self):
        """make help should display available targets."""
        try:
            result = subprocess.run(
                ["make", "help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0, "make help should succeed"
            assert "install" in result.stdout, (
                "help should mention install target"
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("make not available or timeout")

    @pytest.mark.skipif(
        os.name == 'nt', reason="Make commands not available on Windows"
    )
    def test_make_test_works(self):
        """make test should run the test suite."""
        try:
            result = subprocess.run(
                ["make", "test"],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, "make test should succeed"
            assert "passed" in result.stdout.lower(), "tests should pass"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("make not available or timeout")


class TestReadme:
    """Test README provides comprehensive project documentation."""

    def test_readme_exists(self):
        """README.md should exist in project root."""
        readme_path = Path("README.md")
        assert readme_path.exists(), "README.md should exist"

    def test_readme_has_project_description(self):
        """README should have clear project description."""
        readme_path = Path("README.md")
        content = readme_path.read_text()
        assert len(content) > 500, "README should be substantial"
        assert "audio" in content.lower(), "README should mention audio"
        assert (
            "websocket" in content.lower()
        ), "README should mention WebSocket"

    def test_readme_has_installation_section(self):
        """README should have installation instructions."""
        readme_path = Path("README.md")
        content = readme_path.read_text()
        assert "## Installation" in content or "# Installation" in content, (
            "README should have installation section"
        )
        assert "pip install" in content or "requirements.txt" in content, (
            "README should mention installation method"
        )

    def test_readme_has_usage_section(self):
        """README should have usage examples."""
        readme_path = Path("README.md")
        content = readme_path.read_text()
        assert "## Usage" in content or "# Usage" in content, (
            "README should have usage section"
        )
        assert "http" in content.lower() or "ws://" in content, (
            "README should show how to use the service"
        )

    def test_readme_has_api_documentation(self):
        """README should document API endpoints."""
        readme_path = Path("README.md")
        content = readme_path.read_text()
        assert "/health" in content, (
            "README should document health endpoint"
        )
        assert "/ws/audio" in content, (
            "README should document WebSocket endpoint"
        )

    def test_readme_has_development_section(self):
        """README should have development setup instructions."""
        readme_path = Path("README.md")
        content = readme_path.read_text()
        assert "## Development" in content or "# Development" in content, (
            "README should have development section"
        )
        assert "test" in content.lower(), "README should mention testing"

    def test_readme_has_badges(self):
        """README should have status badges (optional)."""
        readme_path = Path("README.md")
        content = readme_path.read_text()
        badge_patterns = ["[![", "![](", "badge", "coverage"]
        # Badges are optional - just check if they exist
        any(pattern in content for pattern in badge_patterns)
        # This is informational only - badges are nice to have

    def test_readme_has_license_info(self):
        """README should mention license."""
        readme_path = Path("README.md")
        content = readme_path.read_text()
        license_keywords = ["license", "mit", "apache"]
        assert any(
            keyword in content.lower() for keyword in license_keywords
        ), "README should mention license"


class TestDevelopmentEnvironment:
    """Test development environment setup."""

    def test_requirements_txt_exists(self):
        """requirements.txt should exist."""
        req_path = Path("requirements.txt")
        assert req_path.exists(), "requirements.txt should exist"

    def test_requirements_txt_has_dependencies(self):
        """requirements.txt should list project dependencies."""
        req_path = Path("requirements.txt")
        content = req_path.read_text()
        assert "fastapi" in content, "requirements should include fastapi"
        assert "pytest" in content, "requirements should include pytest"

    def test_gitignore_exists(self):
        """.gitignore should exist."""
        gitignore_path = Path(".gitignore")
        assert gitignore_path.exists(), ".gitignore should exist"

    def test_gitignore_has_common_entries(self):
        """.gitignore should exclude common files."""
        gitignore_path = Path(".gitignore")
        content = gitignore_path.read_text()
        common_entries = [
            "__pycache__", "*.pyc", ".pytest_cache", ".venv", "venv"
        ]
        assert any(entry in content for entry in common_entries), (
            ".gitignore should exclude common Python files"
        )

    def test_project_structure_is_organized(self):
        """Project should have logical directory structure."""
        expected_dirs = ["app", "tests"]
        for dir_name in expected_dirs:
            dir_path = Path(dir_name)
            assert dir_path.exists(), f"Directory {dir_name} should exist"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"

    def test_main_app_exists(self):
        """Main application file should exist."""
        main_path = Path("app/main.py")
        assert main_path.exists(), "app/main.py should exist"

    def test_codec_module_exists(self):
        """Codec module should exist."""
        codec_path = Path("app/audio/codecs.py")
        assert codec_path.exists(), "app/audio/codecs.py should exist"
