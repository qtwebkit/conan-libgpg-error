#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class GPGErrorConan(ConanFile):
    name = "libgpg-error"
    version = "1.24"
    url = "http://github.com/DEGoodmanWilson/conan-libgpg-error"
    description = "Libgpg-error is a small library that originally defined common error values for all GnuPG components."
    license = "https://www.gnupg.org/documentation/manuals/gnupg/Copying.html#Copying"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def source(self):
        source_url = "https://www.gnupg.org/ftp/gcrypt/libgpg-error"
        tools.get("{0}/libgpg-error-{1}.tar.bz2".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            # self.build_vs()
            self.output.fatal("No windows support yet. Sorry. Help a fellow out and contribute back?")

        with tools.chdir("sources"):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = True

            config_args = []
            for option_name in self.options.values.fields:
                if(option_name == "shared"):
                    if(getattr(self.options, "shared")):
                        config_args.append("--enable-shared")
                        config_args.append("--disable-static")
                    else:
                        config_args.append("--enable-static")
                        config_args.append("--disable-shared")
                else:
                    activated = getattr(self.options, option_name)
                    if activated:
                        self.output.info("Activated option! %s" % option_name)
                        config_args.append("--%s" % option_name)

            # This is a terrible hack to make cross-compiling on Travis work
            if (self.settings.arch=='x86' and self.settings.os=='Linux'):
                config_args.append("--build=$(build-aux/config.guess)")
                config_args.append("--host=i686-pc-linux-gnu")

            env_build.configure(args=config_args)
            env_build.make()

    def package(self):
        self.copy("*.h", "include", "sources/src", keep_path=True)
        # self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="sources", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="sources", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="sources", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="sources", keep_path=False)
        # binaries
        self.copy("gen-posix-lock-obj", dst="bin", src="sources/src", keep_path=False)
        self.copy("gpg-error", dst="bin", src="sources/src", keep_path=False)
        self.copy("gpg-error-config", dst="bin", src="sources/src", keep_path=False)
        self.copy("mkerrcodes", dst="bin", src="sources/src", keep_path=False)
        self.copy("mkheader", dst="bin", src="sources/src", keep_path=False)
        
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)


