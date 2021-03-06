from conans import ConanFile, tools
from conans.tools import os_info
import os
import platform


class JavaInstallerConan(ConanFile):
    name = "java_installer"
    version = "9.0.0"
    url = "https://github.com/bincrafters/conan-java_installer"
    description = "Java installer distributed via Conan"
    license = "https://www.azul.com/products/zulu-and-zulu-enterprise/zulu-terms-of-use/"
    settings = "os", "arch"

    @property
    def jni_folder(self):
        folder = {"Linux": "linux", "Darwin": "darwin", "Windows": "win32"}.get(platform.system())
        return os.path.join("include", folder)

    def config_options(self):
        # Checking against self.settings.* would prevent cross-building profiles from working
        if tools.detected_architecture() != "x86_64":
            raise Exception("Unsupported Architecture.  This package currently only supports x86_64.")
        if platform.system() not in ["Windows", "Darwin", "Linux"]:
            raise Exception("Unsupported System. This package currently only support Linux/Darwin/Windows")

    def build(self):
        source_file = "zulu9.0.0.15-jdk{0}-{1}_x64"

        if os_info.is_windows:
            source_file = source_file.format(self.version, "win")
            ext = "zip"
            checksum = "f22d7ee4c277e0bf84ecb7cd03dfb13f"
        if os_info.is_linux:
            source_file = source_file.format(self.version, "linux")
            ext = "tar.gz"
            checksum = "de913f2aa03c341d865dfb6a1698f31b"
        if os_info.is_macos:
            source_file = source_file.format(self.version, "macosx")
            ext = "tar.gz"
            checksum = "b99e113f29fc0fad71b696d099e93366"

        bin_filename = "{0}.{1}".format(source_file, ext)
        download_url = "http://cdn.azul.com/zulu/bin/{0}".format(bin_filename)
        self.output.info("Downloading : {0}".format(download_url))
        tools.get(download_url, md5=checksum)
        os.rename(source_file, "sources")

    def package(self):
        self.copy(pattern="*", dst=".", src="sources")
        
    def package_info(self):
        self.cpp_info.includedirs.append(self.jni_folder)

        java_home = os.path.join(self.package_folder)
        bin_path = os.path.join(java_home, "bin")

        self.output.info("Creating JAVA_HOME environment variable with : {0}".format(java_home))
        self.env_info.JAVA_HOME = java_home
        
        self.output.info("Appending PATH environment variable with : {0}".format(bin_path))
        self.env_info.path.append(bin_path)
