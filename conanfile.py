#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import shutil


class GPGErrorConan(ConanFile):
    name = "libgpg-error"
    version = "1.36"
    homepage = "https://gnupg.org/software/libgpg-error/index.html"
    url = "http://github.com/DEGoodmanWilson/conan-libgpg-error"
    author = "Bincrafters <bincrafters@gmail.com>"
    topics = ("conan", "gpg", "gnupg")
    description = "Libgpg-error is a small library that originally defined common error values for all GnuPG " \
                  "components."
    license = "GPL-2.0-or-later"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "sources"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def build_requirements(self):
        if tools.os_info.is_windows:
            if "CONAN_BASH_PATH" not in os.environ:
                self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")
        if self._is_msvc:
            self.build_requires("automake_build_aux/1.16.1@bincrafters/stable")

    def configure(self):
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        source_url = "https://www.gnupg.org/ftp/gcrypt/libgpg-error"
        tools.get("{0}/libgpg-error-{1}.tar.bz2".format(source_url, self.version),
                  sha256="babd98437208c163175c29453f8681094bcaf92968a15cafb1a276076b33c97c")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        # the previous step might hang when converting from ISO-8859-2 to UTF-8 late in the build process
        os.unlink(os.path.join(self._source_subfolder, "po", "ro.po"))
        build = None
        host = None
        rc = None
        args = ["--disable-dependency-tracking",
                "--disable-nls",
                "--disable-languages",
                "--disable-doc",
                "--disable-tests"]
        if self.settings.os != "Windows" and self.options.pic:
            args.append("--with-pic")
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])

        if self._is_msvc:
            # INSTALL.windows: Native binaries, built using the MS Visual C/C++ tool chain.
            for filename in ["compile", "ar-lib"]:
                shutil.copy(os.path.join(self.deps_cpp_info["automake_build_aux"].rootpath, filename),
                            os.path.join(self._source_subfolder, "build-aux", filename))
            build = False
            if self.settings.arch == "x86":
                host = "i686-w64-mingw32"
                rc = "windres --target=pe-i386"
            elif self.settings.arch == "x86_64":
                host = "x86_64-w64-mingw32"
                rc = "windres --target=pe-x86-64"
            args.extend(["CC=$PWD/build-aux/compile cl -nologo",
                         "LD=link",
                         "NM=dumpbin -symbols",
                         "STRIP=:",
                         "AR=$PWD/build-aux/ar-lib lib",
                         "RANLIB=:"])
            if rc:
                args.extend(['RC=%s' % rc, 'WINDRES=%s' % rc])

        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings) if self._is_msvc else tools.no_op():
                env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                env_build.configure(args=args, build=build, host=host)
                env_build.make()
                env_build.install()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        la = os.path.join(self.package_folder, "lib", "libgpg-error.la")
        if os.path.isfile(la):
            os.unlink(la)

    def package_info(self):
        self.cpp_info.libs = ["gpg-error"]
