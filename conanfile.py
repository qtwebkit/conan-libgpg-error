from conans import ConanFile
import os, shutil
from conans.tools import download, unzip, replace_in_file, check_md5
from conans import CMake

class GPGErrorConan(ConanFile):
    name = "libgpg-error"
    version = "1.24"
    url = "http://github.com/DEGoodmanWilson/conan-libgpg-error"
    ZIP_FOLDER_NAME = "libgpg-error-%s" % version
    generators = "cmake"
    settings =  "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def source(self):
        zip_name = "libgpg-error-%s.tar.bz2" % self.version
        download("https://www.gnupg.org/ftp/gcrypt/libgpg-error/%s" % zip_name, zip_name)
        check_md5(zip_name, "feb42198c0aaf3b28eabe8f41a34b983")
        unzip(zip_name)
        os.unlink(zip_name)

    def config(self):
        pass
        # del self.settings.compiler.libcxx

    def generic_env_configure_vars(self, verbose=False):
        """Reusable in any lib with configure!!"""
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            libs = 'LIBS="%s"' % " ".join(["-l%s" % lib for lib in self.deps_cpp_info.libs])
            ldflags = 'LDFLAGS="%s"' % " ".join(["-L%s" % lib for lib in self.deps_cpp_info.lib_paths])
            archflag = "-m32" if self.settings.arch == "x86" else ""
            cflags = 'CFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cflags))
            cpp_flags = 'CPPFLAGS="%s %s"' % (archflag, " ".join(self.deps_cpp_info.cppflags))
            command = "env %s %s %s %s" % (libs, ldflags, cflags, cpp_flags)
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            cl_args = " ".join(['/I"%s"' % lib for lib in self.deps_cpp_info.include_paths])
            lib_paths= ";".join(['"%s"' % lib for lib in self.deps_cpp_info.lib_paths])
            command = "SET LIB=%s;%%LIB%% && SET CL=%s" % (lib_paths, cl_args)
            if verbose:
                command += " && SET LINK=/VERBOSE"

        return command


       
    def build(self):
        config_options_string = ""

        for option_name in self.options.values.fields:
            activated = getattr(self.options, option_name)
            if activated:
                self.output.info("Activated option! %s" % option_name)
                config_options_string += " --%s" % option_name.replace("_", "-")

        configure_command = "cd %s && %s ./configure --prefix=%s --enable-static --enable-shared %s" % (self.ZIP_FOLDER_NAME, self.generic_env_configure_vars(), self.package_folder, config_options_string)
        self.output.warn(configure_command)
        self.run(configure_command)
        self.run("cd %s && make" % self.ZIP_FOLDER_NAME)
       

    def package(self):
        self.copy("*.h", "include", "%s/src" % (self.ZIP_FOLDER_NAME), keep_path=True)
        if self.options.shared:
            self.copy(pattern="*.so*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            self.copy(pattern="*.dll*", dst="bin", src=self.ZIP_FOLDER_NAME, keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", src="%s" % self.ZIP_FOLDER_NAME, keep_path=False)

        self.copy(pattern="*.lib", dst="lib", src="%s" % self.ZIP_FOLDER_NAME, keep_path=False)

        #binaries
        self.copy("gen-posix-lock-obj", dst="bin", src="%s/src" % self.ZIP_FOLDER_NAME, keep_path=False)
        self.copy("gpg-error", dst="bin", src="%s/src" % self.ZIP_FOLDER_NAME, keep_path=False)
        self.copy("gpg-error-config", dst="bin", src="%s/src" % self.ZIP_FOLDER_NAME, keep_path=False)
        self.copy("mkerrcodes", dst="bin", src="%s/src" % self.ZIP_FOLDER_NAME, keep_path=False)
        self.copy("mkheader", dst="bin", src="%s/src" % self.ZIP_FOLDER_NAME, keep_path=False)
        
    def package_info(self):
        self.cpp_info.libs = ['gpg-error']


