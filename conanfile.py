# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import shutil
import tempfile


class WinflexbisonConan(ConanFile):
    name = "winflexbison_installer"
    version = "2.5.17"
    description = "Flex and Bison for Windows"
    url = "https://github.com/bincrafters/conan-winflexbison"
    homepage = "https://github.com/lexxmark/winflexbison"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "GPLv3"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "arch", "os_build", "arch_build", "compiler", "build_type"

    _source_subfolder = "sources"

    def configure(self):
        self.settings.arch = str(self.settings.arch_build)
        if self.settings.compiler != "Visual Studio":
            raise ConanInvalidConfiguration("winflexbison is only supported for Visual Studio.")

    def package_id(self):
        self.info.include_build_settings()
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

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

    @property
    def _fake_package(self):
        return os.path.join(self.build_folder, "package")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self._fake_package
        cmake.configure()
        cmake.build(args=["--config", str(self.settings.build_type)])

    def package(self):
        cmake = CMake(self)
        with tools.chdir(self.build_folder):
            try:
                os.mkdir(self._fake_package)
            except IOError:
                pass
            cmake.install(args=["--config", str(self.settings.build_type)])

        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)

        self.copy(pattern="*.exe", src=self._fake_package, dst="bin",keep_path=False)
        self.copy(pattern="*.h", src=self._fake_package, dst="include", keep_path=True)
        self.copy(pattern="data/*", src=self._fake_package, dst="bin", keep_path=True)
        shutil.copy(os.path.join(self.package_folder, "bin", "win_flex.exe"), os.path.join(self.package_folder, "bin", "flex.exe"))
        shutil.copy(os.path.join(self.package_folder, "bin", "win_bison.exe"), os.path.join(self.package_folder, "bin", "bison.exe"))

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
