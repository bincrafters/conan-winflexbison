# -*- coding: utf-8 -*-

from conans import ConanFile, CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def test(self):
        self.run("win_flex --version", run_environment=True)
        self.run("win_bison --version", run_environment=True)
        self.run("flex --version", run_environment=True)
        self.run("bison --version", run_environment=True)
