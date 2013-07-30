%define platform openmooc
%define component ffmpeg

Name:           %{platform}-%{component}
Version:        20120806
Release:        1%{?dist}
Summary:        FFmpeg is a complete, cross-platform solution to record, convert and stream audio and video
License:        LGPL or GPL
URL:            http://www.%{platform}-%{component}.org/
Source0:        %{name}-linux64-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      x86_64


%description
FFmpeg is a free software project that produces libraries and programs for
handling multimedia data. FFmpeg includes libavcodec, an audio/video codec
library used by several other projects, libavformat, an audio/video container
mux and demux library, and the ffmpeg command line program for transcoding
multimedia files.


%prep
%setup -q -c


%build


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%_libexecdir/%{platform}
cp %{name}-linux64-%{version}/%{component} %{buildroot}%_libexecdir/%{platform}
cp %{name}-linux64-%{version}/ffprobe %{buildroot}%_libexecdir/%{platform}
cp %{name}-linux64-%{version}/qt-faststart %{buildroot}%_libexecdir/%{platform}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%_libexecdir/%{component}
%_libexecdir/ffprobe
%_libexecdir/qt-faststart


%changelog
* Tue Jul 30 2013 Oscar Carballal Prego <ocarballal@yaco.es> - 0.3.3-1
- Rename the package to openmooc-ffmpeg so it doesn't have conflicts with
  the system ffmpeg

* Fri Jul 05 2013 Alejandro Blanco <ablanco@yaco.es> - 0.3.3-1
- Initial package
