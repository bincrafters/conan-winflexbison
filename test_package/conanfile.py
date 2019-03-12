# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, RunEnvironment


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run("win_flex --version", run_environment=True)
        self.run("win_bison --version", run_environment=True)
        self.run("flex --version", run_environment=True)
        self.run("bison --version", run_environment=True)

        if not tools.cross_building(self.settings):
            with tools.environment_append(RunEnvironment(self).vars):
                cmake = CMake(self)
                cmake.test()
