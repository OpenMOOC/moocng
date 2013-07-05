%global srcname ffmpeg

Name:           %{srcname}
Version:        20120806
Release:        1%{?dist}
Summary:        FFmpeg is a complete, cross-platform solution to record, convert and stream audio and video

License:        LGPL or GPL
URL:            http://www.%{srcname}.org/
Source0:        %{srcname}-linux64-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      ia64


%description
FFmpeg is a free software project that produces libraries and programs for
handling multimedia data. FFmpeg includes libavcodec, an audio/video codec
library used by several other projects, libavformat, an audio/video container
mux and demux library, and the ffmpeg command line program for transcoding
multimedia files.


%prep
%setup -q -n %{srcname}-%{version}


%build


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%_bindir
cp %{srcname}-linux64-%{version}/%{srcname} %{buildroot}%_bindir/
cp %{srcname}-linux64-%{version}/ffprobe %{buildroot}%_bindir/
cp %{srcname}-linux64-%{version}/qt-faststart %{buildroot}%_bindir/


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%_bindir/%{srcname}
%_bindir/ffprobe
%_bindir/qt-faststart


%changelog
* Fri Jul 05 2013 Alejandro Blanco <ablanco@yaco.es> - 0.3.3-1
- Initial package
