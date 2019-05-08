#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class WinflexbisonConan(ConanFile):
    name = "winflexbison"
    version = "2.5.18"
    description = "Flex and Bison for Windows"
    topics = ("conan", "winflexbison", "flex", "bison")
    url = "https://github.com/bincrafters/conan-winflexbison"
    homepage = "https://github.com/lexxmark/winflexbison"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "GPLv3"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os_build", "arch_build", "build_type", "arch", "compiler"
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os_build != "Windows":
            raise ConanInvalidConfiguration("winflexbison is only supported on Windows.")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256="1db991bebaded832427539b6b28a8f36948e5ce3db5701b5104f85b66b8484de")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        # Generate license from header of a source file
        with open(os.path.join(self.source_folder, self._source_subfolder, "bison", "data", "skeletons", "glr.cc")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(2, 16):
            license_content.append(content_lines[i][2:-1])
        tools.save(os.path.join(self.source_folder, self._source_subfolder, "COPYING"), "\n".join(license_content))

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self.build_folder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="data/*", dst="bin", src="{}/bison".format(self._source_subfolder), keep_path=True)
        actual_build_path = "{}/bin/{}".format(self._source_subfolder, self.settings.build_type)
        self.copy(pattern="*.exe", dst="bin", src=actual_build_path, keep_path=False)
        self.copy(pattern="*.h", dst="include", src=actual_build_path, keep_path=False)

    def package_id(self):
        self.info.include_build_settings()
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
