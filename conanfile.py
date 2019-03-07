# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import tempfile


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

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _source_subfolder = "sources"

    def configure(self):
        if self.settings.compiler != "Visual Studio":
            raise ConanInvalidConfiguration("winflexbison is only supported for Visual Studio.")

    def source(self):
        name = "winflexbison"
        url = "https://github.com/lexxmark/winflexbison/archive/v{}.tar.gz".format(self.version)
        sha256 = "2ab4c895f9baf03dfdfbb2dc4abe60e87bf46efe12ed1218c38fd7761f0f58fc"
        filename = "{}-{}.tar.gz".format(name, self.version)

        dlfilepath = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(dlfilepath) and not tools.get_env("WINFLEXBISON_FORCE_DOWNLOAD", False):
            self.output.info("Skipping download. Using cached {}".format(dlfilepath))
        else:
            self.output.info("Downloading {} from {}".format(name, url))
            tools.download(url, dlfilepath)
        tools.check_sha256(dlfilepath, sha256)
        tools.untargz(dlfilepath)

        extracted_dir = "{}-{}".format(name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

        # Generate license from header of a source file
        with open(os.path.join(self.source_folder, self._source_subfolder, "bison", "data", "skeletons", "glr.cc"), ) as f:
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
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="data/*", dst="bin", src="{}/bison".format(self._source_subfolder), keep_path=True)
        actual_build_path = "{}/bin/{}".format(self._source_subfolder, self.settings.build_type)
        self.copy(pattern="*.exe", dst="bin", src=actual_build_path, keep_path=False)
        self.copy(pattern="*.h", dst="include", src=actual_build_path, keep_path=False)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
