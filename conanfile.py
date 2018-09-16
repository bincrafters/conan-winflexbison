#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class WinflexbisonConan(ConanFile):
    name = "winflexbison"
    version = "2.5.15"
    description = "Flex and Bison for Windows"
    url = "https://github.com/bincrafters/conan-winflexbison"
    homepage = "https://github.com/lexxmark/winflexbison"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "Several licenses"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "*.patch"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os != "Windows":
            raise Exception("winflexbison is only supported on Windows.")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256="a5ea5b98bb8d4054961f7bc82f458b4a9ef60c5e2dedcaba23a8e4363c2e6dfc")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

        # https://github.com/lexxmark/winflexbison/issues/21
        # remove > 2.5.15
        tools.patch(base_path=self.source_subfolder, patch_file="0001-fix-include-paths-for-cmake.patch")

        tools.patch(base_path=self.source_subfolder, patch_file="0002-workaround-for-visual-studio-2013.patch")

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)

        actual_build_path = "{}/bin/{}".format(self.source_subfolder, self.settings.build_type)
        self.copy(pattern="*.exe", dst="bin", src=actual_build_path, keep_path=False)
        self.copy(pattern="data/*", dst="bin", src=actual_build_path, keep_path=True)
        self.copy(pattern="*.h", dst="include", src=actual_build_path, keep_path=False)
