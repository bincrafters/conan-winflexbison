#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class WinflexbisonConan(ConanFile):
    name = "winflexbison"
    version = "2.5.17"
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
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256="2ab4c895f9baf03dfdfbb2dc4abe60e87bf46efe12ed1218c38fd7761f0f58fc")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        # Generate license from header of a source file
        with open(os.path.join(self.source_folder, self._source_subfolder, "bison", "data", "skeletons", "glr.cc")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(2, 16):
            license_content.append(content_lines[i][2:-1])
        tools.save(os.path.join(self.source_folder, self._source_subfolder, "COPYING"), "\n".join(license_content))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self.build_folder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="data/*", dst="bin", src="{}/bison".format(self._source_subfolder), keep_path=True)
        actual_build_path = "{}/bin/{}".format(self._source_subfolder, self.settings.build_type)
        self.copy(pattern="*.exe", dst="bin", src=actual_build_path, keep_path=False)
        self.copy(pattern="*.h", dst="include", src=actual_build_path, keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
