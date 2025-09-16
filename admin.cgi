#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� MONKEY BANMANA : admin.cgi - 23014/11/08
#�� copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �ݒ�t�@�C���F��
require "./init.cgi";
my %cf = set_init();

# �f�[�^��
my %in = parse_form();

# �F��
check_passwd();

# �Ǘ����[�h
admin_mode();

#-----------------------------------------------------------
#  �Ǘ����[�h
#-----------------------------------------------------------
sub admin_mode {
	# �폜
	if ($in{del}) {
		my %del;
		foreach ( split(/\0/,$in{del}) ) {
			$del{$_}++;
		}

		my @log;
		open(DAT,"+< $cf{logfile}") or error("open err: $cf{logfile}");
		eval "flock(DAT, 2);";
		while (<DAT>) {
			my ($no) = (split(/<>/))[0];

			if (!defined($del{$no})) { push(@log,$_); }
		}

		# �X�V
		seek(DAT, 0, 0);
		print DAT @log;
		truncate(DAT, tell(DAT));
		close(DAT);
	}

	# �Ǘ����
	header("�Ǘ����[�h");
	print <<"EOM";
<div align="right">
<form action="$cf{monkey_cgi}">
<input type="submit" value="�������">
<input type="button" value="���O�I�t" onclick=window.open("$cf{admin_cgi}","_top")>
</form>
</div>
<div class="ttl">�� �Ǘ����</div>
<ul>
<li>�폜����L���Ƀ`�F�b�N�����āu�폜����v�������Ă��������B
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="�폜����">
<dl class="list">
EOM

	# �L����W�J
	open(IN,"$cf{logfile}") or error("open err $cf{logfile}");
	while (<IN>) {
		my ($no,$date,$wd,$agent,$host) = split(/<>/);

		print qq|<dt><input type="checkbox" name="del" value="$no"> |;
		print qq|$date &nbsp; <b>$wd</b> - $agent</dt>\n|;
		print qq|<dd>HOST : $host</dd>\n|;
	}
	close(IN);

	print <<EOM;
</dl>
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  HTML�w�b�_�[
#-----------------------------------------------------------
sub header {
	my $ttl = shift;

	print <<EOM;
Content-type: text/html; charset=shift_jis

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<meta http-equiv="content-style-type" content="text/css">
<style type="text/css">
<!--
body,td,th { font-size:80%; background:#f0f0f0; }
div.ttl { border-bottom:1px solid #663300; color:#663300; padding:4px; font-weight:bold; }
p.err { color:#dd0000; }
dl.list dt { border-top:1px dotted #663300; padding:4px; margin-top:10px; }
dl.list b { color: green; }
-->
</style>
<title>$ttl</title>
</head>
<body>
EOM
}

#-----------------------------------------------------------
#  �p�X���[�h�F��
#-----------------------------------------------------------
sub check_passwd {
	# �p�X���[�h�������͂̏ꍇ�͓��̓t�H�[�����
	if ($in{pass} eq "") {
		&enter_form;

	# �p�X���[�h�F��
	} elsif ($in{pass} ne $cf{password}) {
		&error("�F�؂ł��܂���");
	}
}

#-----------------------------------------------------------
#  �������
#-----------------------------------------------------------
sub enter_form {
	&header("�������");
	print <<EOM;
<div align="center">
<form action="$cf{admin_cgi}" method="post">
<table width="380" style="margin-top:50px">
<tr>
	<td height="40" align="center">
		<fieldset><legend>�p�X���[�h����</legend><br>
		<input type="password" name="pass" value="" size="20">
		<input type="submit" value=" �F�� "><br><br>
		</fieldset>
	</td>
</tr>
</table>
</form>
<script language="javascript">
<!--
self.document.forms[0].pass.focus();
//-->
</script>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �G���[
#-----------------------------------------------------------
sub error {
	my $err = shift;

	&header("ERROR!");
	print <<EOM;
<div align="center">
<hr width="350">
<h3>ERROR!</h3>
<p class="err">$err</p>
<hr width="350">
<form>
<input type="button" value="�O��ʂɖ߂�" onclick="history.back()">
</form>
</div>
</body>
</html>
EOM
	exit;
}

