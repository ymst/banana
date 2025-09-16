#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� MONKEY BANANA : check.cgi - 2014/11/07
#�� copyright (c) KentWeb, 1997-2014
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �O���t�@�C���捞��
require './init.cgi';
my %cf = set_init();

print <<EOM;
Content-type: text/html; charset=shift_jis

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<title>Check Mode</title>
</head>
<body>
<b>Check Mode: [ $cf{version} ]</b>
<ul>
EOM

# �f�[�^�t�@�C��
my %log = (logfile => '���O�t�@�C��', cntfile => '�J�E���g�t�@�C��');
foreach ( keys(%log) ) {
	if (-f $cf{$_}) {
		print "<li>$log{$_}�p�X : OK\n";
		if (-r $cf{$_} && -w $cf{$_}) {
			print "<li>$log{$_}�p�[�~�b�V���� : OK\n";
		} else {
			print "<li>$log{$_}�p�[�~�b�V���� : NG\n";
		}
	} else {
		print "<li>$log{$_}�p�X : NG\n";
	}
}

# �e���v���[�g
foreach (qw(monkey note kuji error word)) {
	if (-e "$cf{tmpldir}/$_.html") {
		print "<li>�e���v���[�g( $_.html ) : OK\n";
	} else {
		print "<li>�e���v���[�g( $_.html ) : NG\n";
	}
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;

