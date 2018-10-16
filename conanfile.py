#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class WinflexbisonConan(ConanFile):
    name = "winflexbison"
    version = "2.5.15"
    description = "Flex and Bison for Windows"
    url = "https://github.com/bincrafters/conan-winflexbison"
    homepage = "https://github.com/lexxmark/winflexbison"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "GPLv3"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("winflexbison is only supported on Windows.")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256="a5ea5b98bb8d4054961f7bc82f458b4a9ef60c5e2dedcaba23a8e4363c2e6dfc")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        # Generate license from header of a source file
        with open("%s/%s/bison/data/glr.cc" % (self.source_folder, self._source_subfolder)) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(2, 16):
            license_content.append(content_lines[i][2:-1])
        tools.save("%s/%s/LICENSE" % (self.source_folder, self._source_subfolder), "\n".join(license_content))

        # https://github.com/lexxmark/winflexbison/issues/21
        # remove > 2.5.15
        tools.patch(base_path=self._source_subfolder, patch_file="0001-fix-include-paths-for-cmake.patch")

        tools.patch(base_path=self._source_subfolder, patch_file="0002-workaround-for-visual-studio-2013.patch")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        actual_build_path = "{}/bin/{}".format(self._source_subfolder, self.settings.build_type)
        self.copy(pattern="*.exe", dst="bin", src=actual_build_path, keep_path=False)
        self.copy(pattern="data/*", dst="bin", src=actual_build_path, keep_path=True)
        self.copy(pattern="*.h", dst="include", src=actual_build_path, keep_path=False)
