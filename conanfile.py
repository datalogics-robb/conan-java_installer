#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import platform
from conans import ConanFile, tools


class JavaInstallerConan(ConanFile):
    name = 'java_installer'
    url = 'https://github.com/bincrafters/conan-java_installer'
    description = 'Java installer distributed via Conan'
    license = 'https://www.azul.com/products/zulu-and-zulu-enterprise/zulu-terms-of-use/'
    settings = 'os', 'arch'

    @property
    def jni_folder(self):
        folder = {'Linux': 'linux', 'Darwin': 'darwin',
                  'Windows': 'win32'}.get(platform.system())
        return os.path.join('include', folder)

    @property
    def binarch(self):
        binarch = 'Mac'
        if self.settings.os != 'Macos':
            binarch = "%s_%s" % (self.settings.os, 'x64' if self.settings.arch == 'x86_64' else 'i686')
        return binarch

    def config_options(self):
        # Checking against self.settings.* would prevent cross-building profiles from working
        if self.settings.arch not in ['x86_64', 'x86']:
            raise Exception(
                'Unsupported Architecture.  This package currently only supports x86_64 and x86.')
        if self.settings.os not in ['Windows', 'Macos', 'Linux']:
            raise Exception(
                'Unsupported System. This package currently only support Linux/Darwin/Windows')
        if self.settings.os == 'Macos' and self.settings.arch == 'x86':
            raise Exception('Unsupported System (32-bit Mac OS X)')

    def build(self):
        download_url = self.conan_data.get("binaries", {}).get(self.version, {}).get(self.binarch, {}).get('url')
        checksum = self.conan_data.get("binaries", {}).get(self.version, {}).get(self.binarch, {}).get('sha256')
        self.output.info('Downloading : {0}'.format(download_url))
        tools.get(download_url, sha256=checksum)

    def package(self):
        self.copy(pattern='*', dst='.', src='.')

    def package_info(self):
        download_url = self.conan_data.get("binaries", {}).get(self.version, {}).get(self.binarch, {}).get('url')
        dl_file = download_url.split('/')[-1]
        if self.settings.os == 'Windows':
            jdk_base =  dl_file[:dl_file.find('.zip')]            
        else:
            jdk_base = dl_file[:dl_file.find('.tar.gz')]
        if self.settings.os == 'Macos': 
            jdk_base = os.path.join(jdk_base, 'zulu-8.jdk', 'Contents', 'Home')
        self.cpp_info.includedirs = [
            os.path.join(jdk_base, 'include'),
            os.path.join(jdk_base, self.jni_folder)]
        
        java_home = os.path.join(self.package_folder, jdk_base)
        bin_path = os.path.join(java_home, 'bin')
        self.cpp_info.bindirs = [os.path.join(jdk_base, 'bin')]
        self.output.info(
            'Creating JAVA_HOME environment variable with : {0}'.format(java_home))
        self.env_info.JAVA_HOME = java_home

        self.output.info(
            'Appending PATH environment variable with : {0}'.format(bin_path))
        self.env_info.PATH.append(bin_path)
