%if 0%{?openeuler}
%global _missing_build_ids_terminate_build 0
%global debug_package   %{nil}
%global dde_prefix dde
%else
%global dde_prefix deepin
%endif

Name:           startdde
Version:        6.0.15
Release:        1
Summary:        Starter of deepin desktop environment
# migrated to SPDX
License:        GPL-3.0-or-later
URL:            https://github.com/linuxdeepin/startdde
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz
#Patch0:         0001-Run-lspci-with-full-path-on-Fedora.patch

BuildRequires:  compiler(go-compiler)
BuildRequires:  golang(github.com/linuxdeepin/dde-api/dxinput)
BuildRequires:  golang-deepin-go-lib
BuildRequires:  golang(github.com/godbus/dbus)
BuildRequires:  golang-github-linuxdeepin-go-x11-client
BuildRequires:  golang(github.com/davecgh/go-spew/spew)
BuildRequires:  golang(golang.org/x/xerrors)
BuildRequires:  systemd-rpm-macros
BuildRequires:  make
BuildRequires:  golang
BuildRequires:  jq
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(gnome-keyring-1)
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(gudev-1.0)
BuildRequires:  pkgconfig(libsecret-1)

Provides:       x-session-manager
Requires:       %{dde_prefix}-daemon
Requires:       procps
Requires:       deepin-desktop-schemas
Requires:       %{dde_prefix}-kwin
# for lspci command
Requires:       pciutils
Recommends:     %{dde_prefix}-qt5integration

%description
%{summary}.

%prep
%autosetup -p1 -n %{name}-%{version}
## Scripts in /etc/X11/Xsession.d are not executed after xorg start
sed -i 's|X11/Xsession.d|X11/xinit/xinitrc.d|g' Makefile

sed -i 's|/etc/os-version|/etc/uos-version|' vm.go utils.go misc/Xsession.d/00deepin-dde-env

%build
make prepare
touch prepare
export GOPATH="$PWD/gopath:%{gopath}"
%gobuild -o startdde
# rebuild other executables with different build-ids
for cmd in fix-xauthority-perm greeter-display-daemon; do
    %gobuild -o $cmd github.com/linuxdeepin/startdde/cmd/$cmd
done
%make_build

%install
%make_install
%find_lang %{name}

%post
xsOptsFile=/etc/X11/Xsession.options
update-alternatives --install /usr/bin/x-session-manager x-session-manager \
    /usr/bin/startdde 90 || true
if [ -f $xsOptsFile ];then
	sed -i '/^use-ssh-agent/d' $xsOptsFile
	if ! grep '^no-use-ssh-agent' $xsOptsFile >/dev/null; then
		echo no-use-ssh-agent >> $xsOptsFile
	fi
fi

%files -f %{name}.lang
%doc README.md
%license LICENSE
%{_sysconfdir}/X11/xinit/xinitrc.d/00deepin-dde-env
%{_sysconfdir}/X11/xinit/xinitrc.d/01deepin-profile
%{_sysconfdir}/X11/xinit/xinitrc.d/94qt_env
%{_sysconfdir}/profile.d/deepin-xdg-dir.sh
%{_bindir}/%{name}
%{_sbindir}/deepin-fix-xauthority-perm
%{_datadir}/xsessions/deepin.desktop
%{_datadir}/lightdm/lightdm.conf.d/60-deepin.conf
%{_datadir}/%{name}/
%{_prefix}/lib/deepin-daemon/greeter-display-daemon
%{_datadir}/glib-2.0/schemas/*
%{_datadir}/dsg/
