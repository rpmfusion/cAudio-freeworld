# This is the upstream-preferred name of the project
Name:           cAudio-freeworld
Version:        2.3.1
Release:        3%{?dist}
Summary:        MP3 support for cAudio

# cAudio-2.3.1/Plugins/mp3Decoder/mpaudec/{bits.c,mpaudec.c} are under LGPLv2+
# Everything else is zlib
License:        zlib and LGPLv2+

URL:            https://github.com/R4stl1n/cAudio/
Source0:        https://github.com/R4stl1n/cAudio/archive/%{version}/cAudio-%{version}.tar.gz

# Patch to version the .so names of the plugins.
# Was submitted upstream and merged (see https://github.com/R4stl1n/cAudio/pull/45)
Patch0:         https://patch-diff.githubusercontent.com/raw/R4stl1n/cAudio/pull/45.patch

# We need cmake and a compiler, obviously.
BuildRequires:  gcc-c++, cmake

BuildRequires:  libogg-devel, libvorbis-devel, openal-soft-devel

BuildRequires:  doxygen, graphviz

# Package must depend on cAudio.
Requires:       cAudio%{?_isa}

%description
cAudio is a 3D audio engine based on OpenAL. This package contains
the MP3 decoder plugin for cAudio, which is based on code from ffmpeg.

%package devel

Summary:       Development headers for cAudio-freeworld
Requires:      %{name}%{?_isa} = %{version}-%{release}

%description devel

Development files and library headers for cAudio-freeworld.

%prep
%autosetup -p1 -n cAudio-%{version}

# Remove bundled dependencies
rm -rf Dependencies*

# Set /lib manually because this software has interesting ideas about how to use cmake
sed 's,/lib,/%{_lib},g' -i CMakeLists.txt
sed 's,LIBRARY DESTINATION lib,LIBRARY DESTINATION %{_lib},g' -i CMake/InstallDependencies.cmake

# Fix some spurious executable perm errors.
chmod -x cAudio/Headers/cAudioStaticSource.h
chmod -x cAudio/Headers/cOpenALUtil.h

%build
mkdir build
cd build

export CXXFLAGS="%{optflags} -Wl,--as-needed"

# There is a MPEG decoder plugin that uses code derived from ffmpeg; this can't be built in Fedora.
# There are also C# bindings. They do not compile: https://github.com/R4stl1n/cAudio/issues/42
# The EAX legacy preset plugin  builds and works fine. However, the .so is not currently versioned.
%cmake .. -DCAUDIO_SYSTEM_OGG=TRUE -DCAUDIO_BUILD_MP3DECODER_PLUGIN=TRUE -DCAUDIO_BUILD_SAMPLES=FALSE
# -DCAUDIO_BUILD_EAX_PLUGIN=TRUE reenable when https://github.com/R4stl1n/cAudio/pull/45 merged

make %{?_smp_mflags}

# We don't need to build the documentation for the RPM Fusion version.

%install
cd build
make install DESTDIR=%{buildroot}

# Remove the installed libcAudio.so*; w
rm -rf %{buildroot}%{_libdir}/libcAudio.so*

# Remove the installed header files, too.
rm -rf %{buildroot}%{_includedir}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%{_libdir}/libcAp_mp3Decoder.so.2
%{_libdir}/libcAp_mp3Decoder.so.2.3.0
%license License.txt
%doc README.md

%files devel
%{_libdir}/libcAp_mp3Decoder.so

%changelog
* Sat Mar 18 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 2.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sat Sep 17 2016 Ben Rosser <rosser.bjr@gmail.com> 2.3.1-2
- Update license tag to zlib and LGPLv2+

* Tue Aug 16 2016 Ben Rosser <rosser.bjr@gmail.com> 2.3.1-1
- Initial package of cAudio-freeworld, containing only MP3 decoder.
- Based off of package and spec for cAudio in Fedora.
